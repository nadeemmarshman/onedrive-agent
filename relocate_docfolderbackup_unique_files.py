"""
Step 1 of the DocFolderBackup wholesale-quarantine plan: relocate the 58
files confirmed unique (DOCFOLDERBACKUP_DELTA.json) out of DocFolderBackup
and into a staging folder inside the live Documents tree, preserving each
file's original relative path for traceability.

Deliberately does NOT guess a "correct" final home for each file -- the
live tree has been reorganized since DocFolderBackup was created (e.g.
"1. My Folders" -> "00-My Folders", folders moved/renamed), so an
automatic path-remap would be guessing, not deriving. Nadeem triages
final placement later, per his own instruction. This step's only job:
get unique content out of a folder that's about to be quarantined,
without losing the context of where it came from.
"""

import json
import shutil
from pathlib import Path

DELTA_JSON = r"C:\Dev\onedrive-agent\DOCFOLDERBACKUP_DELTA.json"
BACKUP_ROOT = Path(r"<DOCS_ROOT>\DocFolderBackup\Documents")
STAGING_ROOT = Path(r"<DOCS_ROOT>\_DocFolderBackup_Unique_Files_ToReview")


def relocate() -> list[dict]:
    data = json.load(open(DELTA_JSON, encoding="utf-8"))
    moved = []
    for entry in data["unique_file_list"]:
        src = Path(entry["path"])
        rel = src.relative_to(BACKUP_ROOT)
        dest = STAGING_ROOT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        moved.append({"relative_path": str(rel), "size_bytes": entry["size_bytes"]})
    return moved


if __name__ == "__main__":
    moved = relocate()
    total = sum(m["size_bytes"] for m in moved)
    print(f"Relocated {len(moved)} files, {total / 1024 / 1024:.1f} MB, to {STAGING_ROOT}")
    for m in moved:
        print(f"  {m['relative_path']}")
