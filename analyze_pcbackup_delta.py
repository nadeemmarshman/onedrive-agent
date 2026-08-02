r"""
Delta analysis for OneDrive\PC Backup, ahead of any delete decision.

Same shape as analyze_docfolderbackup_delta.py, with one material
difference: DocFolderBackup lived *inside* 1. Documents and was covered
by the existing DOCUMENTS_DEDUP_PROPOSAL.json scan. PC Backup is a
sibling folder at the OneDrive root and was never in that scan's scope,
so this does its own comparison from scratch.

Two constraints shape the implementation:

1. PC Backup is ~entirely OneDrive cloud-only placeholders (852 KB on
   disk vs 2.77 GB logical). Hashing a placeholder forces OneDrive to
   hydrate (download) it. So the hashing order matters for bandwidth.

2. Name+size matching is NOT sufficient evidence to delete. This dataset
   has already produced same-name-same-purpose files with genuinely
   different content (the six "308 <calibre-1>" reload documents found
   during the DocFolderBackup triage). Only a byte-level hash match
   justifies treating a file as redundant.

Bandwidth optimisation (provably safe): a file can only be byte-identical
to another file if their sizes are exactly equal. So any PC Backup file
whose size does not appear anywhere in the live tree is unique by
definition and is never hydrated. Only size-collision candidates get
downloaded and hashed.

Read-only. Moves and deletes nothing.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

from tools import _hash_file, scan_folder

LIVE_ROOT = r"<DOCS_ROOT>"
PCBACKUP_ROOT = r"<ONEDRIVE_ROOT>\PC Backup"
OUT_JSON = "PCBACKUP_DELTA.json"


def _fmt(nbytes: int) -> str:
    return f"{nbytes / 1024 / 1024:.1f} MB"


def main() -> None:
    print("Scanning live tree (local, no download)...", flush=True)
    live_files = scan_folder(LIVE_ROOT, recursive=True)
    live_sizes = {f["size_bytes"] for f in live_files}
    print(f"  live tree: {len(live_files)} files", flush=True)

    print("Scanning PC Backup (metadata only, no download)...", flush=True)
    backup_files = scan_folder(PCBACKUP_ROOT, recursive=True)
    total_backup_bytes = sum(f["size_bytes"] for f in backup_files)
    print(f"  PC Backup: {len(backup_files)} files, {_fmt(total_backup_bytes)}", flush=True)

    # Split before hashing: anything with no size twin in the live tree
    # cannot possibly be a byte-identical duplicate, so never hydrate it.
    candidates = [f for f in backup_files if f["size_bytes"] in live_sizes]
    unique_by_size = [f for f in backup_files if f["size_bytes"] not in live_sizes]
    candidate_bytes = sum(f["size_bytes"] for f in candidates)

    print(f"\n  unique by size alone (no download needed): {len(unique_by_size)} files, "
          f"{_fmt(sum(f['size_bytes'] for f in unique_by_size))}", flush=True)
    print(f"  size-collision candidates (must hydrate + hash): {len(candidates)} files, "
          f"{_fmt(candidate_bytes)}", flush=True)

    # Hash only the live-tree files whose size could matter, so the live
    # side stays cheap too.
    relevant_live_sizes = {f["size_bytes"] for f in candidates}
    live_to_hash = [f for f in live_files if f["size_bytes"] in relevant_live_sizes]
    print(f"\nHashing {len(live_to_hash)} live-tree files (local)...", flush=True)
    live_hashes = set()
    live_hash_to_paths = defaultdict(list)
    for i, f in enumerate(live_to_hash, 1):
        try:
            h = _hash_file(f["path"])
        except OSError as e:
            print(f"  SKIP (unreadable): {f['path']} -- {e}", flush=True)
            continue
        live_hashes.add(h)
        live_hash_to_paths[h].append(f["path"])
        if i % 200 == 0:
            print(f"  ...{i}/{len(live_to_hash)}", flush=True)

    print(f"\nHashing {len(candidates)} PC Backup candidates "
          f"(this downloads {_fmt(candidate_bytes)})...", flush=True)
    duplicated, unique_after_hash = [], []
    done_bytes = 0
    for i, f in enumerate(candidates, 1):
        try:
            h = _hash_file(f["path"])
        except OSError as e:
            # Treat unreadable as unique: never delete what we could not verify.
            print(f"  SKIP (unreadable, treated as UNIQUE): {f['path']} -- {e}", flush=True)
            unique_after_hash.append(f)
            continue
        done_bytes += f["size_bytes"]
        if h in live_hashes:
            f = {**f, "matches_live": live_hash_to_paths[h][0]}
            duplicated.append(f)
        else:
            unique_after_hash.append(f)
        if i % 50 == 0:
            print(f"  ...{i}/{len(candidates)}  ({_fmt(done_bytes)} of {_fmt(candidate_bytes)})",
                  flush=True)

    unique_all = unique_by_size + unique_after_hash
    unique_bytes = sum(f["size_bytes"] for f in unique_all)
    dup_bytes = sum(f["size_bytes"] for f in duplicated)

    assert len(duplicated) + len(unique_all) == len(backup_files), "file accounting mismatch"
    assert dup_bytes + unique_bytes == total_backup_bytes, "byte accounting mismatch"

    print("\n" + "=" * 70)
    print(f"PC Backup: {len(backup_files)} files, {_fmt(total_backup_bytes)}")
    print(f"  byte-identical twin in live tree: {len(duplicated)} files, {_fmt(dup_bytes)} "
          f"-- safe to lose")
    print(f"  UNIQUE (no byte-identical twin):  {len(unique_all)} files, {_fmt(unique_bytes)} "
          f"-- would be PERMANENTLY LOST")
    print("=" * 70)

    print("\nUnique files, largest first:")
    for f in sorted(unique_all, key=lambda x: -x["size_bytes"])[:40]:
        rel = str(Path(f["path"]).relative_to(PCBACKUP_ROOT))
        print(f"  {f['size_bytes'] / 1024:10.1f} KB  {rel}")
    if len(unique_all) > 40:
        print(f"  ... and {len(unique_all) - 40} more (full list in {OUT_JSON})")

    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump({
            "live_root": LIVE_ROOT,
            "pcbackup_root": PCBACKUP_ROOT,
            "total_files": len(backup_files),
            "total_bytes": total_backup_bytes,
            "duplicated_files": len(duplicated),
            "duplicated_bytes": dup_bytes,
            "unique_files": len(unique_all),
            "unique_bytes": unique_bytes,
            "unique_never_hydrated": len(unique_by_size),
            "unique_file_list": [
                {"path": f["path"], "size_bytes": f["size_bytes"]}
                for f in sorted(unique_all, key=lambda x: -x["size_bytes"])
            ],
            "duplicate_file_list": [
                {"path": f["path"], "size_bytes": f["size_bytes"],
                 "matches_live": f.get("matches_live")}
                for f in sorted(duplicated, key=lambda x: -x["size_bytes"])
            ],
        }, fh, indent=2)
    print(f"\nFull detail written to {OUT_JSON}")


if __name__ == "__main__":
    sys.exit(main())
