# Live Run — `OneDrive\PC Backup` (2026-08-02)

**Outcome:** 1,070 files / 2,840.3 MB quarantined as a single folder
move, after byte-level verification established the folder was
**99.86% redundant by size** with **nothing requiring rescue**.

---

## How this phase was selected

This was the planned next step in a sequenced programme, not an
incidental discovery.

With the `1. Documents` phase closed, {{owner}} commissioned a deliberate
review across both the C: and D: drives to decide what should follow.
That survey — deliberately taken before choosing a target, rather than
jumping to the next obvious folder — produced a ranked set of candidates
by capacity recovered against risk and effort. `PC Backup` ranked second,
behind only a 19.58 GB Google Takeout export, and was chosen first
specifically **because it was the same shape as the job just completed**:
a stale mirror of the live Documents tree, addressable with the exact
playbook and scripts built for `DocFolderBackup`.

{{owner}}'s framing for the programme is *slow and steady, sorting out bugs
along the way* — take a known-shaped problem next, reuse the proven
method, and surface defects on familiar ground rather than novel ground.
This phase is that principle applied.

The survey's other findings (Videos 41.18 GB, Apps 19.58 GB, the
cloud-only storage picture) are recorded separately and remain open.

---

## What PC Backup was

A second stale mirror of the Documents tree — the same pattern as
`DocFolderBackup`, but a **root-level sibling** of `1. Documents` rather
than a child of it, which is why the original Documents-phase scan never
covered it. Its internal structure preserved the **pre-rename** layout
(`PC Backup\1. Documents\1. My Folders\...`), against a live tree since
reorganised to `00-My Folders\...`, dating the snapshot to before that
rename.

---

## Verification: why the full download was justified

PC Backup was ~entirely OneDrive **cloud-only placeholders** — 852 KB on
disk against 2.77 GB logical. Hashing it therefore required hydrating
(downloading) the whole folder.

An initial name+size comparison suggested ~96% overlap and would have
cost nothing. It was rejected as insufficient evidence to delete on, for
a reason this dataset had already demonstrated: during the
`DocFolderBackup` triage, **six files in the `308 <calibre-1>` folder
shared identical names with live-tree files but held genuinely different
content**. Name+size matching would have destroyed those. On a folder of
legal and financial records, bandwidth was the cheaper risk.

{{owner}} chose full download-and-hash. Note that hydrating does not
increase cloud quota usage — the bytes are already counted — it costs
bandwidth and temporary local disk, both reversible via "Free up space".

### Bandwidth optimisation applied

`analyze_pcbackup_delta.py` hydrates only what it must. Since two files
can only be byte-identical if their sizes match exactly, any PC Backup
file whose size appears nowhere in the live tree is unique *by
definition* and is never downloaded.

In practice this saved little — 7 files / 3.9 MB — which is itself a
finding: virtually every file had a size twin, consistent with a
near-total mirror. 1,063 files / 2,836.4 MB were hydrated and hashed.

---

## Result

| | Files | Size |
|---|---:|---:|
| Byte-identical twin in live tree | **1,063** | **2,836.4 MB** |
| Unique (no byte-identical twin) | 7 | 3.9 MB |
| **Total** | **1,070** | **2,840.3 MB** |

### The 7 unique files were not a rescue list

Every one had **already been flagged unique during the DocFolderBackup
phase and ruled on by {{owner}} that same day**:

| Prior decision | File |
|---|---|
| DISCARD → deleted | `Business-Analyst-Resume-Example-Free-Download.zip` |
| DISCARD → deleted | `<vendor-diagnostic-tool>` |
| DISCARD → deleted | `<employerD> 1997 Top Achiever.collection` |
| DISCARD → deleted | `<employerD> move to <employerC>.collection` |
| DISCARD → deleted | `<education-body> Certificate of Evaluation Grd 12.collection` |
| DISCARD → deleted | `<employerC> Employment.collection` |
| LEAVE → deleted by {{owner}} | `<care-facility>\20 Mar, 11.46​.m4a` |

They register as "unique" only because their live-tree counterparts were
removed earlier the same day.

**This is an independent validation of the DocFolderBackup triage.** Two
unrelated stale backups, scanned three days apart by different methods,
converged on the identical seven-file unique set.

Consequence: **no staging step was needed.** DocFolderBackup required
relocating 58 unique files before its folder could be quarantined; here
the job collapsed to a single move.

### The resurfaced voice note

`20 Mar, 11.46​.m4a` (3,112,466 bytes, MD5 `0abf879143d19677c4e1b040b415c09a`)
was deleted by {{owner}} earlier that day without identification. It was
verified byte-identical in two surviving locations and flagged to him
before the move rather than silently carried along:

- `<DR_BACKUP_ROOT>\DocFolderBackup\Documents\<care-facility>\`
- the PC Backup copy now in quarantine

{{owner}} elected to quarantine everything, standing by the original
decision. The D: backup copy remains until that backup is itself retired.

---

## Execution

`quarantine_pcbackup_wholesale.py` moved the folder to
`OneDrive\_Duplicates_PendingDeletion\PC Backup\` in one operation.

The script preflights before touching anything — re-counting files on
disk against `PCBACKUP_DELTA.json` and asserting the unique count is
still exactly 7 — so a stale JSON cannot authorise a move that no longer
matches reality.

Verified afterwards:

- `PC Backup` no longer exists at the OneDrive root
- quarantine holds exactly 1,070 files / 2.8 GB
- live `1. Documents` unchanged at 1,939 files

Nothing deleted. Final delete is {{owner}}'s call, as in every phase.

---

## Safety-net caveat, stated explicitly

Unlike the Documents phase, **the D: backup does not cover this folder.**
`<DR_BACKUP_ROOT>` mirrors
`OneDrive\1. Documents` only — verified from the robocopy log's own
`Source :` line — and `PC Backup` is a root-level sibling, not a child.

This was raised with {{owner}} before any move. The residual exposure is
narrow and was accepted knowingly: 1,063 of 1,070 files have MD5-verified
twins inside `1. Documents`, which *is* backed up; the remaining 7 are
the already-rejected set above, of which the only one of any substance
survives independently on D:.

---

## Artefacts

**Scripts** — `analyze_pcbackup_delta.py`, `quarantine_pcbackup_wholesale.py`
**Data** — `PCBACKUP_DELTA.json` (full per-file duplicate and unique lists)

## Open item

Final permanent delete of
`OneDrive\_Duplicates_PendingDeletion\PC Backup\` (1,070 files, 2.77 GB).

Per RAID **I26**, delete via **OneDrive web** rather than local File
Explorer: this folder was created by script, and Explorer's OneDrive
"Home" view has been observed serving a stale listing that omits
script-created folders entirely, causing repeated failed delete attempts
in the previous phase.
