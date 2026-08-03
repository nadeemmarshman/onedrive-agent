# DocFolderBackup — 58 unique files, triaged (2026-07-31)

Full per-file triage of the review queue (`DOCFOLDERBACKUP_UNIQUE_FILES_REVIEW.md`),
executed by `triage_docfolderbackup_unique_files.py`. Result: **41 Keep, 15
Discard (quarantined, not deleted), 2 Leave (still need {{owner}}'s input)** --
verified to total 58 both before execution (decision map checked against
`DOCFOLDERBACKUP_DELTA.json`) and after (file counts at every destination).

## Keep — 41 files relocated into `00-My Folders`

Placed only into folders that already existed in the live tree -- no new
folders invented to force a placement. Categories: ID documents, resume
photos, career/resume documents, employment records/<<payslip-record>-records>, the two
<employerA> termination archives (contents not inspected -- still worth opening
before relying on them), <household-records> warranty photos, <hobby-records>
reload documentation.

### Collision handling (6 files)

Six files in `<hobby-records>\<hobby-activity>\308 <calibre-1>\` collided
with same-named files already in the live tree. Since
`DOCFOLDERBACKUP_DELTA.json` had already confirmed these backup copies
have **no byte-identical match anywhere**, a same-named file at the
destination must be genuinely different content -- an older draft of an
actively-evolving reload-notes folder, not a duplicate. Never overwritten;
each suffixed `(from DocFolderBackup)` instead, so both versions exist
side by side:

- `0. <calibre-1>_Case_Prep (from DocFolderBackup).docx`
- `1.0 Summery_<calibre-1>_<ammunition-brand> 180gr_N540_Reload (from DocFolderBackup).docx`
- `1.1 <ammunition-brand> 180gr_N540_Reload_Detail (from DocFolderBackup).docx`
- `10. Reloading<calibre-1>ConsolidatedDocument (from DocFolderBackup).docx`
- `3.0 Detailed_<calibre-1>_<ammunition-brand> 168gr_N140_Reload (from DocFolderBackup).docx`
- `<calibre-1> Reload Data (from DocFolderBackup).xlsx`

**Reconciled 2026-08-03.** All 6 pairs compared by actual content, not
just filename/date -- `.docx` files via extracted document text
(similarity ratio + diff of the differing spans), the `.xlsx` via sheet
names and shared-string sets.

Result was consistent across all 6, without exception:

- Every backup copy is dated 2025; every live copy is dated **February
  2026** -- the live tree kept moving after the backup snapshot
- Content similarity ranged 82%-99%, and in every case the divergence was
  the live version **adding** material (expanded explanations, extra
  sections, more precise data) rather than contradicting or replacing the
  backup with something unrelated
- No pair showed the backup holding information absent from live

Conclusion: this is one actively-evolving document per pair, not two
diverging versions. Nothing worth merging back -- the live version
already is the backup version, continued.

All 6 backup copies quarantined (not deleted) to
`_Duplicates_PendingDeletion\Reload_Notes_Superseded\`, same reversible
pattern as the rest of this project. Final delete is {{owner}}'s call.

## Discard — 15 files quarantined (not deleted)

Moved to `_DocFolderBackup_Discard_ToReview\` (mirrors the folder
structure they came from). Reasons, each checked rather than assumed:

- **7 `desktop.ini`** -- folder-view marker files, no content
- **4 `.collection` files** -- opened and read: each is a small JSON
  pointer to a OneDrive item ID, not the actual image/content itself
- **`CV of <third-party-3> 05112021.docx`** -- not {{owner}}'s own document
- **`Business-Analyst-Resume-Example-Free-Download.zip`** -- a downloaded
  template, not personal content
- **`<vendor-diagnostic-tool>`** -- a software installer,
  not personal content
- **`new 2.txt`** -- opened and read: a copy-pasted PowerShell/wsreset
  troubleshooting log, unrelated to personal documents

Final delete of this folder is {{owner}}'s call, same pattern as every
other quarantine step in this project.

## Leave — 2 files, resolved by {{owner}} (2026-08-02)

Both deleted directly by {{owner}} via File Explorer/Recycle Bin, without
further identification:

- `brochure.pdf` -- deleted
- `20 Mar, 11.46​.m4a` -- deleted

## One Discard reclassified as Keep (2026-08-02)

{{owner}} reviewed the discard list and asked to keep
`CV of <third-party-3> 05112021.docx` after all. Moved (not from the
original discard batch, but pulled out before final delete) into a new
folder: `2 Career Documents\1 CurrentResume\CV of <third-party-3> 05112021\`.

A second, different-content file with the same name already existed at
`1 CurrentResume\5. ResumeResources\CV of <third-party-3> 05112021.docx`
(confirmed via MD5 -- different hash, genuinely a different version).
Consolidated both into the new folder rather than leaving one stranded,
suffixing the second `(from ResumeResources)` so neither was overwritten:

```
2 Career Documents\1 CurrentResume\CV of <third-party-3> 05112021\
├── CV of <third-party-3> 05112021.docx                        (ex-DocFolderBackup)
└── CV of <third-party-3> 05112021 (from ResumeResources).docx  (ex-5. ResumeResources)
```

{{owner}} should compare the two and decide if one is stale.

## Remaining 14 discard files: permanently deleted (2026-08-02)

Final delete took several attempts due to a real OneDrive/File Explorer
naming collision, not a technical failure -- worth recording since it
cost significant back-and-forth:

- OneDrive's newer "Home" view in File Explorer shows a curated/cached
  folder listing that does not reliably reflect folders created via
  script (outside Explorer's own file-operation hooks) -- it repeatedly
  failed to show the discard folder at all, even after a direct
  full-path navigation and a refresh
- Separately, and unrelated to the above: `1. Documents` and a second,
  genuinely different, unrelated folder literally named `Documents`
  both exist as siblings at the OneDrive root -- confirmed via
  PowerShell `Get-ChildItem` (byte-exact name check, no hidden
  characters). OneDrive's UI cosmetically strips numeric prefixes from
  some special/pinned folders for display (`1. Documents` renders as
  `Documents`; `2. Desktop` renders as `Desktop`), which made it
  impossible to tell the two `Documents`-labelled folders apart from
  the UI alone -- {{owner}} repeatedly ended up deleting an already-empty
  folder (`_DocFolderBackup_Unique_Files_ToReview`, harmless) instead of
  the real target
- Resolved by renaming the target folder to
  `ZZZ_DELETE_THIS_FOLDER_14_FILES` (an unmistakable name) and locating
  it via OneDrive web's search/Recycle Bin rather than local Explorer
  navigation, which uses real folder paths, not the cosmetic display
  layer
- Verified via OneDrive web Recycle Bin (`Deleted: Just now`, origin
  `My Files > 1. Documents`) and independently re-verified on the local
  filesystem after sync: folder no longer exists, `1. Documents` total
  size unaffected (14 tiny files, no meaningful size change expected or
  observed)

## Verification

- Decision map checked against `DOCFOLDERBACKUP_DELTA.json`'s 58-entry
  `unique_file_list` before any file was moved -- exact match, no
  missing/extra entries
- Every KEEP destination folder confirmed to already exist in the live
  tree before execution
- Script built resumable (skips already-moved files) after the first run
  halted safely on the first real collision rather than overwriting
- Post-execution counts verified directly on disk: 2 in staging, 15 in
  discard, matching 58 total exactly
