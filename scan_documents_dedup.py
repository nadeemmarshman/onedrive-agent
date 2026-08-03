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


def _classify(group: list[dict]) -> list[str]:
    """Multi-label: a group can be BOTH a backup/live pair AND carry
    internal duplication on one or both sides. The original single-label
    version asked only "does this span the backup boundary?" and, if so,
    stopped -- so a 4-member group (1 backup + 3 live) was labelled
    docfolderbackup_vs_live only, its 3-way live-tree redundancy never
    reported. Deleting the backup copy alone (that class's remediation)
    left the other two untouched and invisible to every summary.

    Found by an independent post-action re-scan (Cowork, 2026-08-03):
    238 of 242 groups it had flagged were still duplicated on disk after
    the phase closed. See COWORK_RECONCILIATION_FINDING_v1.0.md.
    """
    live = [f for f in group if BACKUP_MARKER not in f["path"]]
    backup = [f for f in group if BACKUP_MARKER in f["path"]]
    labels = []
    if backup and live:
        labels.append("docfolderbackup_vs_live")
    if len(live) > 1:
        labels.append("internal_duplicate_in_live_tree")
    if len(backup) > 1:
        labels.append("internal_duplicate_within_backup")
    return labels


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

    by_pattern: dict[str, list[dict]] = {}
    for group in dup_groups:
        labels = _classify(group)
        keeper = _suggest_keeper(group)
        size = group[0]["size_bytes"]
        live = [f for f in group if BACKUP_MARKER not in f["path"]]
        backup = [f for f in group if BACKUP_MARKER in f["path"]]

        # Per-label redundant bytes, scoped to what THAT label's own
        # remediation would actually remove -- not the group total. These
        # are deliberately allowed to overlap across labels (e.g. a backup
        # copy counted once under docfolderbackup_vs_live even though the
        # group also carries live-tree redundancy); summing them would
        # double-count, so total_redundant_bytes below uses the group-level
        # figure instead, exactly as before.
        redundant_by_pattern = {}
        if "docfolderbackup_vs_live" in labels:
            redundant_by_pattern["docfolderbackup_vs_live"] = size * len(backup)
        if "internal_duplicate_in_live_tree" in labels:
            redundant_by_pattern["internal_duplicate_in_live_tree"] = size * (len(live) - 1)
        if "internal_duplicate_within_backup" in labels:
            redundant_by_pattern["internal_duplicate_within_backup"] = size * (len(backup) - 1)

        entry = {
            "patterns": labels,
            "suggested_keeper": keeper["path"],
            "members": [f["path"] for f in group],
            "size_bytes": size,
            "redundant_bytes": size * (len(group) - 1),
            "redundant_bytes_by_pattern": redundant_by_pattern,
        }
        report["groups"].append(entry)
        for label in labels:
            by_pattern.setdefault(label, []).append(entry)

    report["summary_by_pattern"] = {
        pattern: {
            "group_count": len(entries),
            "redundant_bytes": sum(e["redundant_bytes_by_pattern"][pattern] for e in entries),
        }
        for pattern, entries in by_pattern.items()
    }
    # Group-level, not a sum of the per-pattern figures above -- a group
    # can carry more than one label, and summing would double-count the
    # bytes each label's own remediation would remove.
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
