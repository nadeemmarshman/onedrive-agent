"""
Phase 4.5: Resilience & Alerting.

Two capabilities, deliberately kept in a separate module from
agent_loop.py so each phase's code stays focused:

1. EMAIL ALERTING (via SendGrid)
   Sends an alert email to a configurable recipient list when an
   ERROR-level event occurs during the agent loop. Uses the same
   SENDGRID_API_KEY environment variable pattern as ANTHROPIC_API_KEY.
   Never called for routine INFO-level events -- only genuine failures.

   Each error category has its own named alert function structured
   around a 5W incident-management framework (What, When, Where,
   Triggered by, Why) -- the same pattern used in IT operations
   runbooks. Every message includes the exact command to run plus
   a README.md pointer for the correct folder path on this machine,
   so a recipient at 2am after load shedding has everything needed
   to diagnose and resolve without relying on memory.

2. STATE MACHINE + RESTART-AND-RESUME
   The agent is always in exactly one of five named states:
     SCANNING -> AWAITING_DECISION -> EXECUTING_TOOL ->
     AWAITING_HUMAN_APPROVAL -> DONE
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

# README reference note -- included in every alert message wherever
# a command or file path is mentioned. Single constant so the wording
# is consistent across all messages and only needs to change in one place.
_README_NOTE = (
    "(Check README.md in the project repo for the correct\n"
    " folder path to run this from on your machine)"
)


def _now_utc() -> str:
    """Return the current UTC time as a readable string for alert messages."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _masked_user_id() -> str:
    """
    Returns a partially masked user identifier (username@hostname)
    for inclusion in alert messages.

    Masking rule: show first 2 characters, replace the rest with ****
    This mirrors the industry-standard partial-masking pattern (same as
    credit card display: **** **** **** 4242) -- enough to identify
    which user/machine is relevant for diagnosis, not enough to expose
    full credentials that could be used in a brute-force or lateral
    movement attack if the alert email is intercepted or forwarded.

    Security note: even partial identifiers carry risk. Alert emails
    should be delivered to a secured inbox. This is logged as a known,
    accepted risk in RAID_LOG.md (see Risk R5).
    """
    def _mask(value: str) -> str:
        return (value[:2] + "****") if len(value) > 2 else "****"

    username = os.environ.get("USERNAME", "unknown")
    hostname = os.environ.get("COMPUTERNAME", "unknown")
    return f"{_mask(username)}@{_mask(hostname)}"


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
    SCANNING                = "SCANNING"
    AWAITING_DECISION       = "AWAITING_DECISION"
    EXECUTING_TOOL          = "EXECUTING_TOOL"
    AWAITING_HUMAN_APPROVAL = "AWAITING_HUMAN_APPROVAL"
    DONE                    = "DONE"


# Valid transitions: maps each state to the set of states it is
# allowed to move into. This makes the allowed transitions explicit
# and checkable (e.g. in unit tests) rather than implicit in code flow.
VALID_TRANSITIONS = {
    AgentState.SCANNING:                {AgentState.AWAITING_DECISION},
    AgentState.AWAITING_DECISION:       {AgentState.EXECUTING_TOOL,
                                         AgentState.AWAITING_HUMAN_APPROVAL,
                                         AgentState.DONE},
    AgentState.EXECUTING_TOOL:          {AgentState.AWAITING_DECISION},
    AgentState.AWAITING_HUMAN_APPROVAL: {AgentState.AWAITING_DECISION,
                                         AgentState.DONE},
    AgentState.DONE:                    set(),  # terminal state
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
            f"Invalid state transition: {current.value} -> {next_state.value}. "
            f"Allowed from {current.value}: "
            f"{[s.value for s in VALID_TRANSITIONS[current]]}"
        )
    _save_state(next_state, data)
    logger.info(f"State transition: {current.value} -> {next_state.value}")
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
        logger.info("No saved state found -- starting fresh")
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
            "RESUMED INTO AWAITING_HUMAN_APPROVAL -- "
            "a previous run stopped while waiting for human approval. "
            "Proposed actions have NOT been executed. "
            "Human approval is required before proceeding."
        )

    logger.info(
        f"Resuming from saved state: {state.value} "
        f"(saved at {saved.get('timestamp', 'unknown')})"
    )
    return state, saved.get("data", {})


# ---------------------------------------------------------------------------
# PART 2: EMAIL ALERTING (via SendGrid)
# ---------------------------------------------------------------------------

ALERT_RECIPIENTS = [
    "nadeemmarshman@gmail.com",
    "narshman@duck.com",
]

ALERT_FROM      = "nadeemmarshman@gmail.com"
ALERT_FROM_NAME = "OneDrive Agent"


def send_alert(subject: str, body: str) -> None:
    """
    Send an email alert via SendGrid to the ALERT_RECIPIENTS list.

    Called only on ERROR-level events -- not on routine INFO messages.
    Reads SENDGRID_API_KEY from the environment variable (never
    hardcoded), using the same pattern as ANTHROPIC_API_KEY.

    Fails gracefully if SendGrid is unavailable or the key is missing:
    logs the failure at ERROR level but does not raise, so a secondary
    alerting failure does not crash the already-failing agent loop.
    """
    api_key = os.environ.get("SENDGRID_API_KEY")
    if not api_key:
        logger.error(
            "SENDGRID_API_KEY environment variable not set. "
            "Cannot send alert email. "
            "Run: echo $env:SENDGRID_API_KEY "
            f"{_README_NOTE}"
        )
        return

    try:
        import urllib.request
        import urllib.error

        timestamp = _now_utc()
        full_body = (
            f"OneDrive Agent Alert\n"
            f"{'=' * 50}\n"
            f"Time: {timestamp}\n\n"
            f"{body}\n\n"
            f"{'=' * 50}\n"
            f"This alert was sent automatically by the OneDrive Agent.\n"
            f"Run: python agent_loop.py to re-run the agent.\n"
            f"{_README_NOTE}"
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
                    f"Alert email sent (202 Accepted) -> "
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


# ---------------------------------------------------------------------------
# PART 3: NAMED ALERT FUNCTIONS (one per error category)
#
# Each function is structured around a 5W incident-management framework:
#   WHAT  -- what broke and what to do
#   WHEN  -- when it failed and when it must be fixed (graduated urgency)
#   WHERE -- which component failed and where to fix it
#   TRIGGERED BY -- what event or condition triggered this
#   WHY   -- root cause and impact if not resolved
#
# Every message includes the exact command to run plus a README.md
# pointer for the correct folder path, so the recipient has everything
# needed to act without relying on memory.
# ---------------------------------------------------------------------------

def alert_auth_failure() -> None:
    """Anthropic API authentication failure -- key rejected."""
    subject = "Authentication failed"
    body = (
        f"WHAT:  The agent failed to authenticate with the Anthropic API.\n"
        f"       The API key was rejected. The agent has stopped.\n\n"
        f"WHEN:  {_now_utc()}\n"
        f"       Fix before the next scheduled run -- the agent cannot\n"
        f"       proceed without a valid API key.\n\n"
        f"WHERE: Failed at: Anthropic API authentication layer.\n"
        f"       Fix at: Windows environment variables.\n"
        f"       {_README_NOTE}\n\n"
        f"TRIGGERED BY: Invalid or missing ANTHROPIC_API_KEY\n"
        f"       environment variable on machine: {_masked_user_id()}\n"
        f"       Fix by: the agent owner / system administrator.\n\n"
        f"WHY:   The API key may have been revoked, regenerated, or\n"
        f"       never set correctly. Until fixed, no API calls can be\n"
        f"       made and the agent cannot run at all.\n\n"
        f"STEPS:\n"
        f"1. Open a new PowerShell terminal.\n"
        f"2. Run: echo $env:ANTHROPIC_API_KEY\n"
        f"   {_README_NOTE}\n"
        f"3. If blank: re-run the setup steps in README.md to restore it.\n"
        f"4. If set but rejected: generate a new key at:\n"
        f"   console.anthropic.com/settings/keys\n"
        f"5. Run: python agent_loop.py\n"
        f"   {_README_NOTE}"
    )
    alert_on_error(subject, body)


def alert_rate_limit() -> None:
    """Anthropic API rate limit hit."""
    subject = "Rate limit hit"
    body = (
        f"WHAT:  The agent hit the Anthropic API rate limit.\n"
        f"       Too many requests were sent too quickly. The agent has stopped.\n\n"
        f"WHEN:  {_now_utc()}\n"
        f"       Fix within 60 seconds -- this is a temporary condition\n"
        f"       that resolves on its own.\n\n"
        f"WHERE: Failed at: Anthropic API rate-limiting layer.\n"
        f"       Fix at: wait, then re-run from the project folder.\n"
        f"       {_README_NOTE}\n\n"
        f"TRIGGERED BY: The agent sending requests faster than the\n"
        f"       API tier allows on machine: {_masked_user_id()}\n"
        f"       No action was taken on any files.\n"
        f"       Fix by: the agent owner -- simply wait and retry.\n\n"
        f"WHY:   The Anthropic free/low tier limits request frequency.\n"
        f"       If this recurs frequently, consider reviewing run\n"
        f"       frequency or upgrading the API tier.\n\n"
        f"STEPS:\n"
        f"1. Wait 60 seconds.\n"
        f"2. Run: python agent_loop.py\n"
        f"   {_README_NOTE}\n"
        f"3. If recurring, check usage at:\n"
        f"   console.anthropic.com/settings/usage"
    )
    alert_on_error(subject, body)


def alert_connection_failure() -> None:
    """Anthropic API connection failure -- network unreachable."""
    subject = "Network connection failed"
    body = (
        f"WHAT:  The agent could not reach the Anthropic API.\n"
        f"       A network connection failure occurred. The agent has stopped.\n\n"
        f"WHEN:  {_now_utc()}\n"
        f"       Fix when your connection is restored -- this is usually\n"
        f"       a temporary condition (load shedding / network drop).\n\n"
        f"WHERE: Failed at: outbound network connection to api.anthropic.com.\n"
        f"       Fix at: check your network, then re-run from the project folder.\n"
        f"       {_README_NOTE}\n\n"
        f"TRIGGERED BY: Network unavailability on machine: {_masked_user_id()}\n"
        f"       Not a code or configuration error.\n"
        f"       No action was taken on any files.\n"
        f"       Fix by: the agent owner once connectivity is restored.\n\n"
        f"WHY:   The API cannot be reached without an active internet\n"
        f"       connection. Common in South Africa during load shedding.\n"
        f"       The agent's state has been saved -- it will resume\n"
        f"       from where it left off when re-run.\n\n"
        f"STEPS:\n"
        f"1. Check your internet connection.\n"
        f"2. If on load shedding / mobile data, wait for the\n"
        f"   connection to stabilise before retrying.\n"
        f"3. Run: python agent_loop.py\n"
        f"   {_README_NOTE}\n"
        f"4. If the problem persists, check:\n"
        f"   https://status.anthropic.com"
    )
    alert_on_error(subject, body)


def alert_api_status_error(status_code: int, message: str) -> None:
    """Anthropic API returned an unexpected status code (e.g. insufficient credit)."""
    subject = f"API error (status {status_code})"
    body = (
        f"WHAT:  The Anthropic API returned an error (status {status_code}).\n"
        f"       Detail: {message}\n"
        f"       The agent has stopped.\n\n"
        f"WHEN:  {_now_utc()}\n"
        f"       Fix before the next scheduled run. If this is a billing\n"
        f"       issue, fix immediately to restore agent functionality.\n\n"
        f"WHERE: Failed at: Anthropic API (HTTP status {status_code}).\n"
        f"       Fix at: console.anthropic.com/settings/billing\n"
        f"       and/or the project folder run log.\n"
        f"       {_README_NOTE}\n\n"
        f"TRIGGERED BY: An API-reported error on machine: {_masked_user_id()}\n"
        f"       Most commonly an exhausted credit balance.\n"
        f"       No action was taken on any files.\n"
        f"       Fix by: the agent owner / billing administrator.\n\n"
        f"WHY:   A status {status_code} error typically means the account\n"
        f"       cannot currently process requests -- either due to\n"
        f"       insufficient credit or an API-side issue. Until resolved,\n"
        f"       the agent cannot make any decisions or take any actions.\n\n"
        f"STEPS:\n"
        f"1. Check your API credit balance at:\n"
        f"   console.anthropic.com/settings/billing\n"
        f"2. If balance is zero, top up, then:\n"
        f"   Run: python agent_loop.py\n"
        f"   {_README_NOTE}\n"
        f"3. If balance is fine, check the run log:\n"
        f"   Run: Get-ChildItem logs\\ | Sort-Object LastWriteTime | Select-Object -Last 1\n"
        f"   {_README_NOTE}"
    )
    alert_on_error(subject, body)


def alert_resume_approval_required(saved_at: str) -> None:
    """Agent resumed into AWAITING_HUMAN_APPROVAL -- approval still pending."""
    subject = "Resumed — approval still required"
    body = (
        f"WHAT:  The agent was interrupted while waiting for human approval.\n"
        f"       Proposed actions have NOT been executed.\n"
        f"       No files have been modified or deleted.\n\n"
        f"WHEN:  State was saved at: {saved_at}\n"
        f"       Fix at your earliest convenience -- no files are at risk\n"
        f"       until you actively approve actions.\n\n"
        f"WHERE: Failed at: agent state persistence (agent_state.json).\n"
        f"       Fix at: review agent_state.json, then re-run the agent.\n"
        f"       {_README_NOTE}\n\n"
        f"TRIGGERED BY: An abrupt interruption on machine: {_masked_user_id()}\n"
        f"       (e.g. load shedding, power loss) after Claude proposed\n"
        f"       actions but before the human approved them.\n"
        f"       Fix by: the agent owner -- review proposals and approve\n"
        f"       or reject each one.\n\n"
        f"WHY:   The agent requires explicit human approval before any\n"
        f"       destructive action (delete, convert). This is a safety\n"
        f"       guarantee -- no action will execute without your sign-off.\n"
        f"       Re-running will present the proposals again for review.\n\n"
        f"STEPS:\n"
        f"1. Review the pending proposals:\n"
        f"   Run: Get-Content agent_state.json\n"
        f"   {_README_NOTE}\n"
        f"2. Re-run the agent to action the approval:\n"
        f"   Run: python agent_loop.py\n"
        f"   {_README_NOTE}\n"
        f"   The agent will present proposals for your approval\n"
        f"   before taking any action."
    )
    alert_on_error(subject, body)


def alert_corrupted_state_file(error_detail: str) -> None:
    """agent_state.json is unreadable or corrupted."""
    subject = "State file unreadable"
    body = (
        f"WHAT:  The file agent_state.json could not be read.\n"
        f"       It may be corrupted. The agent has stopped.\n"
        f"       Detail: {error_detail}\n\n"
        f"WHEN:  {_now_utc()}\n"
        f"       Fix before the next scheduled run. The agent cannot\n"
        f"       resume safely until the state file is resolved.\n\n"
        f"WHERE: Failed at: agent_state.json in the project folder.\n"
        f"       Fix at: locate and delete agent_state.json, then re-run.\n"
        f"       {_README_NOTE}\n\n"
        f"TRIGGERED BY: A likely interrupted write to agent_state.json\n"
        f"       on machine: {_masked_user_id()}\n"
        f"       (e.g. power loss during a state save).\n"
        f"       Fix by: the agent owner / system administrator.\n\n"
        f"WHY:   A corrupted state file prevents safe resume. Deleting it\n"
        f"       forces a fresh run from the scanning step -- no OneDrive\n"
        f"       files are affected by deleting agent_state.json.\n\n"
        f"STEPS:\n"
        f"1. Locate the corrupted file:\n"
        f"   Run: Get-Item agent_state.json\n"
        f"   {_README_NOTE}\n"
        f"2. Delete it:\n"
        f"   Run: Remove-Item agent_state.json\n"
        f"   {_README_NOTE}\n"
        f"3. Re-run the agent from scratch:\n"
        f"   Run: python agent_loop.py\n"
        f"   {_README_NOTE}\n"
        f"Note: no files in your OneDrive folder are affected\n"
        f"by deleting agent_state.json."
    )
    alert_on_error(subject, body)


def alert_sendgrid_failure(error_detail: str) -> None:
    """SendGrid alert delivery failed -- key invalid, expired, or network issue."""
    subject = "Alert delivery failed"
    body = (
        f"WHAT:  The agent tried to send an alert email but failed.\n"
        f"       Detail: {error_detail}\n"
        f"       The SendGrid API key may be invalid or expired.\n\n"
        f"WHEN:  {_now_utc()}\n"
        f"       Fix when convenient -- this does not stop the agent,\n"
        f"       but means future alerts will also fail to deliver.\n\n"
        f"WHERE: Failed at: SendGrid API (alert delivery layer).\n"
        f"       Fix at: Windows environment variables + SendGrid console.\n"
        f"       {_README_NOTE}\n\n"
        f"TRIGGERED BY: An invalid, expired, or missing\n"
        f"       SENDGRID_API_KEY on machine: {_masked_user_id()}\n"
        f"       Fix by: the agent owner / system administrator.\n\n"
        f"WHY:   Without a valid SendGrid key, the agent cannot send\n"
        f"       alert emails. Other failures during a run will occur\n"
        f"       silently -- check the run log for any missed errors.\n\n"
        f"STEPS:\n"
        f"1. Open a new PowerShell terminal.\n"
        f"2. Verify the key is set:\n"
        f"   Run: echo $env:SENDGRID_API_KEY\n"
        f"   {_README_NOTE}\n"
        f"3. If blank or incorrect, re-run setup steps in README.md.\n"
        f"4. Check your key is active at:\n"
        f"   app.sendgrid.com/settings/api_keys\n"
        f"5. Check the run log for missed errors:\n"
        f"   Run: Get-ChildItem logs\\ | Sort-Object LastWriteTime | Select-Object -Last 1\n"
        f"   {_README_NOTE}"
    )
    alert_on_error(subject, body)
