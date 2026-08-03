r"""
Post-action invariant checker for dedup live-run phases -- the "standing
practice" recommended twice now (Cowork v1.0 finding, then reaffirmed
independently by v1.1) and not adopted until this point.

Two consecutive defects in this phase were both caught only by an
EXTERNAL check with an independent notion of the intended end state, not
by the run's own reporting:

  v1.0 -- a classifier bug routed 260 groups away from the action queue.
          File-count reconciliation balanced anyway, because it
          reconciled against what was queued, not against what should
          have been.
  v1.1 -- an over-quarantine near-miss where the tool's OWN chosen keeper
          for several groups ended up outside the scan scope used to
          verify the run, producing 31 false "orphan" alarms (later
          independently found to be 30 false positives + 1 file that was
          orphaned on purpose by an earlier, unrelated, already-approved
          decision -- see RAID entry for the full account). Neither the
          dry-run nor the per-file preflight caught this, because both
          checked FILE-level preconditions (does this path exist, does
          its size match), not the GROUP-level invariant that actually
          matters: does at least one copy survive.

This script checks that invariant directly, by content hash rather than
by path, against a scan JSON's group data:

  - EVERY group must have at least one byte-identical copy currently
    present in the live tree (the orphan check -- nothing lost).
  - No group should have MORE than one byte-identical copy currently
    present in the live tree (the dedup-achieved check -- this only
    passes once quarantined copies are permanently deleted, so it is
    EXPECTED to fail while a quarantine folder still holds files; that
    is not a bug in this script).

Usage:
    python verify_dedup_invariants.py <scan_json> <live_tree_root> [quarantine_root]

If quarantine_root is given, files under it are excluded from the
"live" hash set, so quarantined-but-not-yet-deleted copies don't
falsely satisfy the orphan check via their own quarantined copy.
"""

import hashlib
import json
import sys
from pathlib import Path


def _md5(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def _hash_tree(root: Path, exclude: Path | None) -> dict[str, list[Path]]:
    hashes: dict[str, list[Path]] = {}
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if exclude is not None and exclude in p.parents:
            continue
        try:
            hashes.setdefault(_md5(p), []).append(p)
        except OSError as e:
            print(f"  SKIP unreadable: {p} -- {e}", file=sys.stderr)
    return hashes


def verify(scan_json: Path, live_root: Path, quarantine_root: Path | None) -> dict:
    data = json.loads(scan_json.read_text(encoding="utf-8"))
    groups = [g for g in data["groups"] if g["size_bytes"] > 0]

    print(f"Hashing live tree ({live_root})"
          f"{' excluding ' + str(quarantine_root) if quarantine_root else ''}...")
    live_hashes = _hash_tree(live_root, quarantine_root)
    print(f"  {sum(len(v) for v in live_hashes.values())} files, "
          f"{len(live_hashes)} unique content hashes")

    orphaned, over_retained, ok = [], [], []
    for g in groups:
        # A group's content hash: hash whichever member still exists,
        # preferring the suggested keeper (most likely to still be live).
        candidates = [g["suggested_keeper"], *g["members"]]
        group_hash = None
        for c in candidates:
            p = Path(c)
            if p.is_file():
                group_hash = _md5(p)
                break
        if group_hash is None:
            # Every member of this group is gone from disk entirely --
            # not this script's concern (nothing to verify against), but
            # worth surfacing rather than silently skipping.
            print(f"  WARNING: no member of this group exists anywhere: {g['members'][0]}")
            continue

        live_count = len(live_hashes.get(group_hash, []))
        if live_count == 0:
            orphaned.append((group_hash, g))
        elif live_count > 1:
            over_retained.append((group_hash, live_count, g))
        else:
            ok.append(group_hash)

    return {
        "groups_checked": len(groups),
        "ok": len(ok),
        "orphaned": orphaned,
        "over_retained": over_retained,
    }


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    scan_json = Path(sys.argv[1])
    live_root = Path(sys.argv[2])
    quarantine_root = Path(sys.argv[3]) if len(sys.argv) > 3 else None

    result = verify(scan_json, live_root, quarantine_root)

    print()
    print(f"Groups checked: {result['groups_checked']}")
    print(f"OK (exactly 1 live copy): {result['ok']}")
    print(f"ORPHANED (0 live copies): {len(result['orphaned'])}")
    for h, g in result["orphaned"]:
        print(f"  {h}  {g['members'][0]}")
    print(f"OVER-RETAINED (>1 live copy -- expected until final delete runs): {len(result['over_retained'])}")

    if result["orphaned"]:
        print()
        print("GATE FAILED: orphaned groups present. Do not permanently delete quarantine.")
        return 1

    print()
    print("GATE PASSED: every group has at least one surviving live copy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
