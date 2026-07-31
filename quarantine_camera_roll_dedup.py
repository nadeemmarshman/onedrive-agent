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

Reuses find_duplicates() (byte-for-byte MD5) and the shared
keeper-selection fix in dedup_keeper.py: a plain-named file is preferred
as keeper over a " 1"/"(1)"-suffixed OneDrive sync-conflict copy.
"""

import shutil
from pathlib import Path

from tools import scan_folder, find_duplicates
from dedup_keeper import reorder_keeper_first

TARGET_FOLDER = r"C:\Users\Nadeem\OneDrive\Pictures\Camera Roll"
QUARANTINE_SUBFOLDER_NAME = "_Duplicates_PendingDeletion"


def quarantine_duplicates(folder: str = TARGET_FOLDER) -> list[dict]:
    files = scan_folder(folder, recursive=True)
    dup_groups = [reorder_keeper_first(g) for g in find_duplicates(files)]

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
