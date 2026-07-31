"""
Live run: byte-for-byte duplicate detection against the Pictures root
folder (top-level files only -- Camera Roll and Screenshots are separate
subfolders, already handled/out of scope here).

Same pattern as quarantine_camera_roll_dedup.py: uses tools.py's
scan_folder/find_duplicates unmodified, applies the shared
plain-name-preferred keeper-selection fix (RAID I21, dedup_keeper.py),
and moves duplicates into a quarantine subfolder rather than deleting
them directly -- final delete stays a separate, human-initiated step.
"""

import shutil
from pathlib import Path

from tools import scan_folder, find_duplicates
from dedup_keeper import reorder_keeper_first

TARGET_FOLDER = r"C:\Users\Nadeem\OneDrive\Pictures"
QUARANTINE_SUBFOLDER_NAME = "_Duplicates_PendingDeletion"


def quarantine_duplicates(folder: str = TARGET_FOLDER) -> list[dict]:
    files = scan_folder(folder, recursive=False)
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
                "size_bytes": dup["size_bytes"],
            })

    return moved, len(files), len(dup_groups)


if __name__ == "__main__":
    moved, total_scanned, group_count = quarantine_duplicates()
    print(f"Scanned {total_scanned} files (top-level only)")
    print(f"Found {group_count} duplicate group(s)")
    total_bytes = sum(m["size_bytes"] for m in moved)
    print(f"Moved {len(moved)} duplicate file(s), {total_bytes / 1024 / 1024:.1f} MB, to {QUARANTINE_SUBFOLDER_NAME}\\")
    for entry in moved:
        print(f"  '{entry['moved']}' -> kept '{entry['kept_original_at']}'")
