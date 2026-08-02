r"""
DR-backup integrity verification for the 2026-07-31 D:\ backup of
OneDrive\1. Documents.

Count/size matching (already done via robocopy's own summary + an
independent find/du check) is not sufficient proof for a DR backup --
this computes a full MD5 manifest of every file on both sides, keyed by
relative path, and diffs them. Same rigor as the original project's
CP1/CP2/CP3 checkpoint manifests (TEST_BED_AND_CASES.md v2.0 Sec8),
applied here to a backup instead of a live-run dedup pass.
"""

import hashlib
import json
from pathlib import Path

SOURCE = r"<DOCS_ROOT>"
BACKUP = r"<DR_BACKUP_ROOT>"


def _hash_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def build_manifest(root: str) -> dict:
    root_path = Path(root)
    manifest = {}
    for entry in root_path.rglob("*"):
        if entry.is_file():
            rel = str(entry.relative_to(root_path))
            manifest[rel] = {
                "size_bytes": entry.stat().st_size,
                "md5": _hash_file(entry),
            }
    return manifest


def main():
    print("Hashing source (this will take a few minutes for 6.5 GB)...")
    source_manifest = build_manifest(SOURCE)
    print(f"  {len(source_manifest)} files hashed in source")

    print("Hashing backup...")
    backup_manifest = build_manifest(BACKUP)
    print(f"  {len(backup_manifest)} files hashed in backup")

    source_paths = set(source_manifest)
    backup_paths = set(backup_manifest)

    missing_from_backup = source_paths - backup_paths
    extra_in_backup = backup_paths - source_paths
    common = source_paths & backup_paths

    hash_mismatches = [
        rel for rel in common
        if source_manifest[rel]["md5"] != backup_manifest[rel]["md5"]
    ]

    result = {
        "source_file_count": len(source_manifest),
        "backup_file_count": len(backup_manifest),
        "missing_from_backup": sorted(missing_from_backup),
        "extra_in_backup": sorted(extra_in_backup),
        "hash_mismatches": sorted(hash_mismatches),
        "verified_identical_count": len(common) - len(hash_mismatches),
        "pass": not missing_from_backup and not extra_in_backup and not hash_mismatches,
    }

    with open("DOCUMENTS_BACKUP_VERIFICATION.json", "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)

    print()
    print(f"Source files: {result['source_file_count']}")
    print(f"Backup files: {result['backup_file_count']}")
    print(f"Missing from backup: {len(missing_from_backup)}")
    print(f"Extra in backup (unexpected): {len(extra_in_backup)}")
    print(f"Hash mismatches: {len(hash_mismatches)}")
    print(f"Verified byte-identical: {result['verified_identical_count']}")
    print()
    print("PASS" if result["pass"] else "FAIL -- see DOCUMENTS_BACKUP_VERIFICATION.json for detail")


if __name__ == "__main__":
    main()
