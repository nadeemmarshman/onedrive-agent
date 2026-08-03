# Orphan restore — 30 documents, 2026-08-03

Response to Cowork's independent re-verification of the RAID I28 quarantine
run (`COWORK_RECONCILIATION_FINDING_v1.1.md`), which found the run
appeared to have quarantined some groups' only surviving copy. Restored
30 of the 31 flagged documents; the 31st was deliberately excluded (see
below). Final permanent delete is **on hold** pending this write-up.

## What Cowork got right

The catch was genuinely valuable and the caution to pause before deleting
was exactly correct. Independently re-verified before acting on anything
Cowork's report claimed:

- All 242 of Cowork's original v1.0 groups are resolved, 581.7 MB
  reclaimed — confirmed directly on disk
- The self-nested subtree is down to 1 file / 64,746 bytes — confirmed
- The employment-dispute recording has exactly one surviving copy, at
  the correct shallow path — confirmed
- 31 documents Cowork flagged as having "no surviving copy" — the
  underlying observation (their scoped scan couldn't find a live copy)
  was accurate

## Where the diagnosis needed correcting

Cowork's root cause theory was: *"keeper selection assumed every group
had a member outside the action set... where all members were in scope,
every copy got moved."* This was checked directly and does not match
what happened.

**Definitive check, run against the raw scan data:** cross-referenced
every one of Cowork's 31 flagged `restore_to` paths against every one of
the 265 acted-on groups' `suggested_keeper` field.

**Result: 0 of 31 was ever the group's designated keeper.** The
quarantine script's `if member == keeper: continue` logic worked
correctly in all 265 groups — no group ever had its keeper moved.

The real explanation, confirmed by an independent full-tree MD5 scan
(not scoped, unlike Cowork's "two mounted roots"): **30 of the 31
documents have a byte-identical live copy sitting in a folder outside
Cowork's scanned scope** — the old top-level `Certificates\` folder,
`ShareX\`, `Unsorted\`, or a root-level file. The keeper for each of
those groups was correctly chosen and correctly preserved; Cowork's scan
simply couldn't see where it landed.

This is not a wash, though — restoring anyway was still the right call,
for a different reason (see below).

### The 31st document — not a defect at all

`CV_Superseded\CV of <third-party-3> 05112021.docx` genuinely has no
live copy, and correctly so: it was quarantined **on purpose**, after a
real content comparison, by an earlier and already-completed
reconciliation (commit `0de68ec`). That decision concluded this was the
superseded copy of a third party's document. It is excluded from this
restore because restoring it would undo a correct, already-made
decision, not fix a mistake.

## Why 30 documents were restored anyway

Even though 30 of 31 were false alarms for the narrow question "would
deleting quarantine destroy the only copy" (no — a copy already existed
elsewhere), restoring them was still correct, for a distinct reason
found while investigating:

**For the 21 `5 Certificates` documents specifically**, the surviving
live copy sits in the *old, stale, top-level* `Certificates\` folder —
not the deliberately organised `00-My Folders\2 Career Documents\
5 Certificates\` folder this same phase judged canonical earlier (Group
1 of the internal-duplicates work: numbered files, contains items the
stale folder lacks). The automated keeper-selection heuristic
(shortest absolute path wins) picked the shorter path every time — the
stale folder's path is shorter because it isn't nested under
`00-My Folders\2 Career Documents\` — silently reversing that earlier,
deliberate, content-informed judgement call. Restoring puts the
organised copy back where it belongs. The stale duplicate is
deliberately left alone rather than auto-resolved a second time; which
copy to eventually remove is a separate decision, not made here.

The remaining 9 (ShareX config-backup snapshots, one resume POE file)
were restored as the simple conservative default — no urgency, no
organisational concern, just no reason not to.

## Execution

`restore_orphaned_keepers_20260803.py`: preflighted every restoration
immediately before acting (source file exists in quarantine with
expected size; destination does not already exist — never overwrite).
Dry-run confirmed 30/30 clean before anything real moved.

**Result: 30 restored, 0 skipped, 0 errors.**

## Verification — the new standing-practice gate

Built `verify_dedup_invariants.py`, adopting the post-action re-scan both
this finding and v1.0 recommended as standing practice rather than an ad
hoc check run only when someone thinks to ask. Checks two invariants by
content hash (not path, so renamed/relocated copies are still found):
every previously-reported group has ≥1 surviving live copy (the orphan
gate), and flags (without failing) any group with >1 — expected right
now, since quarantine hasn't been permanently deleted yet.

**Gate result:** 265 groups checked, **0 orphaned**, 235 with exactly one
live copy, 30 "over-retained" (exactly the 30 just restored — each now
has both its restored live copy and its still-quarantined duplicate,
correctly, until final delete removes the latter).

Covered by `test_verify_dedup_invariants.py` — 5 tests against real temp
directories and real file content, since the tool's entire purpose is
content-hash correctness.

## The 344 vs 345 discrepancy

Already explained, not a new mystery: `_Duplicates_PendingDeletion\`
holds both `Internal_Duplicates_20260803\` (this run, 344 files) and
`CV_Superseded\` (1 file, pre-existing from the unrelated `0de68ec`
reconciliation). Any check that scans the whole `_Duplicates_
PendingDeletion\` parent — as both Cowork's and this session's orphan
checks did — sees 345. `LIVE_RUN_INTERNAL_DUPLICATES_20260803.md`
already documented this at the time.

## `.git\index.lock`

Present, 0 bytes, no `git.exe` process running (checked directly before
removing) — matches the RAID I25 pattern exactly: a stale lock left by a
process from a different concurrent session that has since exited.
Removed.

## Status

- 30 documents restored, verified in place
- Invariant gate passes: 0 orphans
- Final permanent delete of quarantine (now 315 files, ~578.3 MB after
  the restore) is **still on hold** — {{owner}}'s call, not performed here,
  same as every other delete in this project
- The keeper-selection heuristic itself (shortest-path-wins) is
  unchanged. It never moved a keeper, so the specific defensive fix
  Cowork proposed (exclude the keeper from the move set) wasn't needed —
  but the heuristic's *choice* of keeper is still naive to organisational
  intent, as the Certificates case shows. Worth deliberate improvement
  before this pattern runs against another folder; not fixed here,
  since it wasn't the cause of this near-miss.
