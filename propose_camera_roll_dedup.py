"""
Proposal generation for the two duplicate groups found by the
2026-07-30 live run (see LIVE_RUN_CAMERA_ROLL.md).

Read-only -- writes a proposal file for human review, per the project's
approval-gate design (approval_gate.py). Nothing is deleted here.

Extends Phase 1's propose_action() with one live-run finding: that
function keeps group[0] as the "keeper" arbitrarily, which is wrong for
OneDrive's own naming convention -- a " 1", " 2", etc. suffix before the
extension marks a sync-conflict copy, not the original. Both duplicate
groups here follow that pattern, so the keeper/duplicate choice is
reordered accordingly before calling propose_action(), via the shared
dedup_keeper.py helper.
"""

import json

from tools import scan_folder, find_duplicates, propose_action
from dedup_keeper import reorder_keeper_first

TARGET_FOLDER = r"C:\Users\Nadeem\OneDrive\Pictures\Camera Roll"


def build_proposals(folder: str = TARGET_FOLDER) -> list[dict]:
    files = scan_folder(folder, recursive=True)
    dup_groups = find_duplicates(files)
    reordered = [reorder_keeper_first(g) for g in dup_groups]
    proposals = propose_action(reordered, convertible_files=[])

    # Trim to filename only -- no full local paths committed to a public repo.
    for p in proposals:
        p["target_path"] = p["target_path"].split("\\")[-1]
        for k in ("keeper_path", "duplicate_path"):
            if k in p.get("details", {}):
                p["details"][k] = p["details"][k].split("\\")[-1]
        p["reason"] = f"Identical content to '{p['details']['keeper_path']}'"

    return proposals


if __name__ == "__main__":
    print(json.dumps(build_proposals(), indent=2))
