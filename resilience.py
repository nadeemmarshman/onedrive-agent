"""
Phase 4.5: Resilience & Alerting.

Two capabilities, deliberately kept in a separate module from
agent_loop.py so each phase's code stays focused:

1. EMAIL ALERTING (via SendGrid)
   Sends an alert email to a configurable recipient list when an
   ERROR-level event occurs during the agent loop. Uses the same
   SENDGRID_API_KEY environment variable pattern as ANTHROPIC_API_KEY.
   Never called for routine INFO-level events -- only genuine failures.

2. STATE MACHINE + RESTART-AND-RESUME
   The agent is always in exactly one of five named states:
     SCANNING → AWAITING_DECISION → EXECUTING_TOOL →
     AWAITING_HUMAN_APPROVAL → DONE
   Current state is persisted to a JSON file (agent_state.json) at
   each meaningful transition, so the process can resume correctly
   after an abrupt stop (e.g. load shedding / power loss).

   Safety-critical guarantee: AWAITING_HUMAN_APPROVAL is a state the
   restart logic must NEVER silently skip past. If power cuts out
   after Claude proposes a deletion but before the human approves it,
   resuming must land back in "still waiting for approval" -- never
   auto-resume into "proceed with the action."

   This is not ad hoc retry logic -- it is a deliberate state machine,
   designed and documented as such, because restart-and-resume
   correctness depends on named, inspectable states, not on an
   arbitrary dump of in-progress variables.

SCOPE NOTE (what this module does NOT do):
   "Restart-and-resume" means this script checks for saved, unfinished
   state on startup and resumes from there. It does NOT mean the script
   can make itself run again after the whole machine reboots -- that
   requires an OS-level mechanism (e.g. Windows Task Scheduler). This
   distinction is intentional and documented honestly in the README.
"""

import json
import logging
import os
from enum import Enum
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger("agent_loop")

# ---------------------------------------------------------------------------
# PART 1: STATE MACHINE
# ---------------------------------------------------------------------------

class AgentState(Enum):
    """
    The five named states the agent can be in at any point.

    Using an Enum (not plain strings) means:
      - States are a closed, finite, inspectable set -- you can't
        accidentally introduce a typo-state like "AWAITING_DECISOIN"
      - Each state transition can be unit-tested explicitly
      - The state can be serialised to JSON (via .value) and
        deserialised (via AgentState(value)) without ambiguity
    """
    SCANNING              = "SCANNING"
    AWAITING_DECISION     = "AWAITING_DECISION"
    EXECUTING_TOOL        = "EXECUTING_TOOL"
    AWAITING_HUMAN_APPROVAL = "AWAITING_HUMAN_APPROVAL"
    DONE                  = "DONE"


# Valid transitions: maps each state to the set of states it is
# allowed to move into. This makes the allowed transitions explicit
# and checkable (e.g. in unit tests) rather than implicit in code flow.
VALID_TRANSITIONS = {
    AgentState.SCANNING:               {AgentState.AWAITING_DECISION},
    AgentState.AWAITING_DECISION:      {AgentState.EXECUTING_TOOL,
                                        AgentState.AWAITING_HUMAN_APPROVAL,
                                        AgentState.DONE},
    AgentState.EXECUTING_TOOL:         {AgentState.AWAITING_DECISION},
    AgentState.AWAITING_HUMAN_APPROVAL:{AgentState.AWAITING_DECISION,
                                        AgentState.DONE},
    AgentState.DONE:                   set(),  # terminal state
}

STATE_FILE = Path("agent_state.json")


def _load_state() -> dict | None:
    """
    Load persisted state from disk. Returns None if no state file
    exists (i.e. this is a fresh run, not a resume).
    """
    if not STATE_FILE.exists():
        return None
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to load state file {STATE_FILE}: {e}")
        return None


def _save_state(state: AgentState, data: dict) -> None:
    """
    Persist the current state and any supporting data to disk.
    Called at every meaningful state transition so a restart can
    resume from the exact point of interruption.
    """
    payload = {
        "state": state.value,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)
        logger.info(f"State saved: {state.value}")
    except OSError as e:
        logger.error(f"Failed to save state to {STATE_FILE}: {e}")


def _clear_state() -> None:
    """Remove the state file once the agent has reached DONE."""
    if STATE_FILE.exists():
        STATE_FILE.unlink()
        logger.info("State file cleared (run complete)")


def transition_to(current: AgentState, next_state: AgentState, data: dict) -> AgentState:
    """
    Move the agent from current to next_state, validating the
    transition is allowed and persisting the new state to disk.

    Raises ValueError if the transition is not in VALID_TRANSITIONS --
    this makes invalid state changes an explicit, loud failure rather
    than a silent data corruption.
    """
    if next_state not in VALID_TRANSITIONS[current]:
        raise ValueError(
            f"Invalid state transition: {current.value} → {next_state.value}. "
            f"Allowed from {current.value}: "
            f"{[s.value for s in VALID_TRANSITIONS[current]]}"
        )
    _save_state(next_state, data)
    logger.info(f"State transition: {current.value} → {next_state.value}")
    return next_state


def check_for_resume() -> tuple[AgentState | None, dict]:
    """
    Check whether there is saved, unfinished state from a previous run.

    Returns (None, {}) if this is a fresh run.
    Returns (state, data) if there is state to resume from.

    SAFETY-CRITICAL: if the saved state is AWAITING_HUMAN_APPROVAL,
    this function logs a prominent warning and returns that state
    directly -- the caller MUST handle this case explicitly and MUST
    NOT auto-skip past it. This is enforced by the state machine's
    transition rules (AWAITING_HUMAN_APPROVAL can only move to
    AWAITING_DECISION or DONE, never silently back to EXECUTING_TOOL).
    """
    saved = _load_state()
    if saved is None:
        logger.info("No saved state found — starting fresh")
        return None, {}

    try:
        state = AgentState(saved["state"])
    except ValueError:
        logger.error(
            f"Saved state '{saved['state']}' is not a recognised state. "
            f"Ignoring saved state and starting fresh."
        )
        return None, {}

    # The safety-critical check: never silently resume past this state.
    if state == AgentState.AWAITING_HUMAN_APPROVAL:
        logger.warning(
            "=" * 60 + "\n"
            "RESUMED INTO AWAITING_HUMAN_APPROVAL\n"
            "A previous run stopped while waiting for human approval.\n"
            "Proposed actions have NOT been executed.\n"
            "Human approval is required before proceeding.\n"
            "=" * 60
        )

    logger.info(f"Resuming from saved state: {state.value} "
                f"(saved at {saved.get('timestamp', 'unknown')})")
    return state, saved.get("data", {})


# ---------------------------------------------------------------------------
# PART 2: EMAIL ALERTING (via SendGrid)
# ---------------------------------------------------------------------------

# Configurable recipient list -- not hardcoded, so it can be changed
# without touching the code. In a production system this would come
# from a config file or environment variable; for this portfolio project
# a module-level constant is proportionate.
ALERT_RECIPIENTS = [
    "nadeemmarshman@gmail.com",
    "narshman@duck.com",
]

ALERT_FROM = "nadeemmarshman@gmail.com"  # must match SendGrid Single Sender Verification
ALERT_FROM_NAME = "OneDrive Agent"


def send_alert(subject: str, body: str) -> None:
    """
    Send an email alert via SendGrid to the ALERT_RECIPIENTS list.

    Called only on ERROR-level events -- not on routine INFO messages.
    Reads SENDGRID_API_KEY from the environment variable (never
    hardcoded), using the same pattern as ANTHROPIC_API_KEY.

    Fails gracefully if SendGrid is unavailable or the key is missing:
    logs the failure at ERROR level but does not raise, so a secondary
    alerting failure doesn't crash the already-failing agent loop.
    """
    api_key = os.environ.get("SENDGRID_API_KEY")
    if not api_key:
        logger.error(
            "SENDGRID_API_KEY environment variable not set. "
            "Cannot send alert email. Open a new terminal after setting it."
        )
        return

    try:
        import urllib.request
        import urllib.error

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        full_body = (
            f"OneDrive Agent Alert\n"
            f"{'=' * 40}\n"
            f"Time: {timestamp}\n\n"
            f"{body}\n\n"
            f"{'=' * 40}\n"
            f"This alert was sent automatically by the OneDrive Agent.\n"
            f"Check the run log in the logs/ folder for full detail."
        )

        payload = {
            "personalizations": [
                {
                    "to": [{"email": r} for r in ALERT_RECIPIENTS],
                    "subject": f"[OneDrive Agent] {subject}",
                }
            ],
            "from": {"email": ALERT_FROM, "name": ALERT_FROM_NAME},
            "content": [{"type": "text/plain", "value": full_body}],
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            "https://api.sendgrid.com/v3/mail/send",
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.status
            if status == 202:
                logger.info(
                    f"Alert email sent (202 Accepted) → "
                    f"{', '.join(ALERT_RECIPIENTS)}"
                )
            else:
                logger.error(f"Alert email returned unexpected status: {status}")

    except urllib.error.HTTPError as e:
        logger.error(f"SendGrid HTTP error {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        logger.error(f"Could not reach SendGrid: {e.reason}")
    except Exception as e:
        logger.error(f"Unexpected error sending alert: {type(e).__name__}: {e}")


def alert_on_error(subject: str, body: str) -> None:
    """
    Convenience wrapper: log at ERROR level AND send an alert email.
    This is the single call point for any serious failure in the loop --
    ensures the log file and the email recipient list both get notified
    without the caller having to call both separately.
    """
    logger.error(f"ALERT: {subject} | {body}")
    send_alert(subject, body)
