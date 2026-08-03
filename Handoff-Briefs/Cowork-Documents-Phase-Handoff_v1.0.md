# Handoff Brief — Documents phase, Cowork session (v1.0)

**From:** Claude Cowork session, 8 July – 3 August 2026
**To:** the next session (Cowork or CODE) picking up the Documents work
**Closes:** the de-duplication phase from the Cowork side
**Companion:** `<ONEDRIVE_ROOT>\<DOCS>\<area>\<admin>\<audit-report-v2>.docx` (closing report, plain-English, for {{owner}})

---

## 1. Why this brief exists

This session ran long and holds a lot of context that is now historical. The
remaining work — building the folder schema — is a different kind of task and
deserves a clean start. Everything a successor needs is below or in the
referenced artefacts; nothing important lives only in the chat transcript.

## 2. Where things stand

**The de-duplication phase is complete.** Measured on disk 2026-08-03, not
carried forward from any report:

| | v1 (2026-07-08) | now (2026-08-03) |
|---|---|---|
| Duplicate groups | 242 | **9** |
| Redundant copies | 308 | 9 |
| Reclaimable | 581.7 MB | **0.44 MB** |

Current tree: 1,288 files / 3,274.4 MB across `00-My Folders` (1,201 files,
247 folders), `<family-member-1>`, `Unsorted` (31), `ShareX` (19).
`Certificates\` (top-level) and `_Duplicates_PendingDeletion\` are both empty.

Of the 9 remaining groups, 4 are `ShareX` application backups behaving normally
and should be left alone. The rest resolve when `Unsorted\` and `<care-facility>\`
are triaged.

## 3. What was done

Cowork side: original scan and report v1; reconciliation findings v1.0 and v1.1;
independent verification of every CODE remediation run; `Will and Testament`
rename; report v2.

CODE side (see `LIVE_RUN_DOCUMENTS.md`, RAID I28/I29): the quarantine and
delete runs, the orphan restore, and `verify_dedup_invariants.py`.

{{owner}} performed every permanent deletion himself. That gate held throughout and
is why two near-misses cost nothing.

## 4. Open items

**Small, mechanical:**

- 2 `.lnk` shortcuts — under `<training>\...\LSS GB Simulation Files\` and
  `<employerA>_Work_Files\Mine\General\<firearm-3>\`
- `Other Unsorted` (1 file) and `Random Artifacts` (empty) — review then delete
- `Personal(Revolving)` — bracketed folder name, still to fix
- 6 reload-notes pairs with `(from DocFolderBackup)` suffixes — need a human
  decision per pair on which is current (`TODO.md`)
- `Unsorted\` (31 files) never triaged
- ~3 GB now hydrated locally that was cloud-only — "Free up space" pass due,
  once sync settles (watch for the RAID I26 stale-cache trap)

**Substantial:**

- **The folder schema has not been built.** Section 5 of report v1, restated in
  v2 §4.2. Only `00-Admin\` exists. Recommended order: `90-Archive` first
  (largest, lowest risk), then `20-Finance`, renaming while moving.

## 5. Things a successor should know

**Cowork cannot delete on the OneDrive mounts.** `rmdir` is blocked outright,
and the mounted folders are separate mounts, so a cross-folder `mv` of a
directory becomes copy-then-delete and half-fails — leaving the source in place.
This happened once in this session and had to be cleaned up by {{owner}}. Renames
*within* a parent work fine (single `rename()`, no removal). Plan accordingly:
Cowork can rename and create; deletions go to {{owner}} or CODE.

**Scope your checks, and say so.** A finding limited to two mounted roots was
stated too strongly and produced a false diagnosis (v1.1 §7.3 in the report).
The correction was right. Then the *re-check* hit the same trap again — an
apparent orphan that was simply in an unmounted folder. Mount everything before
concluding anything is missing.

**Substring matching has bitten three times.** `Bytes` inside `size_bytes`
(documented in `sanitize_mapping.json`), a correctly-mapped token matching inside
its own correctly-generated placeholder, and `pension` inside `suspension`. The
third caused both
Cowork and CODE to misread a rename verification. Anchor to word or path-segment
boundaries anywhere substring matching is used — including in verification code,
where a false negative is worse than a false positive.

**Verify end states, not actions.** Both defects this phase passed their own
checks. "344/344 moved successfully" is true whether or not the right files were
chosen. `verify_dedup_invariants.py` now encodes the right shape of check; use it
rather than re-deriving one.

**The certificates problem recurred twice.** Resolved once, then silently
re-created by a keeper heuristic preferring a stale folder. It is the strongest
argument that the schema work is the actual fix — cleanup alone resets the
counter without stopping it.

## 6. Artefacts

**In this repo (sanitised; unredacted copies in `_raw_local_only/`, gitignored):**
`COWORK_DUP_SCAN_FINDINGS_DOCUMENTS_v1.0.md`, `COWORK_DUP_SCAN_GROUPS_v1.0.json`,
`COWORK_RECONCILIATION_FINDING_v1.0.md`, `COWORK_RECONCILIATION_REMAINING_v1.0.json`,
`COWORK_RECONCILIATION_FINDING_v1.1.md`, `COWORK_ORPHANED_KEEPERS_v1.1.json`,
`Handoff-Briefs\CODE-to-Cowork-Reconciliation-Response_v1.0.md`, this brief.

**In OneDrive (`<area>\<admin>\`):** report v1 + its duplicate-groups JSON
(retained as the record of the starting state), and report v2.

## 7. Suggested first move for the successor

Read report v2 §4.2 and §7, then confirm current state on disk before trusting
any of the above — including this brief. Start the schema work with `90-Archive`,
one area at a time, with {{owner}} approving each move. Do not batch it.
