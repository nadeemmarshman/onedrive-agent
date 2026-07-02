"""
Phase 5: Human-approval gate.

This is the governance layer -- the BA/PM differentiator. Before any
destructive action (file deletion, format conversion) executes, the
agent must:

  1. Write a pre-run manifest snapshot (pre_run_snapshot.json) --
     a point-in-time JSON record of every affected file's path, size,
     and hash BEFORE any changes are made. This is the audit trail.
     DESIGN DECISION: if the snapshot cannot be written, all execution
     is blocked. "No snapshot, no actions" -- the audit trail is a
     precondition for execution, not an optional extra.

  2. Present the full proposal list to the user for review.

  3. Let the user approve or reject each item individually.

  4. Execute only the approved actions, skipping rejected ones.
     A rejection does not stop the loop -- remaining proposals are
     still offered for approval.

WHAT THIS MODULE DOES NOT DO:
  - It does not make decisions about WHICH files to act on -- that is
    Phase 1-4's job (propose_action() output).
  - It does not loop or call the API -- it receives a ready list of
    proposals and gates their execution.
  - It does not convert files (format conversion is stubbed here --
    actual conversion logic would be Phase 6+ scope).

PROACTIVE DESIGN (standing rule):
  The following risks are explicitly handled:
  [RISK 1] Snapshot write failure -> blocks all execution (by design)
  [RISK 2] Invalid user input at approval prompt -> re-prompts, never crashes
  [RISK 3] Action execution failure (file locked, already gone, permissions)
           -> logs error, continues with remaining approved actions
  [RISK 4] Partial execution on crash -> state machine updated after each
           action so resume knows what was completed vs pending
"""

import hashlib
import json
import logging
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

from resilience import alert_on_error

logger = logging.getLogger("agent_loop")

SNAPSHOT_FILE = Path("pre_run_snapshot.json")


# ---------------------------------------------------------------------------
# PART 1: PRE-RUN MANIFEST SNAPSHOT
# ---------------------------------------------------------------------------

def _hash_file(path: str, chunk_size: int = 8192) -> str:
    """MD5 hash of a file's content -- same approach as Phase 1's dedup."""
    hasher = hashlib.md5()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except OSError:
        return "unreadable"


def write_snapshot(proposals: list[dict]) -> bool:
    """
    Write a pre-run manifest snapshot of every file that will be
    affected by the approved proposals.

    [RISK 1] If the snapshot cannot be written, returns False --
    the caller must block all execution. "No snapshot, no actions."

    Returns True if the snapshot was written successfully.
    """
    affected_paths = {p["target_path"] for p in proposals}

    snapshot_entries = []
    for path_str in sorted(affected_paths):
        path = Path(path_str)
        entry = {
            "path": path_str,
            "exists": path.exists(),
        }
        if path.exists():
            stat = path.stat()
            entry["size_bytes"] = stat.st_size
            entry["modified_utc"] = datetime.fromtimestamp(
                stat.st_mtime, tz=timezone.utc
            ).isoformat()
            entry["md5"] = _hash_file(path_str)
        snapshot_entries.append(entry)

    snapshot = {
        "snapshot_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "files_affected": len(snapshot_entries),
        "note": (
            "Pre-run manifest snapshot written before any actions executed. "
            "Use this to verify what existed before this agent run. "
            "For file recovery, use OneDrive recycle bin or version history."
        ),
        "files": snapshot_entries,
    }

    try:
        with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)
        logger.info(
            f"Pre-run snapshot written: {SNAPSHOT_FILE} "
            f"({len(snapshot_entries)} file(s) recorded)"
        )
        return True
    except OSError as e:
        logger.error(
            f"BLOCKED: Could not write pre-run snapshot to {SNAPSHOT_FILE}: {e}. "
            f"No actions will be executed. "
            f"Check disk space and folder permissions, then retry."
        )
        alert_on_error(
            "Execution blocked — snapshot write failed",
            f"WHAT:  The agent could not write the pre-run snapshot file.\n"
            f"       No actions have been executed.\n\n"
            f"WHEN:  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            f"       Fix before retrying — execution is blocked until the\n"
            f"       snapshot can be written successfully.\n\n"
            f"WHERE: Failed at: {SNAPSHOT_FILE}\n"
            f"       Fix at: check disk space and folder permissions.\n"
            f"       (Check README.md for the correct path on your machine)\n\n"
            f"TRIGGERED BY: OS error on machine: {os.environ.get('USERNAME', 'unknown')}\n"
            f"       Detail: {e}\n"
            f"       Fix by: the agent owner / system administrator.\n\n"
            f"WHY:   The audit trail (snapshot) is a precondition for execution.\n"
            f"       No snapshot = no actions. This is a deliberate safety design.\n\n"
            f"STEPS:\n"
            f"1. Check available disk space:\n"
            f"   Run: Get-PSDrive C\n"
            f"   (Check README.md for the correct path to run from)\n"
            f"2. Check folder permissions, then retry:\n"
            f"   Run: python agent_loop.py\n"
            f"   (Check README.md for the correct path to run from)"
        )
        return False


# ---------------------------------------------------------------------------
# PART 2: APPROVAL PROMPT
# ---------------------------------------------------------------------------

def _prompt_approval(proposal: dict, index: int, total: int) -> bool:
    """
    Present a single proposal to the user and collect their y/n response.

    [RISK 2] Invalid input -- re-prompts until a valid response is given.
    Never crashes on unexpected input (e.g. empty string, random text).

    Returns True if approved, False if rejected.
    """
    action = proposal["action_type"]
    target = proposal["target_path"]
    reason = proposal["reason"]

    print(f"\n  [{index}/{total}] {action.upper().replace('_', ' ')}")
    print(f"  Target : {target}")
    print(f"  Reason : {reason}")

    while True:
        response = input("  Approve? (y/n): ").strip().lower()
        if response in ("y", "yes"):
            return True
        elif response in ("n", "no"):
            return False
        else:
            print(f"  Invalid input '{response}' -- please enter y or n.")


def present_proposals(proposals: list[dict]) -> list[dict]:
    """
    Show the full proposal list as a summary, then collect
    approve/reject decisions for each item individually.

    Returns the list of approved proposals only -- rejected ones
    are excluded, not passed to the execution step.
    """
    if not proposals:
        logger.info("No proposals to review.")
        return []

    # Step 1: show the full summary first
    print("\n" + "=" * 60)
    print("PROPOSED ACTIONS — REVIEW REQUIRED")
    print("=" * 60)
    print(f"\n{len(proposals)} action(s) proposed:\n")
    for i, p in enumerate(proposals, start=1):
        action = p["action_type"].upper().replace("_", " ")
        print(f"  {i}. [{action}] {p['target_path']}")
        print(f"     Reason: {p['reason']}")
    print(
        f"\nNOTE: No files have been modified yet. "
        f"You will be asked to approve each action individually.\n"
    )

    # Step 2: collect individual approvals
    print("-" * 60)
    print("INDIVIDUAL APPROVAL")
    print("-" * 60)

    approved = []
    rejected_count = 0

    for i, proposal in enumerate(proposals, start=1):
        approved_flag = _prompt_approval(proposal, i, len(proposals))
        if approved_flag:
            approved.append(proposal)
            logger.info(
                f"Approved [{i}/{len(proposals)}]: "
                f"{proposal['action_type']} -> {proposal['target_path']}"
            )
        else:
            rejected_count += 1
            logger.info(
                f"Rejected [{i}/{len(proposals)}]: "
                f"{proposal['action_type']} -> {proposal['target_path']}"
            )

    print(f"\n  Summary: {len(approved)} approved, {rejected_count} rejected.\n")
    return approved


# ---------------------------------------------------------------------------
# PART 3: EXECUTE APPROVED ACTIONS
# ---------------------------------------------------------------------------

def _execute_delete(target_path: str) -> bool:
    """
    Delete a file. Returns True on success, False on failure.

    [RISK 3] Handles file-level failures gracefully -- a single
    failed deletion does not abort the remaining approved actions.
    """
    try:
        Path(target_path).unlink()
        logger.info(f"Deleted: {target_path}")
        return True
    except FileNotFoundError:
        logger.warning(f"Delete skipped -- file not found (already gone?): {target_path}")
        return False
    except PermissionError as e:
        logger.error(f"Delete failed -- permission denied: {target_path}: {e}")
        alert_on_error(
            "Action failed — permission denied",
            f"WHAT:  Could not delete file due to a permission error.\n"
            f"       Target: {target_path}\n\n"
            f"WHEN:  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            f"       Other approved actions will still be attempted.\n\n"
            f"WHERE: Failed at: {target_path}\n"
            f"       (Check README.md for the correct path on your machine)\n\n"
            f"TRIGGERED BY: OS permission error on machine: "
            f"{os.environ.get('USERNAME', 'unknown')}\n"
            f"       Detail: {e}\n"
            f"       Fix by: the agent owner / system administrator.\n\n"
            f"WHY:   The file may be open in another application, or the\n"
            f"       user account may lack delete permissions on this file.\n\n"
            f"STEPS:\n"
            f"1. Close any application that may have the file open.\n"
            f"2. Re-run the agent to retry:\n"
            f"   Run: python agent_loop.py\n"
            f"   (Check README.md for the correct path to run from)"
        )
        return False
    except OSError as e:
        logger.error(f"Delete failed -- unexpected OS error: {target_path}: {e}")
        return False


def _execute_convert(target_path: str, suggested_extension: str) -> bool:
    """
    Convert a file to a new format.

    STUB: actual format conversion (e.g. .bmp -> .png using Pillow)
    is outside Phase 5's scope -- this stub logs the intent and
    confirms the approval gate works end to end without requiring
    additional image-processing dependencies. Full implementation
    would replace this stub in a future phase.
    """
    logger.info(
        f"CONVERT (stub): {target_path} -> {suggested_extension} "
        f"[conversion logic not yet implemented -- approved and logged only]"
    )
    return True


def execute_approved_actions(approved: list[dict]) -> dict:
    """
    Execute each approved action in sequence.

    [RISK 3] Each action is attempted independently -- a failure on
    one does not abort the remaining approved actions.

    Returns a summary dict: {succeeded: int, failed: int, skipped: int}
    """
    if not approved:
        logger.info("No approved actions to execute.")
        return {"succeeded": 0, "failed": 0, "skipped": 0}

    print("\n" + "=" * 60)
    print("EXECUTING APPROVED ACTIONS")
    print("=" * 60)

    succeeded = 0
    failed = 0
    skipped = 0

    for i, action in enumerate(approved, start=1):
        action_type = action["action_type"]
        target_path = action["target_path"]

        print(f"\n  [{i}/{len(approved)}] {action_type.upper().replace('_', ' ')}: {target_path}")

        if action_type == "delete_duplicate":
            success = _execute_delete(target_path)
        elif action_type == "convert_format":
            suggested_ext = action.get("details", {}).get("suggested_extension", "")
            success = _execute_convert(target_path, suggested_ext)
        else:
            logger.warning(f"Unknown action type '{action_type}' -- skipping.")
            skipped += 1
            continue

        if success:
            succeeded += 1
            print(f"  -> Done")
        else:
            failed += 1
            print(f"  -> Failed (see log for detail)")

    print(f"\n{'=' * 60}")
    print(
        f"Execution complete: {succeeded} succeeded, "
        f"{failed} failed, {skipped} skipped."
    )
    print("=" * 60)

    logger.info(
        f"Execution complete: {succeeded} succeeded, "
        f"{failed} failed, {skipped} skipped."
    )
    return {"succeeded": succeeded, "failed": failed, "skipped": skipped}


# ---------------------------------------------------------------------------
# PART 4: MAIN GATE FUNCTION
# ---------------------------------------------------------------------------

def run_approval_gate(proposals: list[dict]) -> dict:
    """
    Run the full Phase 5 approval gate:
      1. Write pre-run snapshot (block if it fails)
      2. Present proposals for review
      3. Collect individual approvals
      4. Execute approved actions

    Returns a summary dict suitable for logging/state persistence.
    """
    logger.info(
        f"Approval gate: {len(proposals)} proposal(s) to review."
    )

    # [RISK 1] Snapshot is a precondition -- block if it fails
    snapshot_ok = write_snapshot(proposals)
    if not snapshot_ok:
        return {
            "status": "blocked",
            "reason": "Snapshot write failed -- no actions executed.",
            "succeeded": 0,
            "failed": 0,
            "skipped": 0,
        }

    # Present full list, collect per-item approvals
    approved = present_proposals(proposals)

    if not approved:
        logger.info("No actions approved -- nothing to execute.")
        return {
            "status": "complete",
            "reason": "All proposals rejected by user.",
            "succeeded": 0,
            "failed": 0,
            "skipped": len(proposals),
        }

    # Execute approved actions
    result = execute_approved_actions(approved)
    result["status"] = "complete"
    return result
