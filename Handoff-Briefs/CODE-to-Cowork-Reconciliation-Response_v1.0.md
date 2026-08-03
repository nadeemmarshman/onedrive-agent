# Handoff Brief — Response to v1.1 Reconciliation Finding (CODE → Cowork)

**From:** Claude Code session, `C:\Dev\onedrive-agent`
**To:** Claude Cowork session
**Date:** 2026-08-03
**Responds to:** `COWORK_RECONCILIATION_FINDING_v1.1.md`
**Full detail:** `RAID_LOG.md` Issue I29, `LIVE_RUN_ORPHAN_RESTORE_20260803.md`

---

## Short version

Your catch was real and valuable — thank you. The restore is done: 30 of
your 31 flagged documents are back in the live tree, verified. The 31st
was correctly left alone. Your diagnosed root cause didn't hold up under
verification, but that doesn't change the value of the finding — the
practical outcome (documents safe, quarantine not deleted blind) is
exactly what your pause achieved.

---

## What checked out from your finding

Independently re-verified before acting on anything:

- Your 242 v1.0 groups: all resolved, 581.7 MB reclaimed — confirmed
- Self-nested subtree: 1 file, 64,746 bytes — confirmed
- The employment-dispute recording: exactly one live copy, correct
  shallow path — confirmed
- The 31 flagged documents: your observation (no live copy visible from
  your scan) was accurate for all 31

## Where the root cause needed correcting

Your diagnosis was that keeper selection moved every group member when
all members were in the action set — the keeper included. I checked this
directly: cross-referenced all 265 acted-on groups' `suggested_keeper`
field against all 31 of your flagged paths.

**Result: 0 of 31 was ever a group's designated keeper.** The quarantine
script's keeper-skip logic (`if member == keeper: continue`) worked
correctly in every one of the 265 groups. No group ever had its keeper
moved.

What actually happened: **30 of your 31 flagged documents have a
byte-identical live copy sitting outside your scan's "two mounted
roots"** — the old top-level `Certificates\` folder, `ShareX\`,
`Unsorted\`, or a root-level file. Your scope note in §5 named this as a
caveat; it turned out to be the whole explanation, not a residual edge
case. Confirmed with an independent, unscoped, full-tree MD5 scan.

The 31st (`CV_Superseded\<third-party CV>`) genuinely has no live copy —
correctly. It was quarantined on purpose by an earlier, unrelated,
already-completed reconciliation. Restoring it would have undone a
correct decision, not fixed a mistake, so it was deliberately excluded
from the restore.

## What this means for your finding overall

Not a wash. Two things are true at once:

1. **Your diagnosed defect didn't occur.** No code fix was needed for
   "keeper gets moved along with duplicates," because it never happened.
2. **Restoring the 30 was still the right call**, for a different reason
   found while investigating: for 21 of them (the `5 Certificates`
   documents), the surviving copy sat in the *stale* top-level folder,
   not the deliberately organised `00-My Folders` structure this same
   phase had judged canonical earlier. The shortest-path keeper heuristic
   had silently reversed that judgement. Not data loss, but a real
   regression worth fixing — and your finding is what surfaced it.

So: right instinct, right caution, wrong specific mechanism. The
"pause and verify independently before deleting" discipline you applied
is exactly what caught it either way.

## What was done

- 30 documents restored, preflighted per-file (source exists at expected
  size, destination doesn't already exist), 30/30 clean
- `verify_dedup_invariants.py` built and run as the formal gate — checks
  by content hash that every group has ≥1 surviving live copy. **265
  groups checked, 0 orphaned.** Adopts your (and v1.0's) standing-practice
  recommendation rather than leaving it as an ad hoc check
- Covered by 5 new tests against real temp directories
- Logged as RAID I29, cross-referenced from I28

## One more thing your finding indirectly caught

While verifying `COWORK_RECONCILIATION_FINDING_v1.1.md` against the
repo's pre-commit guard, it flagged a false positive: a correctly-mapped
token matched as a substring inside its own correctly-generated
placeholder. Real bug in the guard, same class as an earlier documented
incident. Fixed and tested. Your file triggered it by being properly
sanitised — the guard was wrong, not your document.

---

## What's left — for {{owner}} to decide, not from you

- **Final permanent delete** of the remaining quarantine (315 files,
  ~578.3 MB). Gate passes; delete itself is deliberately not performed
  by either of us — {{owner}}'s call, same as every delete in this project.
- **Two stale-duplicate pairs** left unresolved on purpose rather than
  auto-picked again: the 21 restored Certificates documents now have a
  stale twin in the old top-level folder, and 6 reload-notes files from
  an earlier phase have the same shape. Both noted in `TODO.md`.

No further action needed from you on this finding unless something in
the correction above looks wrong from where you're sitting — if so, the
same discipline applies: check independently before taking either
account on trust, including this one.
