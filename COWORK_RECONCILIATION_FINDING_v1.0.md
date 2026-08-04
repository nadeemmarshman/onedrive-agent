# Cowork Reconciliation Finding — Documents dedup classifier gap (v1.0)

**Produced by:** Cowork session (Claude), 3 August 2026
**Trigger:** Owner asked Cowork to verify whether the findings in
`COWORK_DUP_SCAN_FINDINGS_DOCUMENTS_v1.0.md` (scan dated 2026-07-08) had been
actioned by the Documents live-run phase (`LIVE_RUN_DOCUMENTS.md`, closed 2026-08-02).
**Method:** Cowork's 242 duplicate groups re-checked against **actual disk state**
on 2026-08-03, not against any report.
**Companion data:** `COWORK_RECONCILIATION_REMAINING_v1.0.json` (aggregate; unredacted
per-group detail in `_raw_local_only/`, gitignored).

---

## 1. Verdict

**Not actioned.** 238 of 242 groups are still duplicated on disk.

| Measure | Value |
|---|---|
| Groups resolved | **4** of 242 |
| Groups still duplicated | **238** |
| Reclaimable space still on disk | **578.1 MB** of 581.7 MB |
| Proportion actioned | **0.6%** |
| Suggested keepers missing (data-loss check) | **0** — no keeper was lost |

The phase index already recorded the risk in its own words: the Cowork scan
"independently found the same `{{employerA}}_Termination` self-duplication, which confirms
that finding was real and had simply sat unactioned for three weeks." That statement
is still true today — the three weeks is now four.

Spot-check, live paths, 2026-08-03:

```
245618212  ...\{{employerA}}_Termination\{{employerA-suspension}}\{{hearing-recording}}.wav
245618212  ...\{{employerA}}_Termination\{{employerA}}_Termination\{{employerA-suspension}}\{{hearing-recording}}.wav
245618212  ...\{{employerA}}_Termination\{{employerA}}_Termination\{{employerA-suspension}}\{{suspension-documents}}\{{hearing-recording}}.wav
```

`{{employerA}}_Termination\` tree: **777 MB across 87 files**, self-nested subtree intact.

The 4 groups that did resolve were the profile-picture variants (Groups 5–6 of
`LIVE_RUN_INTERNAL_DUPLICATES.md`) — see §3 for why exactly those.

---

## 2. Root cause — `_classify()` in `scan_documents_dedup.py`

```python
def _classify(group: list[dict]) -> str:
    in_backup = [BACKUP_MARKER in f["path"] for f in group]
    if any(in_backup) and not all(in_backup):
        return "docfolderbackup_vs_live"          # <-- absorbs mixed groups
    if not any(in_backup):
        return "internal_duplicate_in_live_tree"
    return "internal_duplicate_within_backup"
```

The classifier asks *"does this group span the backup boundary?"* and stops there.
It never asks *"how many copies are on the live side?"*

A group is labelled `docfolderbackup_vs_live` if **at least one** member sits under
`DocFolderBackup`, regardless of how many live-tree copies accompany it. The
remediation for that class was the wholesale quarantine-and-delete of the
`DocFolderBackup` folder — which removes the backup members **and nothing else**.
Live-tree redundancy inside those groups was therefore never queued for action, and
never appeared in any summary.

The `{{hearing-recording}}.wav` group, as recorded in the raw proposal, had **4 members:
1 backup + 3 live**. It was classified `docfolderbackup_vs_live`. One copy was deleted.
Three remain.

### Measured impact

Recomputed from `_raw_local_only/DOCUMENTS_DEDUP_PROPOSAL.json`:

| Metric | Value |
|---|---|
| Groups classed `docfolderbackup_vs_live` that also held **>1 live-tree copy** | **260** |
| Live-tree redundancy hidden inside that class | **590.7 MB** |
| Live-tree redundancy actually reported (`internal_duplicate_in_live_tree`) | 13 groups / 6.2 MB |

So the proposal reported ~1% of the live-tree redundancy it had the data to detect.
The 590.7 MB (CODE's scope, all of `1. Documents`) and Cowork's 578.1 MB (narrower
scope, two roots) are the same phenomenon measured over different scopes.

**This is a classification defect, not a detection defect.** The hashing and grouping
were correct — every one of these groups is present and correct in the raw proposal.
Only the label, and therefore the action routing, was wrong.

---

## 3. Why the 4 resolved groups resolved

The profile-picture groups had **no `DocFolderBackup` twin**, so `any(in_backup)` was
false and they fell through to `internal_duplicate_in_live_tree` — the one branch whose
remediation actually targets live-tree copies. They were resolved correctly.

This confirms the mechanism precisely: the internal-duplicate path worked whenever a
group reached it. The defect is solely that mixed groups never did.

---

## 4. Why the phase's own reconciliation did not catch this

`LIVE_RUN_DOCUMENTS.md` closes with a file-count reconciliation that balances exactly
(3,084 − 1,939 = 1,145 removed = 1,118 + 14 + 2 + 11). That arithmetic is correct.

It reconciles **what was deleted against what was queued**. It cannot detect work that
never entered the queue — a gap of this shape is invisible to it by construction. The
phase's own stated lesson (I24/I25/I26): *"a tool's own report of its state is not
evidence."* The same applies one level up — a scan's own classification of its findings
is not evidence that the findings were acted on. Only an independent detection source,
or a post-action re-scan, closes that loop. This finding is the former.

---

## 5. Recommended actions for CODE

1. **Fix `_classify()`** — classification should be multi-label, or at minimum a group
   with >1 live-tree member must always be routed to internal-duplicate handling
   regardless of backup membership. Suggested shape:

   ```python
   live = [f for f in group if BACKUP_MARKER not in f["path"]]
   backup = [f for f in group if BACKUP_MARKER in f["path"]]
   labels = []
   if backup and live: labels.append("docfolderbackup_vs_live")
   if len(live) > 1:   labels.append("internal_duplicate_in_live_tree")
   if len(backup) > 1: labels.append("internal_duplicate_within_backup")
   ```

   with `redundant_bytes` reported per label so no class can mask another.

2. **Re-run the scan** against the current live tree and confirm it now reports
   ~238–260 internal groups rather than 13.

3. **Work the 238 groups** in `COWORK_RECONCILIATION_REMAINING_v1.0.json`
   (`_raw_local_only/` for paths). Highest-value single action remains deleting the
   self-nested `{{employerA}}_Termination\{{employerA}}_Termination\` subtree — ~500 MB,
   one operation.

4. **Add a post-action verification step** to the live-run pattern: re-scan after
   deletion and assert the previously-reported groups are gone. This is the control
   that would have caught the gap without an external scan.

5. **RAID entry** — recommend logging as an Issue in the same family as I24/I25/I26:
   *a classifier silently routed 260 groups away from the action queue; the phase's
   internal reconciliation could not see the omission.*

---

## 6. Caveats

- Cowork's scope (two roots) ≠ CODE's scope (all of `1. Documents`); the 238 is a
  **subset**, not a full current-state count. A corrected re-scan will likely find more.
- Path translation applied: Cowork's `1. My Folders\` → current `00-My Folders\`.
  Existence was tested against translated live paths.
- Group membership is the reconciliation key, not keeper choice (keeper heuristics
  differ between the two tools; both are advisory).
- Verified 2026-08-03. Nothing was deleted, moved or renamed to produce this finding —
  the only writes are this file and its two companion JSONs.
- All keepers confirmed present: **no data loss** from the phase. The gap is
  unreclaimed space and unresolved redundancy, not lost files.
