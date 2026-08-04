# Documents rescan — post-fix, 2026-08-03

Re-run of `scan_documents_dedup.py` against the live `1. Documents` tree
after the RAID I28 classifier fix, requested to establish current numbers
before acting on the 238 groups Cowork had already identified.

**Scope difference from the original scan:** `DocFolderBackup` no longer
exists on disk (quarantined and permanently deleted during the DocFolderBackup
phase), so this scan sees a smaller, purely live tree — 1,933 files, down
from the original 3,084. Every group below is therefore
`internal_duplicate_in_live_tree`; there is no backup side left to mislabel
against, so the classifier's multi-label fix isn't exercised by this
particular rescan the way it would be on a tree that still had a backup
folder. It's still the correct scan to run: it's what's actually on disk
now.

## Result

| | Value |
|---|---|
| Files scanned | 1,933 |
| Duplicate groups | 266 |
| Total reclaimable | 590.9 MB |
| Groups >1 MB reclaimable | 27 |

Matches Cowork's independent estimate (590.7 MB) closely — the small
difference is scope (Cowork checked two roots against its original 242
groups; this is a fresh full-tree scan).

## Top 15 by reclaimable space

| Reclaimable | Copies | File |
|---|---|---|
| 468.5 MB | 3 | `{{hearing-recording}}.wav` |
| 13.2 MB | 3 | `Statement_N_{{surname-redacted}}.pdf` |
| 9.8 MB | 4 | `D_{{suspension-notice}} 1stNov2019.pdf` |
| 8.8 MB | 4 | `F_{{union}}Agreeement9thDec2019.pdf` |
| 6.5 MB | 4 | `C_{{warning-appeal}} 4thOct2019.pdf` |
| 5.4 MB | 2 | `LSS GB Experience.pptx` |
| 4.6 MB | 3 | `agile-edx_A_context.pdf` |
| 4.4 MB | 2 | `knockout-target.pdf` |
| 2.3 MB | 2 | `{{competency-form}}_CompetanceCert_AllTypes.pdf` |
| 2.2 MB | 2 | `IMG_20241030_094042.jpg` |
| 2.1 MB | 2 | `{{school}}ProficiencyExamReport.jpg` |
| 2.0 MB | 2 | `Game extended Samsung washing machine warrantee.pdf` |
| 1.8 MB | 2 | `A(b)_LoanAgreement.pdf` |
| 1.6 MB | 4 | `B_{{employerA}}RequestforWarningAppeal 3rdOct2019.pdf` |
| 1.6 MB | 4 | `E_{{disciplinary-enquiry-notice}} 2ndDec2019.pdf` |

The headline item is unchanged from Cowork's finding: the three live-tree
copies of the employment-dispute recording, at 234.2 MB each, account for
79% of all reclaimable space on their own.

## Status

Read-only. Nothing moved, deleted or renamed by this scan. Full 266-group
detail with real paths written to `_raw_local_only/DOCUMENTS_DEDUP_PROPOSAL_20260803.json`
(gitignored), same convention as `COWORK_RECONCILIATION_REMAINING_v1.0.json`.

Acting on these — including the 238 already identified by Cowork, which
substantially overlap this list — is still {{owner}}'s call to sequence,
per RAID I28.
