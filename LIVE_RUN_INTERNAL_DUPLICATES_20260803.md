# Internal duplicates — 265 groups quarantined, 2026-08-03

Execution of the 266-group rescan (`DOCUMENTS_DEDUP_RESCAN_20260803.md`,
RAID I28) — the corrected picture after the classifier fix, and the
follow-up to Cowork's reconciliation finding that 238 previously-known
groups had never been actioned.

## Result

| | Value |
|---|---|
| Groups actioned | **265** of 266 |
| Groups excluded | 1 (0-byte false positive, see below) |
| Files moved to quarantine | **344** |
| Space reclaimable on final delete | **590.9 MB** |

## The excluded group

One group of four files was excluded deliberately: `Default.rdp`, two
NetBeans build artifacts, and a `.write_test` marker — all 0 bytes. They
are byte-identical only because they are empty, not because they are
actual duplicates of each other in any meaningful sense. Same judgement
this project made on zero-byte groups earlier in the live-run programme.

## Headline result: the self-nested subtree

The `{{employerA}}_Termination\{{employerA}}_Termination\` self-nested subtree — flagged
repeatedly across this whole phase (`DOCUMENTS_WORKSTREAM_DEDUP_REPORT.md`,
`COWORK_RECONCILIATION_FINDING_v1.0.md`, RAID I28) — went from **42 files
/ ~500 MB down to 1 file / 100 KB**. Nearly everything in it was a
duplicate of a file already present elsewhere in the live tree; the one
remaining file is genuinely unique.

The three copies of the 234.2 MB employment-dispute recording, which
alone accounted for 79% of all reclaimable space, are resolved: one
keeper remains at its shallow, non-nested path; both nested copies are
in quarantine.

## Execution

`quarantine_documents_internal_duplicates_20260803.py`:

1. Loaded the 266-group rescan, excluded the one 0-byte group
2. **Preflighted every candidate file immediately before moving it** —
   re-checked existence and exact size against the live filesystem, not
   against the scan's memory of it. Dry-run first, against the same
   preflight logic, confirmed 344/344 candidates still matched with zero
   skips before any file was touched for real.
3. For each group, the keeper (shortest-path suggestion — the
   non-self-nested copy, in the headline case) stays in place; every
   other member moves into
   `_Duplicates_PendingDeletion\Internal_Duplicates_20260803\`,
   preserving its full relative path from `1. Documents\` so provenance
   is never lost and no name collision is possible.

No staging step was needed, unlike the DocFolderBackup phase — these are
all live-tree files with no reorganised destination to guess at, so
relative-path preservation is both correct and sufficient on its own.

## Verification

Independently re-checked on disk after the move, not just the script's
own printed summary:

- Quarantine folder: **344 files, 592 MB** (matches expected exactly)
- Headline `.wav` group: keeper present at its original shallow path
  (245,618,212 bytes), both other copies present in quarantine at the
  same size
- Self-nested subtree: down to 1 file, 100 KB
- `_Duplicates_PendingDeletion` also holds `CV_Superseded\` (1 file) —
  pre-existing, from an earlier, unrelated reconciliation task; not part
  of this run, noted here only to explain the folder's total count

## Safety net

`{{DR_BACKUP_ROOT}}` still holds every file's
pre-cleanup state. Nothing here is a permanent delete — this is a move,
reversible via Recycle Bin or that backup.

## Open item

Final permanent delete of
`_Duplicates_PendingDeletion\Internal_Duplicates_20260803\`
(344 files, 590.9 MB). Per RAID I26, delete via **OneDrive web** rather
than local File Explorer.

This closes RAID I28's outstanding action item and Cowork's reconciliation
finding — all 265 real groups from the corrected scan are now resolved to
the quarantine stage.
