"""
Re-analyzes the existing duplicate scan (DOCUMENTS_DEDUP_PROPOSAL.json) by
folder-pair rather than file-pair.

The file-level view (948 duplicate groups) doesn't answer the question
that actually matters here: this folder holds multiple independent
"workstreams" (project folders) that were built up over time by copying
subfolders/files between them, so a duplicate file isn't automatically a
mistake -- it might be a deliberate, still-valid part of a workstream.

This groups duplicates by (containing folder A, containing folder B)
pairs -- both at the top-level workstream level (first path segment
under "1. Documents") for the big-picture decision, and at full
directory-pair granularity with actual filenames for everything else,
so a workstream can be judged case by case rather than file by file.
"""

import json
from collections import defaultdict
from pathlib import Path

INPUT = "DOCUMENTS_DEDUP_PROPOSAL.json"
ROOT = r"<DOCS_ROOT>"


def top_level_workstream(path: str) -> str:
    rel = Path(path).relative_to(ROOT)
    return rel.parts[0] if rel.parts else "(root)"


def containing_folder(path: str) -> str:
    return str(Path(path).parent)


def main():
    report = json.load(open(INPUT, encoding="utf-8"))

    # --- Top-level workstream-pair summary ---
    workstream_pairs = defaultdict(lambda: {"groups": 0, "redundant_bytes": 0})
    for g in report["groups"]:
        workstreams = sorted({top_level_workstream(m) for m in g["members"]})
        if len(workstreams) == 1:
            key = (workstreams[0], workstreams[0])  # duplicated within one workstream
        else:
            key = tuple(workstreams[:2]) if len(workstreams) == 2 else tuple(workstreams)
        workstream_pairs[key]["groups"] += 1
        workstream_pairs[key]["redundant_bytes"] += g["redundant_bytes"]

    # --- Full directory-pair detail, with filenames ---
    dir_pairs = defaultdict(list)
    for g in report["groups"]:
        folders = sorted({containing_folder(m) for m in g["members"]})
        key = tuple(folders)
        dir_pairs[key].append({
            "filenames": [Path(m).name for m in g["members"]],
            "size_bytes": g["size_bytes"],
            "redundant_bytes": g["redundant_bytes"],
        })

    lines = []
    lines.append("# Documents folder -- duplicate artefacts by workstream/path\n")
    lines.append(f"Source: {INPUT} ({report['duplicate_groups']} duplicate groups, "
                  f"{report['total_redundant_bytes']/1024/1024:.1f} MB total)\n")

    lines.append("## Top-level workstream-pair summary\n")
    lines.append("Which top-level folders under `1. Documents` overlap with which "
                  "others, and by how much. A pair with a huge group count/size and "
                  "one side named like a backup is a strong wholesale-delete candidate; "
                  "a pair with 1-2 small groups is more likely a couple of files worth "
                  "a individual decision, not a reason to delete either workstream.\n")
    lines.append("| Workstreams involved | Duplicate groups | Redundant MB |")
    lines.append("|---|---|---|")
    for workstreams, stats in sorted(workstream_pairs.items(), key=lambda kv: -kv[1]["redundant_bytes"]):
        lines.append(f"| {', '.join(workstreams)} | {stats['groups']} | {stats['redundant_bytes']/1024/1024:.1f} |")

    lines.append("\n---\n")
    lines.append("## Full path-pair detail (every folder pair, with filenames)\n")
    lines.append("Sorted by redundant size, largest first. Folder-pairs belonging to "
                  "the DocFolderBackup-vs-live bulk are collapsed to a count (see "
                  "summary above); every other pair is listed in full with filenames "
                  "so each can be judged on its own.\n")

    sorted_pairs = sorted(
        dir_pairs.items(),
        key=lambda kv: -sum(e["redundant_bytes"] for e in kv[1])
    )

    backup_bulk_groups = 0
    backup_bulk_bytes = 0
    for folders, entries in sorted_pairs:
        is_backup_pair = any("DocFolderBackup" in f for f in folders) and \
                         any("DocFolderBackup" not in f for f in folders) and \
                         len(folders) == 2
        total_bytes = sum(e["redundant_bytes"] for e in entries)
        if is_backup_pair:
            backup_bulk_groups += len(entries)
            backup_bulk_bytes += total_bytes
            continue

        lines.append(f"### {' <-> '.join(folders)}")
        lines.append(f"{len(entries)} duplicate file(s), {total_bytes/1024/1024:.1f} MB\n")
        for e in entries:
            lines.append(f"- {e['filenames'][0]} ({e['size_bytes']/1024/1024:.2f} MB)"
                          + (f" -- variants: {e['filenames'][1:]}" if len(set(e['filenames'])) > 1 else ""))
        lines.append("")

    lines.append(f"### (collapsed) DocFolderBackup <-> live-tree folder pairs")
    lines.append(f"{backup_bulk_groups} duplicate file(s) across many nested folder-pairs, "
                  f"{backup_bulk_bytes/1024/1024:.1f} MB -- see DOCUMENTS_DEDUP_PROPOSAL.json "
                  f"for the full per-file list if needed; not expanded here since every "
                  f"instance follows the same pattern (DocFolderBackup mirrors the live tree).")

    output = "\n".join(lines)
    with open("DOCUMENTS_WORKSTREAM_DEDUP_REPORT.md", "w", encoding="utf-8") as fh:
        fh.write(output)
    print("Written to DOCUMENTS_WORKSTREAM_DEDUP_REPORT.md")
    print(f"Top-level workstream pairs: {len(workstream_pairs)}")
    print(f"Full directory pairs (non-backup-bulk): {len(sorted_pairs) - sum(1 for f, _ in sorted_pairs if any('DocFolderBackup' in x for x in f) and any('DocFolderBackup' not in x for x in f) and len(f) == 2)}")


if __name__ == "__main__":
    main()
