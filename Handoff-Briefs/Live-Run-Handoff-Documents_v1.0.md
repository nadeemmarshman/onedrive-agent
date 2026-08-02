# OneDrive AI Agent — Live Run Handoff Brief (Documents folder phase)

**Purpose of this document:** Context handoff for the live-run phase against `OneDrive\1. Documents`, written so any Claude session (or Cowork) picking this up has the background without re-deriving it. Same purpose and convention as `Live-Run-Handoff_v1.0.md` (Camera Roll/Pictures root phase), kept as a separate document because this phase has a materially different risk profile and duplication pattern.

**Current version: v1.0**

**Acronyms:** as defined in `GLOSSARY.md` in the repo.

---

## Relationship to the existing project

Not a continuation of the closed foundational build
(`Handoff-Briefs/AI-Agent-Build-Handoff_v9.2.md`, Phases 1-8, signed off
2026-07-20) or of the Camera Roll/Pictures-root live-run phase
(`Live-Run-Handoff_v1.0.md`). Read those first for background this
document assumes.

## Why this phase has its own document

The Camera Roll and Pictures-root live runs were same-folder,
filename-suffix duplicates (`" 1"`, `"(1)"`) — low blast radius (photos),
simple keeper rule. This phase is materially different:

- **6.5 GB, 3,084 files** of financial, legal, and identity documents
  (<employerA> termination/<dispute-body> records, <tax-authority>, <identity-documents>,
  <<payslip-record>-records>, resumes) — much higher consequence if something is deleted
  wrongly than a duplicate holiday photo.
- **Cross-directory duplication**, not same-folder suffix pairs —
  `DocFolderBackup` mirrors most of the live tree from a different
  top-level folder entirely, and some duplication is a folder
  copy-pasted into itself (`<employerA>_Termination\<employerA>_Termination\...`).
  `dedup_keeper.py`'s suffix-based logic doesn't apply here at all.
- {{owner}}'s framing (2026-07-31): duplicate files across different
  **workstreams** (self-organized folder trees built up over time) are
  not automatically mistakes — a duplicate might be a still-valid part
  of a workstream, not clutter. This needs a path/workstream-level
  report and human judgment per pair, not an automatic file-level rule.

## Decision log

### Decision: DR/rollback approach for this phase — full physical backup, not the original project's Option A

The closed foundational build's Decision log
(`AI-Agent-Build-Handoff_v9.2.md`, Decision log entry 5) chose
**Option A: manifest snapshot** (`pre_run_snapshot.json`) over **Option
B: full file backup**, explicitly relying on OneDrive's built-in recycle
bin and version history (30-180 days) as the primary recovery mechanism
(RAID R6, `TEST_STRATEGY.md` §5.7). That decision was scoped to that
project's Phase 5 approval-gate test runs against small, disposable test
beds.

**This phase escalates beyond that decision**, at {{owner}}'s explicit
request (2026-07-31): a full physical backup of the entire
`OneDrive\1. Documents` folder to `D:\` before any quarantine/delete
action runs, in addition to (not instead of) the existing quarantine
pattern.

**Why the escalation is justified, not a contradiction of the original
decision:** the original Option A vs B trade-off explicitly weighed
"proportionate to the project's actual risk profile" — a risk profile
built around small test beds and, at largest, a personal photo folder.
This phase's actual folder is 6.5 GB of financial/legal/ID documents
with a confirmed history of accidental self-duplication
(`<employerA>_Termination\<employerA>_Termination`) already found once by this same live
run (see `LIVE_RUN_PICTURES_ROOT.md`-equivalent findings for this
folder). The cost of Option B (storage, time) is trivial here (256 GB
free on `D:`, ~15 seconds to copy) relative to the cost of getting a
keeper-selection or quarantine decision wrong on an ID document or a
legal record. Proportionate risk-based judgement, applied fresh to a
different risk profile, not a departure from the original decision's
own reasoning.

**Backup taken:** `robocopy` mirror of `<ONEDRIVE_ROOT>\1.
Documents` to `<DR_BACKUP_ROOT>`, `/E /COPY:DAT`
(subdirectories including empty ones; data+attributes+timestamps, no
security/owner metadata — irrelevant for a single-user DR copy).

**First attempt failed harmlessly** — see RAID I24: Git Bash's
auto path-conversion rewrote the `/E` flag into a bogus `E:/` drive
argument before robocopy saw it; robocopy errored out immediately
(`Invalid Parameter #3`), 0 files copied. Caught from the log, not
assumed successful. Retried with `MSYS_NO_PATHCONV=1` prefixed to the
command, which succeeded.

**Verification:** see "Backup verification" below — full MD5 manifest
comparison, not just count/size, matching the same rigor as the
foundational build's CP1/CP2/CP3 checkpoint manifests
(`TEST_BED_AND_CASES.md` v2.0 §8).

## Backup verification

Two independent checks, not one, before this backup was considered done:

**Check 1 — robocopy's own summary** (immediately after the copy):
3,084/3,084 files, 6.42 GB, 0 Failed, 0 Mismatch (per `robocopy_backup_log.txt`).

**Check 2 — independent `find`/`du` count** (not trusting robocopy's own
self-report alone): 3,084 files, 6.5 GB on both source and destination,
matching exactly.

**Check 3 — full MD5 manifest comparison** (`verify_documents_backup.py`):
every file on both sides hashed individually (not sampled), keyed by
relative path, and diffed:

| Metric | Result |
|---|---|
| Source files | 3,084 |
| Backup files | 3,084 |
| Missing from backup | 0 |
| Extra in backup (unexpected) | 0 |
| Hash mismatches | 0 |
| Verified byte-identical | 3,084 |
| **Overall result** | **PASS** |

Full per-file detail in `DOCUMENTS_BACKUP_VERIFICATION.json`. Verified
2026-07-31, same session as the backup itself, before any quarantine
step in this phase was permitted to run.

---

## Prior art found mid-phase, not yet reconciled

While staging this phase's files for commit, two pre-existing untracked
files were found already sitting in the repo (present before this phase
began, not created by it):

- `COWORK_DUP_SCAN_FINDINGS_DOCUMENTS_v1.0.md` +
  `COWORK_DUP_SCAN_GROUPS_v1.0.json` — an independent Cowork scan from
  **2026-07-08**, scoped to `1. My Folders` (the live folder's name
  before it was renamed to `00-My Folders`) and `<family-member-1>` only (1,689
  files, not the full tree this phase scanned). Found 242 duplicate
  groups, 581.7 MB reclaimable, and **independently identified the same
  `<employerA>_Termination\<employerA>_Termination` self-nested-copy pattern** this
  phase found fresh on 2026-07-31 — confirming it's real, and that it
  was never actioned in the three weeks between the two scans (no files
  were deleted by the July 8 scan itself; read-only findings only).
- `Handoff-Briefs/Live-Run-Handoff_PicturesRoot_v1.0.md` — a companion
  handoff Cowork wrote *for the already-completed Pictures-root phase*
  (commit `f746446`), reconstructed from the real transcript/repo state,
  not fabricated. Verified accurate; includes a Decision log table for
  that phase this session never wrote itself. Committed alongside this
  phase's own files as legitimate, accurate prior work.

**Not yet done:** a full reconciliation between the July 8 scan's 242
groups (narrower scope, different folder name) and this phase's 948
groups (full tree, current names) — the two don't cover the same scope
or vintage, so group counts aren't directly comparable without mapping
`1. My Folders` paths to their `00-My Folders` equivalents first. Flagged
here rather than silently ignored; worth doing before finalizing which
files get deleted from `DocFolderBackup` /
`<employerA>_Termination\<employerA>_Termination`, since the July 8 report's Appendix A
(in the `.docx`, not the companion JSON) may contain keeper/delete
judgment calls already made by {{owner}} that shouldn't be silently
re-decided.

## What happened in this phase so far (chronological)

1. High-level recon of `OneDrive\1. Documents`: 6.5 GB, 3,084 files, 551
   subfolders, 0 OneDrive cloud-only placeholders (fully hydrated, no
   network-hydration risk during hashing).
2. Full duplicate scan (`scan_documents_dedup.py`, read-only, no files
   moved): 948 duplicate groups, 3,173.2 MB reclaimable.
   `DOCUMENTS_DEDUP_PROPOSAL.json`.
3. Re-analyzed by folder-pair/workstream instead of file-pair
   (`generate_workstream_dedup_report.py`) per {{owner}}'s framing that
   cross-workstream duplicates need human judgment, not an automatic
   rule. `DOCUMENTS_WORKSTREAM_DEDUP_REPORT.md`.
4. `DocFolderBackup` delta analysis (`analyze_docfolderbackup_delta.py`):
   of 1,176 files / 3,072.9 MB, **58 files / 496.6 MB have no duplicate
   anywhere else** and would be permanently lost by a wholesale folder
   delete — including a 329 MB zip, ID document photos, resume drafts,
   and video files. Ruled out "delete the whole folder" as a shortcut.
   `DOCFOLDERBACKUP_DELTA.json`.
5. Suggested approach (pending {{owner}}'s go-ahead, not yet executed):
   rescue the 58 unique files first, then quarantine the remainder of
   `DocFolderBackup` as one unit rather than 1,118 individual files.
6. **Full physical backup taken and verified** before any of the above
   execution steps run — see Decision log above.

## Session concurrency finding (2026-07-31, end of this session's active work)

Investigated via `list_sessions`/`get_session`/`list_events` after {{owner}}
flagged a "Folder Dedup fork" session as the owner of actual
dedup/quarantine execution: three Claude Code sessions were found
concurrently pointed at this exact working directory
(`C:\Dev\onedrive-agent`), no separate git worktrees involved —

- This session ("DR fork" by elimination) — backup, verification,
  workstream/delta analysis, reconciliation (this document)
- "OneDrive agent live phase setup (Folder Dedup fork)" — owns further
  dedup/quarantine execution per {{owner}}'s direction
- "OneDrive agent live phase setup" (unsuffixed) — found to be a dormant
  session-level fork of this same conversation (identical transcript up
  to a shared checkpoint), stalled since 08:41 on a decision already
  superseded by later work here. Archived with {{owner}}'s explicit
  agreement.

This also gave a more plausible root cause for the recurring stray
`.git/index.lock` seen earlier in this phase (previously attributed to
an unconfirmed "sandbox mount quirk," see RAID I25 for the correction):
genuinely concurrent sessions sharing one working directory is a much
simpler explanation than an unexplained sandbox artifact.

**This session stands down from further repo-writing work as of this
commit**, per {{owner}}'s direction — further dedup/quarantine execution on
`OneDrive\1. Documents` is owned by the "Folder Dedup fork" session, not
this one.

---

## Current state

- ⬜ Nothing quarantined or deleted yet in this phase — steps 1-4 above
  are read-only analysis only
- ✅ Full DR backup taken and verified (see verification section)
- ⬜ Awaiting {{owner}}'s decision on the suggested approach (rescue-then-quarantine
  for DocFolderBackup) before any execution
- ⬜ `<employerA>_Termination\<employerA>_Termination` self-nested duplicate, `Certificates`
  vs `5 Certificates`, and `<employerA>_HR_Documents` vs `<salary-records>\<employerA> HR` all
  still need {{owner}}'s workstream-validity judgment, not yet decided
