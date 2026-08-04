# Internal Duplicates — 7 groups, resolved (2026-08-02)

Resolved all 7 genuine internal-duplicate groups found in the live `1. Documents` tree (separate from DocFolderBackup work). These were files duplicated *within* the organized folder structure, not backups.

## Summary

| # | File(s) | Size | Type | Kept | Quarantined |
|---|---------|------|------|------|-------------|
| 1 | {{education-body}} certificate photo | 2.2 MB | duplicate across folder schemes | `00-My Folders\2 Career Documents\5 Certificates\...` | `Certificates\{{education-body}}_Grade12\...` |
| 2 | Handoff doc (Agent→JobSearch) | 8 KB | shared between projects | `JobSearchProject\Handoff Briefs\...` | `JobPrepApp\...` |
| 3 | Handoff doc (Post-Closure) | 6.2 KB | shared between projects | `OneDrive-Agent\Handoff-Briefs\...` | `JobSearchProject\Handoff Briefs\...` |
| 4 | README.png | 245 KB | shared between referral packs | `SilverBullet(NetworkPack)\...` | `ProgrammeMan_Referral pack\...` |
| 5 | Profile pics (C.png, F.png) | 3.2 MB | variant drafts | — | Both quarantined |
| 6 | Profile pics (E.png, I.png) | 3.8 MB | variant drafts | — | Both quarantined |
| 7 | {{employerA}} Certificate of Service | 4×63.7 KB | working copies | `{{employerA}}_Termination\...` (root) | 3 copies across {{dispute-body}}_Appeal, self-nested folder, {{employerA}}_Correspondence |

## Decision reasoning

**Groups 1–4:** Each had a clear canonical location (organized structure, project owner, referral pack creator, root folder). Copies were working/reference duplicates kept for convenience.

**Groups 5–6:** Two sets of identical profile picture variants with single-letter names (C/F, E/I). No distinguishing metadata or naming convention. User chose to quarantine all — keeps the folder clean; originals can be found via Recycle Bin if needed.

**Group 7:** Legal termination document copied into 3 working locations during {{dispute-body}} appeal process. Root of {{employerA}}_Termination is canonical; appeal-process copies are obsolete.

## Files quarantined

All moved to `_Duplicates_PendingDeletion\Internal_Duplicates\` with original folder structure preserved:

```
_Duplicates_PendingDeletion\Internal_Duplicates\
├── Certificates\{{education-body}}_Grade12\
│   └── {{education-certificate}}0.jpg
├── 01-AI-Project-Portfolio\
│   ├── JobPrepApp\
│   │   └── Handoff_Brief_OneDrive_Agent_to_JobSearch_2026-07-20.md
│   └── JobSearchProject\
│       ├── Handoff Briefs\
│       │   └── Handoff_Brief_Post_Closure_Open_Items.md
│       └── ProgrammeMan_Referral pack\
│           └── README.png
└── 00-My Folders\
    └── 2 Career Documents\
        ├── Profile Pics & Templates\
        │   ├── C.png
        │   ├── E.png
        │   ├── F.png
        │   └── I.png
        └── 4 Employment Companies\{{employerA}}\{{employerA}}_Termination\
            ├── {{dispute-body}}_Appeal\
            │   ├── {{employerA}} Certificate of Service - {{owner}} ({{employee-ref}}) - Copy.pdf
            │   └── {{employerA}}_Correspondence\
            │       └── {{employerA}} Certificate of Service - {{owner}} ({{employee-ref}}).pdf
            └── {{employerA}}_Termination\
                └── {{employerA}} Certificate of Service - {{owner}} ({{employee-ref}}).pdf
```

**Total quarantined: 11 files across 7 groups, 9.37 MB.**

> **Correction (2026-08-02).** The commit message for this work
> (`4321830`) states "~3.5 MB across 13 files". Both figures are wrong —
> the true totals are **11 files, 9.37 MB**, derived by summing the
> per-group byte counts from `DOCUMENTS_DEDUP_PROPOSAL.json` and
> independently confirmed by whole-folder file-count reconciliation
> (3,084 files at phase start − 1,939 after = 1,145 removed;
> 1,118 DocFolderBackup duplicates + 14 discard + 2 unidentified +
> **11** internal = 1,145 exactly). The commit message is left as-is —
> git history is not rewritten — and corrected here instead, following
> the same "correct the record, don't rewrite it" pattern as RAID I25.

## Safety net

Verified full physical backup independent of this action:
`{{DR_BACKUP_ROOT}}` (3,084/3,084 files, MD5-verified identical, RAID I24)

## Final delete (2026-08-02, by {{owner}})

`_Duplicates_PendingDeletion\` (containing `Internal_Duplicates\`) and the
emptied `_DocFolderBackup_Unique_Files_ToReview\` scaffolding both
permanently deleted, Recycle Bin emptied.

Verified independently on disk afterwards: neither folder exists, no
underscore-prefixed working folders remain in `1. Documents`, and every
Group 1-7 keeper plus the reclassified {{third-party-3}} CV folder confirmed
still present at its intended path.

## Status

**Complete.** All 7 groups resolved and permanently deleted.
