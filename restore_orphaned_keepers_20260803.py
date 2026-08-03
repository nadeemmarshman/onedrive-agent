r"""
Restore for RAID (over-quarantine defect, Cowork v1.1 finding).

Restores documents whose ONLY surviving copy was accidentally moved to
quarantine on 2026-08-03, when keeper selection assumed every group had
at least one member outside the action set.

Independently re-verified against Cowork's COWORK_ORPHANED_KEEPERS_v1.1.json
before building this: an own full-tree MD5 scan (not scoped to "two
mounted roots" the way Cowork's was) found only 1 of Cowork's 31 flagged
documents is a TRUE orphan with zero surviving copies anywhere in
1. Documents. The other 30 all have a byte-identical live copy sitting in
a folder outside Cowork's mounted scope (top-level Certificates\, ShareX\,
Unsorted\, or a root-level file) -- so deleting quarantine as it stood
would NOT have destroyed the only copy of those 30. Restoring them anyway,
because:

  - For the 21 "5 Certificates" documents specifically, the surviving
    live copy sits in the OLD, stale, top-level Certificates\ folder,
    not the deliberately organised 00-My Folders\2 Career Documents\
    5 Certificates\ folder this project judged canonical earlier in this
    same phase (numbered sequentially, contains items the stale folder
    lacks). Keeper selection's shortest-path heuristic picked the
    shorter absolute path -- the stale folder -- as keeper every time,
    silently reversing that earlier deliberate judgement. Restoring puts
    the organised copy back where it belongs; the stale duplicate is
    left alone for a separate, later decision, not auto-resolved again.
  - For the remaining 9 (ShareX config backups, an Unsorted resume POE),
    restoring is simply the conservative default -- a copy already
    exists elsewhere, so this isn't urgent, but there's no reason not to
    put it back exactly where it was.

The 31st document Cowork flagged (CV_Superseded\<third-party-3>, a
third party's CV) is DELIBERATELY EXCLUDED. It is not a defect: it was
quarantined on purpose, after real content comparison, by an earlier,
already-completed reconciliation (commit 0de68ec) that concluded this
was genuinely the superseded copy of a third party's document.
Restoring it would undo a correct decision, not fix a mistake. It
correctly has no live copy because that was the intended outcome.

Every restore is preflighted immediately before acting: restore_from
must exist in quarantine with the expected size, and restore_to must
NOT already exist (never overwrite).
"""

import json
from pathlib import Path
import shutil

ORPHAN_JSON = Path("_raw_local_only/COWORK_ORPHANED_KEEPERS_v1.1.json")
EXCLUDE_SUBSTRING = "CV_Superseded"  # deliberate prior decision, not a defect


def main() -> None:
    data = json.loads(ORPHAN_JSON.read_text(encoding="utf-8"))
    docs = [d for d in data["documents"] if EXCLUDE_SUBSTRING not in d["restore_to"]]
    excluded = len(data["documents"]) - len(docs)
    print(f"{len(docs)} documents to restore ({excluded} excluded: deliberate prior decision, not a defect)")

    restored, skipped, errors = [], [], []
    for doc in docs:
        src = Path(doc["restore_from"])
        dest = Path(doc["restore_to"])

        if not src.is_file():
            skipped.append((str(src), "no longer exists in quarantine"))
            continue
        actual_size = src.stat().st_size
        if actual_size != doc["size_bytes"]:
            skipped.append((str(src), f"size changed: expected {doc['size_bytes']}, got {actual_size}"))
            continue
        if dest.exists():
            errors.append((str(dest), "destination already exists -- refusing to overwrite"))
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(src), str(dest))
            restored.append((str(src), str(dest)))
        except OSError as e:
            errors.append((str(src), str(e)))

    print(f"\nRestored: {len(restored)}")
    for s, d in restored:
        print(f"  {d}")
    print(f"\nSkipped: {len(skipped)}")
    for p, reason in skipped:
        print(f"  SKIP: {p} -- {reason}")
    print(f"\nErrors: {len(errors)}")
    for p, reason in errors:
        print(f"  ERROR: {p} -- {reason}")


if __name__ == "__main__":
    main()
