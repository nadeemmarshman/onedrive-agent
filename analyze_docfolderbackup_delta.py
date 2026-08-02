"""
Delta analysis for DocFolderBackup before any wholesale-delete decision.

"Near-total mirror" is not "total mirror" -- this identifies exactly
which files inside DocFolderBackup have NO matching duplicate anywhere
else in the tree (i.e. unique content that would be permanently lost if
the whole folder were deleted), rather than assuming full overlap from
the aggregate MB figures alone.
"""

import json
from pathlib import Path

from tools import scan_folder, find_duplicates

ROOT = r"<DOCS_ROOT>"
BACKUP_FOLDER = str(Path(ROOT) / "DocFolderBackup")

DUP_PROPOSAL = "DOCUMENTS_DEDUP_PROPOSAL.json"


def main():
    # Full listing of everything inside DocFolderBackup right now.
    backup_files = scan_folder(BACKUP_FOLDER, recursive=True)
    backup_paths = {f["path"] for f in backup_files}
    total_backup_bytes = sum(f["size_bytes"] for f in backup_files)

    # Every path that appeared as a member of some duplicate group.
    report = json.load(open(DUP_PROPOSAL, encoding="utf-8"))
    duplicated_paths = set()
    for g in report["groups"]:
        duplicated_paths.update(g["members"])

    backup_paths_with_a_duplicate = backup_paths & duplicated_paths
    backup_paths_unique = backup_paths - duplicated_paths

    unique_bytes = 0
    unique_entries = []
    by_path = {f["path"]: f for f in backup_files}
    for p in backup_paths_unique:
        f = by_path[p]
        unique_bytes += f["size_bytes"]
        unique_entries.append(f)

    print(f"DocFolderBackup: {len(backup_files)} files, {total_backup_bytes/1024/1024:.1f} MB total")
    print(f"  -- with a duplicate elsewhere: {len(backup_paths_with_a_duplicate)} files "
          f"({(total_backup_bytes - unique_bytes)/1024/1024:.1f} MB) -- safe to lose if deleted")
    print(f"  -- UNIQUE, no duplicate found: {len(backup_paths_unique)} files "
          f"({unique_bytes/1024/1024:.1f} MB) -- would be PERMANENTLY LOST if the whole folder is deleted")
    print()
    print("Unique (would-be-lost) files, sorted by size:")
    for f in sorted(unique_entries, key=lambda x: -x["size_bytes"]):
        rel = str(Path(f["path"]).relative_to(BACKUP_FOLDER))
        print(f"  {f['size_bytes']/1024:.1f} KB  {rel}")

    with open("DOCFOLDERBACKUP_DELTA.json", "w", encoding="utf-8") as fh:
        json.dump({
            "total_files": len(backup_files),
            "total_bytes": total_backup_bytes,
            "duplicated_files": len(backup_paths_with_a_duplicate),
            "duplicated_bytes": total_backup_bytes - unique_bytes,
            "unique_files": len(backup_paths_unique),
            "unique_bytes": unique_bytes,
            "unique_file_list": [
                {"path": f["path"], "size_bytes": f["size_bytes"]}
                for f in sorted(unique_entries, key=lambda x: -x["size_bytes"])
            ],
        }, fh, indent=2)
    print()
    print("Full detail written to DOCFOLDERBACKUP_DELTA.json")


if __name__ == "__main__":
    main()
