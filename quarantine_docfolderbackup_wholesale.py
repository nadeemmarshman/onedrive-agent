r"""
Step 2 of the DocFolderBackup wholesale-quarantine plan. Run only after
relocate_docfolderbackup_unique_files.py has moved out the 58 unique
files -- everything left in DocFolderBackup at that point is a confirmed
byte-identical duplicate of something in the live tree (DOCFOLDERBACKUP_DELTA.json:
1,118 duplicated files, 2.5 GB).

Moves the whole DocFolderBackup folder in one operation into
_Duplicates_PendingDeletion\DocFolderBackup, rather than 1,118 individual
file moves -- same reversible quarantine pattern as the other live-run
phases, just applied to a whole folder since every remaining file in it
is duplicate content.
"""

import shutil
from pathlib import Path

DOCUMENTS_ROOT = Path(r"<DOCS_ROOT>")
SOURCE = DOCUMENTS_ROOT / "DocFolderBackup"
QUARANTINE_DIR = DOCUMENTS_ROOT / "_Duplicates_PendingDeletion"
DEST = QUARANTINE_DIR / "DocFolderBackup"


def quarantine() -> None:
    QUARANTINE_DIR.mkdir(exist_ok=True)
    if DEST.exists():
        raise FileExistsError(f"Destination already exists: {DEST}")
    shutil.move(str(SOURCE), str(DEST))


if __name__ == "__main__":
    quarantine()
    print(f"Moved {SOURCE} -> {DEST}")
