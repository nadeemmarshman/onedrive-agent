"""
Quarantine step for the 2026-07-30 live run: moves files identified as
duplicates into a subfolder within the scanned folder, instead of
deleting them directly.

Process change (requested 2026-07-30): direct deletion of real files was
explicitly declined -- permanent deletion is a prohibited action for this
assistant regardless of user authorization. Moving files is reversible
(they can be moved back, and nothing is destroyed), so it proceeds as a
regular action. The user does the final delete themselves, from the
quarantine subfolder, once satisfied.

Reuses find_duplicates() (byte-for-byte MD5) and the same keeper-selection
fix as propose_camera_roll_dedup.py: a plain-named file is preferred as
keeper over a " 1"/" 2"-suffixed OneDrive sync-conflict copy.
"""

import shutil
from pathlib import Path

from tools import scan_folder, find_duplicates

TARGET_FOLDER = r"C:\Users\Nadeem\OneDrive\Pictures\Camera Roll"
QUARANTINE_SUBFOLDER_NAME = "_Duplicates_PendingDeletion"


def _is_onedrive_conflict_copy(name: str) -> bool:
    stem = name.rsplit(".", 1)[0]
    parts = stem.rsplit(" ", 1)
    return len(parts) == 2 and parts[1].isdigit()


def _reorder_keeper_first(group: list[dict]) -> list[dict]:
    plain = [f for f in group if not _is_onedrive_conflict_copy(f["name"])]
    suffixed = [f for f in group if _is_onedrive_conflict_copy(f["name"])]
    return (plain + suffixed) if plain else group


def quarantine_duplicates(folder: str = TARGET_FOLDER) -> list[dict]:
    files = scan_folder(folder, recursive=True)
    dup_groups = [_reorder_keeper_first(g) for g in find_duplicates(files)]

    quarantine_dir = Path(folder) / QUARANTINE_SUBFOLDER_NAME
    quarantine_dir.mkdir(exist_ok=True)

    moved = []
    for group in dup_groups:
        keeper, *duplicates = group
        for dup in duplicates:
            src = Path(dup["path"])
            dest = quarantine_dir / src.name
            shutil.move(str(src), str(dest))
            moved.append({
                "moved": src.name,
                "kept_original_at": keeper["name"],
                "new_location": str(dest),
            })

    return moved


if __name__ == "__main__":
    for entry in quarantine_duplicates():
        print(f"Moved '{entry['moved']}' -> {QUARANTINE_SUBFOLDER_NAME}\\ "
              f"(kept: '{entry['kept_original_at']}')")
