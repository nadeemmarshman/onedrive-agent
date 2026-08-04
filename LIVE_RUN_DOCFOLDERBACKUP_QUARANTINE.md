# DocFolderBackup — wholesale quarantine, 2026-07-31

Executed the two-step plan from `DOCFOLDERBACKUP_UNIQUE_FILES_REVIEW.md`,
per {{owner}}'s direction to relocate now and triage individual keep/discard
decisions on the 58 unique files later.

## Step 1: relocate the 58 unique files

`relocate_docfolderbackup_unique_files.py` moved all 58 files
(DOCFOLDERBACKUP_DELTA.json's `unique_file_list`, 496.6 MB) out of
`DocFolderBackup` into `{{ONEDRIVE_ROOT}}\{{DOCS}}\_DocFolderBackup_Unique_Files_ToReview\`,
preserving each file's original relative path exactly (no guessed
remapping to the live tree's current, reorganized folder structure --
`1. My Folders` became `00-My Folders` at some point, and other folders
moved too, so any automatic remap would have been a guess, not a fact).

Verified: 58 files in the staging folder, `DocFolderBackup` down to
1,118 files (1,176 - 58), matching the delta analysis exactly.

**Still open:** {{owner}} triages `_DocFolderBackup_Unique_Files_ToReview\`
later -- decide each file's real home in the live tree, or that it's not
worth keeping after all, per the categorized recommendations already in
`DOCFOLDERBACKUP_UNIQUE_FILES_REVIEW.md`.

## Step 2: quarantine the rest wholesale

`quarantine_docfolderbackup_wholesale.py` moved the entire, now-reduced
`DocFolderBackup` folder (1,118 files, all confirmed byte-identical
duplicates of live-tree content) into
`_Duplicates_PendingDeletion\DocFolderBackup\` as a single folder-move,
rather than 1,118 individual file moves.

Verified after the move:
- `DocFolderBackup` no longer exists at its original path
- `_Duplicates_PendingDeletion\DocFolderBackup\` contains 1,118 files
- `_DocFolderBackup_Unique_Files_ToReview\` still holds its 58 files, untouched by step 2

## Safety net

A verified full physical backup of the pre-quarantine state already
exists independently of this action:
`{{DR_BACKUP_ROOT}}` (3,084/3,084 files, MD5-verified
identical, RAID I24). Nothing here is a permanent delete -- both moves
are reversible.

## Final delete (2026-07-31, by {{owner}})

`_Duplicates_PendingDeletion\DocFolderBackup\` (1,118 files, 2.6 GB)
permanently deleted by {{owner}} via File Explorer, Recycle Bin emptied.
Verified after the fact: the folder no longer exists on disk, the
`_Duplicates_PendingDeletion` parent folder remains (now empty),
`_DocFolderBackup_Unique_Files_ToReview\` (58 files) untouched, and
`1. Documents` total size dropped from 6.5 GB to 4.0 GB -- matching the
2.6 GB expected exactly. The independent full backup
(`{{DR_BACKUP_ROOT}}`) still exists regardless, as a
separate safety net outside this folder entirely.

## What this doesn't cover yet

- The 58 staged files in `_DocFolderBackup_Unique_Files_ToReview\` still
  need real triage (keep-and-relocate vs. discard) -- unaffected by the
  delete above
- The ~7 genuine internal-duplicate groups found in the earlier live-tree
  scan (certificate photo, handoff-brief doc, README.png, profile pics,
  {{employerA}} certificate PDF) are unrelated to DocFolderBackup and still open
