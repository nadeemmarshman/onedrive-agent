"""
Read-only duplicate scan for OneDrive\\1. Documents -- proposal-only,
no files moved. This folder holds financial/legal/ID documents and has
two duplication patterns not seen in the photo-folder live runs:

1. DocFolderBackup mirrors the live folder's own structure (an old full
   backup sitting alongside the live copy) -- duplicates here span two
   different top-level folders, not a same-folder naming-suffix pair.
2. Internal self-duplication -- the same file found nested at multiple
   paths inside the live tree itself (e.g. a folder copy-pasted into
   itself), with no filename-suffix signal to go on at all.

Neither pattern fits dedup_keeper.py's suffix-based logic (built for
same-folder " 1" / "(1)" OneDrive sync-conflict copies), so this script
doesn't move anything -- it classifies each duplicate group by pattern
and writes a report for human review before any quarantine step runs.
"""

import json
from pathlib import Path

from tools import scan_folder, find_duplicates

TARGET_FOLDER = r"<DOCS_ROOT>"
BACKUP_MARKER = "DocFolderBackup"


def _classify(group: list[dict]) -> str:
    in_backup = [BACKUP_MARKER in f["path"] for f in group]
    if any(in_backup) and not all(in_backup):
        return "docfolderbackup_vs_live"
    if not any(in_backup):
        return "internal_duplicate_in_live_tree"
    return "internal_duplicate_within_backup"


def _suggest_keeper(group: list[dict]) -> dict:
    # Prefer a file not under DocFolderBackup; among ties, prefer the
    # shortest path (shallowest nesting -- a weak signal against the
    # copy-pasted-into-itself pattern, not a strong rule).
    not_backup = [f for f in group if BACKUP_MARKER not in f["path"]]
    candidates = not_backup if not_backup else group
    return min(candidates, key=lambda f: len(f["path"]))


def scan(folder: str = TARGET_FOLDER) -> dict:
    files = scan_folder(folder, recursive=True)
    dup_groups = find_duplicates(files)

    report = {
        "files_scanned": len(files),
        "duplicate_groups": len(dup_groups),
        "groups": [],
    }

    by_pattern = {}
    for group in dup_groups:
        pattern = _classify(group)
        keeper = _suggest_keeper(group)
        entry = {
            "pattern": pattern,
            "suggested_keeper": keeper["path"],
            "members": [f["path"] for f in group],
            "size_bytes": group[0]["size_bytes"],
            "redundant_bytes": group[0]["size_bytes"] * (len(group) - 1),
        }
        report["groups"].append(entry)
        by_pattern.setdefault(pattern, []).append(entry)

    report["summary_by_pattern"] = {
        pattern: {
            "group_count": len(entries),
            "redundant_bytes": sum(e["redundant_bytes"] for e in entries),
        }
        for pattern, entries in by_pattern.items()
    }
    report["total_redundant_bytes"] = sum(
        e["redundant_bytes"] for e in report["groups"]
    )

    return report


if __name__ == "__main__":
    report = scan()
    print(f"Scanned {report['files_scanned']} files")
    print(f"Found {report['duplicate_groups']} duplicate group(s)")
    print(f"Total reclaimable: {report['total_redundant_bytes'] / 1024 / 1024:.1f} MB")
    print()
    print("By pattern:")
    for pattern, stats in report["summary_by_pattern"].items():
        print(f"  {pattern}: {stats['group_count']} groups, "
              f"{stats['redundant_bytes'] / 1024 / 1024:.1f} MB")

    with open("DOCUMENTS_DEDUP_PROPOSAL.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print()
    print("Full detail written to DOCUMENTS_DEDUP_PROPOSAL.json")
