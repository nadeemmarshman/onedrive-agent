r"""
Quarantine execution for the 266-group internal-duplicate rescan
(DOCUMENTS_DEDUP_RESCAN_20260803.md, RAID I28).

Excludes one group deliberately: a 0-byte group of four unrelated files
(Default.rdp, two NetBeans build artifacts, a .write_test marker) that
are byte-identical only because they are all empty -- a false positive
of content-hash matching, not a real duplicate, consistent with the
zero-byte-false-positive judgement made earlier in this project's live
runs. 265 real groups act on 590.9 MB of genuine redundancy.

For each group: the suggested_keeper stays in place; every other member
is moved into a quarantine folder, preserving its full relative path
from "1. Documents\" so provenance is never lost and no name collision
is possible (unlike the DocFolderBackup phase, there is no separate
staging step here -- these are all live-tree files with no reorganised
destination to guess at, so relative-path preservation is both correct
and sufficient).

Preflights every file's existence and size against the raw scan JSON
immediately before moving it, so a stale scan cannot authorise a wrong
move. Read-only until the loop that actually calls shutil.move.

Never deletes. Final delete is Nadeem's call, same as every phase.
"""

import json
from pathlib import Path
import shutil

RAW_JSON = Path("_raw_local_only/DOCUMENTS_DEDUP_PROPOSAL_20260803.json")
DOCS_ROOT = Path(r"<DOCS_ROOT>")
QUARANTINE_DIR = DOCS_ROOT / "_Duplicates_PendingDeletion" / "Internal_Duplicates_20260803"


def main() -> None:
    data = json.loads(RAW_JSON.read_text(encoding="utf-8"))
    groups = [g for g in data["groups"] if g["size_bytes"] > 0]
    excluded = len(data["groups"]) - len(groups)
    print(f"{len(groups)} groups to action ({excluded} zero-byte false-positive group excluded)")

    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

    moved, skipped, errors = [], [], []
    for g in groups:
        keeper = g["suggested_keeper"]
        for member in g["members"]:
            if member == keeper:
                continue
            src = Path(member)

            # Preflight: re-verify against the live filesystem, not the
            # scan's memory of it, immediately before acting.
            if not src.is_file():
                skipped.append((member, "no longer exists"))
                continue
            actual_size = src.stat().st_size
            if actual_size != g["size_bytes"]:
                skipped.append((member, f"size changed: expected {g['size_bytes']}, got {actual_size}"))
                continue
            if not Path(keeper).is_file():
                skipped.append((member, f"keeper missing: {keeper}"))
                continue

            rel = src.relative_to(DOCS_ROOT)
            dest = QUARANTINE_DIR / rel
            if dest.exists():
                errors.append((member, f"destination already exists: {dest}"))
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(src), str(dest))
                moved.append((member, str(dest)))
            except OSError as e:
                errors.append((member, str(e)))

    print(f"\nMoved: {len(moved)}")
    print(f"Skipped (stale/changed): {len(skipped)}")
    for m, reason in skipped:
        print(f"  SKIP: {m} -- {reason}")
    print(f"Errors: {len(errors)}")
    for m, reason in errors:
        print(f"  ERROR: {m} -- {reason}")

    total_bytes = sum(g["redundant_bytes"] for g in groups)
    print(f"\nExpected reclaimable: {total_bytes / 1024 / 1024:.1f} MB")
    print(f"Quarantine location: {QUARANTINE_DIR}")


if __name__ == "__main__":
    main()
