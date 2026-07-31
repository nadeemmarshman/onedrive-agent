"""
Shared keeper-selection logic for the live-run scripts (Camera Roll,
Pictures root, and any future folder). Extracted 2026-07-31 after the
same incomplete check was independently copied into three scripts and
one copy (Pictures root) got 32 groups backwards as a result -- it only
recognised OneDrive's " 1" conflict-copy suffix, not the "(1)" suffix
seen elsewhere in the same OneDrive account. See LIVE_RUN_PICTURES_ROOT.md
for the incident and fix.

Not merged into tools.py -- that's Phase 1 of the closed foundational
build (see RAID I21, Backlog #15 for the equivalent, deliberately
deferred fix there).
"""

import re

_CONFLICT_COPY_SUFFIX = re.compile(r" (\(\d+\)|\d+)$")


def is_onedrive_conflict_copy(name: str) -> bool:
    """True if `name` ends in a sync-conflict suffix before the extension:
    "name 1.jpg" or "name (1).jpg" -- both seen in this OneDrive account."""
    stem = name.rsplit(".", 1)[0]
    return bool(_CONFLICT_COPY_SUFFIX.search(stem))


def reorder_keeper_first(group: list[dict]) -> list[dict]:
    """Reorders a find_duplicates() group so a plain-named file (if any)
    comes first, since propose_action()/manual keeper logic elsewhere
    treats group[0] as the file to keep."""
    plain = [f for f in group if not is_onedrive_conflict_copy(f["name"])]
    suffixed = [f for f in group if is_onedrive_conflict_copy(f["name"])]
    return (plain + suffixed) if plain else group
