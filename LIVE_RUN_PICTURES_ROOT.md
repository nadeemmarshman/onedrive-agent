# Live run report -- 2026-07-31

Target: `OneDrive\Pictures` root (top-level files only -- `Camera Roll` and
`Screenshots` are separate subfolders, out of scope for this run, each
handled/to-be-handled as their own phase).

Files scanned: 6,426
Duplicate groups (identical content, MD5): 477
Duplicate files quarantined: 478 (one group had 2 duplicates against a
single keeper; the rest had 1 each)
Reclaimed space (moved out of the active folder, not yet deleted): 98.7 MB

Script: `quarantine_pictures_root_dedup.py`. Same approach as the Camera
Roll phase: read-only detection, then a reversible quarantine-move into
`_Duplicates_PendingDeletion\` rather than a direct delete -- final
delete stays a separate, human-initiated step.

## Defect found and fixed: incomplete conflict-copy detection (RAID I22)

The keeper-selection fix built for Camera Roll (RAID I21) only recognized
OneDrive's `" 1"` (space, no parens) sync-conflict suffix. This folder's
477 groups include 32 that use a second convention in the same OneDrive
account -- `"name (1).jpg"` (parenthesized) -- which the original check
didn't recognize at all. Those 32 fell through to arbitrary scan order,
which happened to be alphabetical, and `"(1)"` sorts before `"."`
alphabetically -- so the conflict copy was picked as keeper in **all 32
cases**, backwards from intent.

Caught by diffing the full run output against actual on-disk state, not
by trusting the printed summary. All 32 pairs were individually swapped
back (MD5-verified identical before acting), and the fix itself was
generalized: the keeper-selection logic was pulled out of three
duplicated per-script copies into one shared module, `dedup_keeper.py`,
with a regex that covers both suffix styles (`" 1"` and `"(1)"`). Every
one of the 478 groups in this run was then re-verified against the
corrected logic -- 0 mismatches.

## Second issue found during the fix (RAID I23)

While manually swapping the 32 pairs back, one pair
(`IMG_20180207_215045.jpg` / `IMG_20180207_215045 (1).jpg`) ended up with
both copies left in quarantine and neither in root, despite the swap
script reporting success. Caught by the same full verification pass, not
assumed fixed from the script's own output. MD5-confirmed identical, then
manually restored. Root cause not conclusively identified (see RAID I23
-- logged as Monitoring, not Closed, since the cause is unconfirmed).

## Final verified state

- Root: 5,948 files
- `_Duplicates_PendingDeletion\`: 478 files
- 5,948 + 478 = 6,426 -- matches the original scan total exactly; nothing
  lost or duplicated overall
- All 478 groups re-checked individually against the corrected
  keeper-selection logic after the fix: 0 mismatches

## What's still true from the Camera Roll phase

Nothing here is fixed in `tools.py` itself -- `propose_action()`'s
underlying arbitrary `group[0]` selection is unchanged (Backlog #15
still covers the proper fix). This live-run phase's own workaround
(`dedup_keeper.py`) is now more complete than the Camera Roll one it
started from, but it's still a call-site workaround, not a Phase 1 code
change.
