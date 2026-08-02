r"""
Wholesale quarantine of OneDrive\PC Backup.

PCBACKUP_DELTA.json (byte-level MD5 comparison against the live
1. Documents tree) established:

    1,070 files / 2,840.3 MB total
    1,063 files / 2,836.4 MB  byte-identical twin in the live tree
        7 files /     3.9 MB  unique

and the 7 unique files were each independently flagged unique during the
DocFolderBackup phase and already ruled on by Nadeem then (6 DISCARD,
1 LEAVE-then-deleted). So unlike DocFolderBackup, there is nothing to
rescue first -- no staging step, just the folder move.

Same reversible quarantine pattern as every other live-run phase: this
moves, it does not delete. The final delete stays Nadeem's call.

Quarantine goes to the OneDrive root rather than inside 1. Documents,
because PC Backup is a root-level sibling of 1. Documents, not a child
of it.
"""

import json
import shutil
from pathlib import Path

ONEDRIVE_ROOT = Path(r"<ONEDRIVE_ROOT>")
SOURCE = ONEDRIVE_ROOT / "PC Backup"
QUARANTINE_DIR = ONEDRIVE_ROOT / "_Duplicates_PendingDeletion"
DEST = QUARANTINE_DIR / "PC Backup"
DELTA_JSON = "PCBACKUP_DELTA.json"


def _preflight() -> int:
    """Re-verify the delta against what is actually on disk right now,
    rather than trusting a JSON written earlier in the session."""
    delta = json.load(open(DELTA_JSON, encoding="utf-8"))
    expected = delta["total_files"]
    actual = sum(1 for p in SOURCE.rglob("*") if p.is_file())
    if actual != expected:
        raise AssertionError(
            f"PC Backup changed since the scan: delta says {expected} files, "
            f"disk has {actual}. Re-run analyze_pcbackup_delta.py before moving."
        )
    if delta["unique_files"] != 7:
        raise AssertionError(
            f"Expected 7 unique files (all previously ruled on), got "
            f"{delta['unique_files']} -- do not proceed without re-triage."
        )
    return actual


def quarantine() -> int:
    count = _preflight()
    QUARANTINE_DIR.mkdir(exist_ok=True)
    if DEST.exists():
        raise FileExistsError(f"Destination already exists: {DEST}")
    shutil.move(str(SOURCE), str(DEST))
    return count


if __name__ == "__main__":
    n = quarantine()
    print(f"Moved {SOURCE} -> {DEST}  ({n} files)")
