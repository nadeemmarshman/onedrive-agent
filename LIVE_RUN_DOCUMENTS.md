# Live Run — `{{ONEDRIVE_ROOT}}\{{DOCS}}` (phase index)

**Phase:** third live run of the Phase 1 dedup tool against real data,
after `Pictures\Camera Roll` (`LIVE_RUN_CAMERA_ROLL.md`) and
`Pictures` root (`LIVE_RUN_PICTURES_ROOT.md`).

**Dates:** 2026-07-30 (scan) → 2026-08-02 (final delete).

**Outcome:** `1. Documents` reduced from **6.5 GB / 3,084 files** to
**3.9 GB / 1,939 files** — 2.6 GB and 1,145 files permanently removed,
zero data loss, every removal either byte-identical to a surviving copy
or individually reviewed first.

This document is the phase-level index. The detailed reports it points
to were produced across **two concurrent Claude Code sessions** (see
[Session split](#session-split-dr-fork-vs-folder-dedup-fork)) and are
consolidated here so the phase reads as one piece of work.

---

## Why this phase was different

The first two live runs were same-folder, filename-suffix duplicates
(`" 1"`, `"(1)"`) — photos, low blast radius, one simple keeper rule.
This phase was not:

- **6.5 GB of financial, legal and identity documents** — {{employerA}}
  termination/{{dispute-body}} records, {{tax-authority}}, {{identity-documents}},
  {{payslip-records}}, resumes. Materially higher consequence for a wrong delete.
- **Cross-directory duplication**, not suffix pairs — a stale
  `DocFolderBackup` folder mirrored most of the live tree, and in places
  a folder had been copy-pasted into itself
  (`{{employerA}}_Termination\{{employerA}}_Termination\...`). `dedup_keeper.py`'s
  suffix-based logic did not apply at all.
- **Workstream ambiguity** — {{owner}}'s framing (2026-07-31): files
  duplicated across self-organised folder trees are not automatically
  mistakes. A duplicate may be a valid part of a workstream. This needed
  a path/workstream-level report and human judgement per group, not an
  automatic file-level rule.

That risk profile is what triggered the DR escalation below.

---

## DR escalation: from manifest snapshot to full physical backup

The closed foundational build's Decision log chose a
**manifest-snapshot-only** approach (Option A) for rollback, relying on
OneDrive's recycle bin and version history, and explicitly rejected full
file copies as overkill for that scope (RAID R6).

This phase **escalated to a full physical backup**. That is not a
contradiction of the original decision — it is a fresh proportionate
judgement for a materially different risk profile (6.5 GB of
financial/legal/ID documents with confirmed self-duplication history,
versus holiday photos recoverable from the platform's own bin).

**Backup location:** `{{DR_BACKUP_ROOT}}`
— robocopy mirror of `{{ONEDRIVE_ROOT}}\{{DOCS}}`, taken **before any
destructive action**, and deliberately on a **different physical drive**
so it survives anything done to the OneDrive tree.

**Still intact as of 2026-08-02:** 3,084 files, 6.5 GB — the complete
pre-cleanup state, unaffected by everything that followed. Every
"permanent" delete in this phase remains recoverable from it.

### Verification (three independent methods)

`verify_documents_backup.py` → `DOCUMENTS_BACKUP_VERIFICATION.json`:

| Check | Result |
|---|---|
| Source file count | 3,084 |
| Backup file count | 3,084 |
| Missing from backup | 0 |
| Extra in backup | 0 |
| MD5 hash mismatches | 0 |
| Verified byte-identical | **3,084 / 3,084** |
| **Pass** | **true** |

Confirmed three ways rather than one: robocopy's own summary, an
independent `find`/`du` count on both sides, and a full MD5 manifest
comparison of every file. The second and third exist specifically
because the first is self-reported — the same discipline that caught
RAID I22/I23 in the previous phase.

---

## RAID entries raised in this phase

| # | What | Status |
|---|---|---|
| **I24** | First robocopy attempt failed while *looking* like a normal run — Git Bash/MSYS rewrote the `/E` flag into a bogus `E:/` drive argument, so **0 files were copied**. Caught before assuming success. Fixed with `MSYS_NO_PATHCONV=1`. | Closed — fixed and independently re-verified |
| **I25** | Correction to a prior root-cause claim: a stray `.git/index.lock` had been attributed to "a sandbox quirk" without verification. Session tooling later showed **three Claude Code sessions concurrently pointed at the same working directory** — a real concurrent-process lock is far more plausible. Recorded as a documentation fix; the original doc left unedited as a historical record. | Closed — correction recorded |
| **I26** | {{owner}} could not delete a quarantine folder via File Explorer despite correct-looking steps. Two compounding causes: OneDrive's "Home" view served a **stale cached listing** for script-created folders, and a genuinely separate folder literally named `Documents` sits beside `1. Documents` at the OneDrive root, with OneDrive's UI **cosmetically stripping the numeric prefix** so both render identically. Resolved by renaming to an unmistakable name and deleting via OneDrive web search. | Closed — resolved and verified |

The common thread across I24, I25 and I26: **a tool's own report of its
state is not evidence.** Each was caught by checking actual disk state
independently, not by trusting a success message, a plausible
explanation, or a UI listing.

---

## Execution, in order

| Step | What happened | Report |
|---|---|---|
| 1. Scan | Read-only MD5 scan of all 3,084 files → 948 duplicate groups, 3.10 GB redundant | `DOCUMENTS_DEDUP_PROPOSAL.json` |
| 2. Workstream analysis | Grouped every duplicate by which top-level folders it spans, to separate wholesale-discard candidates from per-file judgement calls | `DOCUMENTS_WORKSTREAM_DEDUP_REPORT.md` |
| 3. Backup + verify | Full physical backup to `D:\`, verified three ways | `DOCUMENTS_BACKUP_VERIFICATION.json` |
| 4. Delta analysis | Isolated the files unique to `DocFolderBackup`: **1,118 duplicated / 58 unique** of 1,176 | `DOCFOLDERBACKUP_DELTA.json` |
| 5. Review queue | The 58 unique files categorised into a human-reviewable decision queue | `DOCFOLDERBACKUP_UNIQUE_FILES_REVIEW.md` |
| 6. Relocate + quarantine | 58 unique files moved out preserving original paths; remaining 1,118-file folder quarantined as a single move, then deleted (**2.6 GB reclaimed**) | `LIVE_RUN_DOCFOLDERBACKUP_QUARANTINE.md` |
| 7. Triage the 58 | Per-file decisions: 41 kept (+1 later reclassified), 15 discarded, 2 left to {{owner}} | `LIVE_RUN_DOCFOLDERBACKUP_TRIAGE.md` |
| 8. Internal duplicates | The 7 genuine duplicate groups *within* the live tree, resolved one at a time with {{owner}} | `LIVE_RUN_INTERNAL_DUPLICATES.md` |

### Final file reconciliation

3,084 files at phase start − 1,939 remaining = **1,145 removed**:

- 1,118 — `DocFolderBackup` files byte-identical to surviving live-tree copies
- 14 — discard-category files from the 58 (system noise, broken OneDrive
  pointer stubs, someone else's CV, a downloaded template, an installer,
  an unrelated PowerShell log) — each checked by opening it, not guessed
- 2 — `brochure.pdf` and a voice note, deleted by {{owner}}
- 11 — internal duplicates across the 7 groups

Reconciles exactly. Nothing unaccounted for.

---

## Session split: DR fork vs. Folder Dedup fork

This phase ran across two concurrent Claude Code sessions on the **same
working directory**, which is itself the subject of RAID I25:

- **"DR fork"** — took and verified the physical backup, raised I24 and
  I25, wrote `Handoff-Briefs/Live-Run-Handoff-Documents_v1.0.md`, then
  stood down and handed execution over. Archived 2026-07-31.
- **"Folder Dedup fork"** (this session) — the scan, workstream
  analysis, delta analysis, review queue, all relocation/quarantine/
  triage execution, the internal-duplicate groups, and I26.

A third session was found to be a dormant exact fork of the same
conversation, stalled on a superseded question, and was archived without
merging anything.

**Consolidated to a single session from 2026-07-31 onward**, on {{owner}}'s
instruction — no parallel sessions on this repo. The concurrency was not
harmless: it produced a stray `.git/index.lock`, surprise commits
appearing mid-work, and an untracked-file pileup, all reconciled rather
than ignored.

**Everything from both sessions is in this repo and on `origin/main`.**
Nothing from the DR fork lives only in a chat transcript or a local
scratchpad — that consolidation is what this index closes out.

---

## Prior art: reconciled, not ignored

An independent Cowork scan from **2026-07-08** covering part of this same
folder was found untracked in the repo during staging
(`COWORK_DUP_SCAN_FINDINGS_DOCUMENTS_v1.0.md`,
`COWORK_DUP_SCAN_GROUPS_v1.0.json`). It scanned a narrower scope
(`1. My Folders` + `{{family-member-1}}`; never `DocFolderBackup`), so it does not
conflict with this phase's findings — but it **independently found the
same `{{employerA}}_Termination` self-duplication**, which confirms that finding
was real and had simply sat unactioned for three weeks. Committed rather
than deleted, as evidence of the gap between detection and action.

---

## Artefacts

**Reports** — `LIVE_RUN_DOCFOLDERBACKUP_QUARANTINE.md`,
`LIVE_RUN_DOCFOLDERBACKUP_TRIAGE.md`, `LIVE_RUN_INTERNAL_DUPLICATES.md`,
`DOCUMENTS_WORKSTREAM_DEDUP_REPORT.md`,
`DOCFOLDERBACKUP_UNIQUE_FILES_REVIEW.md`

**Data** — `DOCUMENTS_DEDUP_PROPOSAL.json`,
`DOCFOLDERBACKUP_DELTA.json`, `DOCUMENTS_BACKUP_VERIFICATION.json`

**Scripts** — `scan_documents_dedup.py`,
`generate_workstream_dedup_report.py`,
`analyze_docfolderbackup_delta.py`, `verify_documents_backup.py`,
`relocate_docfolderbackup_unique_files.py`,
`quarantine_docfolderbackup_wholesale.py`,
`triage_docfolderbackup_unique_files.py`

**Handoff** — `Handoff-Briefs/Live-Run-Handoff-Documents_v1.0.md`

**Prior art** — `COWORK_DUP_SCAN_FINDINGS_DOCUMENTS_v1.0.md`,
`COWORK_DUP_SCAN_GROUPS_v1.0.json`

---

## Open items

- **Six `(from DocFolderBackup)`-suffixed files** in
  `{{hobby-records}}\{{hobby-activity}}\308 {{calibre-1}}\` — older versions of
  actively-evolving reload notes, deliberately not overwritten. {{owner}} to
  compare each pair and drop whichever is stale.
- **Two `CV of {{third-party-3}} 05112021` versions** consolidated into one
  folder, different content — same call to make.
- **`{{DR_BACKUP_ROOT}}`** (6.5 GB) still on disk.
  Worth keeping until the above are settled; then it can go.
