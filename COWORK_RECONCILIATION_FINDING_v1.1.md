# Cowork Reconciliation Finding v1.1 — orphaned keepers in quarantine

**Produced by:** Cowork session (Claude), 3 August 2026
**Supersedes:** `COWORK_RECONCILIATION_FINDING_v1.0.md` (classifier gap — now **resolved**, see §2)
**Trigger:** Owner asked Cowork to verify the remediation run that followed v1.0.
**Method:** Independent re-check against **actual disk state**, plus a full MD5 orphan
check of every quarantined file against the live tree.
**Companion data:** `COWORK_ORPHANED_KEEPERS_v1.1.json` (aggregate; unredacted
per-document restore list in `_raw_local_only/`, gitignored).

> ## ⚠ HOLD THE PERMANENT DELETE
> **47 quarantined files across 31 distinct documents have no surviving copy anywhere
> in the live tree.** Deleting `_Duplicates_PendingDeletion\` as it currently stands
> destroys the only remaining copy of each — 12.66 MB of certificates, diplomas and
> career records. Restore first (§4), re-run the orphan check, then delete.
> Nothing is lost yet: all 47 are intact in quarantine, and the `<DR_BACKUP_ROOT>`
> backup is a second net.

---

## 1. Verification of the remediation run — what checks out

Re-checked on disk, not taken from the run's own output:

| Claim | Independent result | Verdict |
|---|---|---|
| 344 files / 590.9 MB quarantined | **345 files** / 590.9 MB | Size exact; count off by one |
| Self-nested `<employerA>_Termination\<employerA>_Termination\` reduced to 1 file / ~100 KB | **1 file, 64,746 bytes** | ✅ |
| `<hearing-recording>.wav` — keeper at shallow path, 2 nested copies quarantined | Exactly one 245,618,212-byte copy remains, at the shallow path | ✅ |
| Nothing deleted; move only | All 345 present in quarantine | ✅ |
| Cowork's 242 groups resolved | **242 / 242**, 581.7 MB reclaimed | ✅ |

**The v1.0 classifier finding is closed.** The 238 previously-unresolved groups are all
resolved, and the headline 468.5 MB `.wav` redundancy — the single largest item across
this entire phase — is genuinely gone. That work is sound.

The one-file count discrepancy is immaterial to the outcome but worth a glance: it may
be an off-by-one in the run's reporting, or one file quarantined outside the 265-group
set (`CV_Superseded\` sits at quarantine root rather than under
`Internal_Duplicates_20260803\`).

---

## 2. The new defect — over-quarantine

The v1.0 defect **omitted** work. This one **over-performed** it. Same blind spot:
the run's self-check could not see either.

For 31 documents, **every** member of the duplicate group was moved to quarantine,
including the copy that should have been retained. These are not redundant copies —
they are now the only copies in existence outside the DR backup.

| Metric | Value |
|---|---|
| Quarantined files total | 345 / 590.9 MB |
| **Orphan files (no live-tree copy)** | **47 / 14.14 MB** |
| **Distinct documents at risk** | **31** |
| Restore actions required (1 per document) | 31 / 12.66 MB |
| Safe to delete after restore | **578.3 MB** |

### Where the losses land

| Files | Location |
|---|---|
| **21** | `2 Career Documents\5 Certificates\` — the folder is effectively emptied |
| 3 | `2 Career Documents\4 Employment Companies\` |
| 2 | `2 Career Documents\1 CurrentResume\` |
| 21 | remainder — `ShareX\Backup\` configs, `<household-records>\`, `Unsorted\`, `CV_Superseded\`, one root PNG |

The `5 Certificates` casualties include the 1987 high-school diploma, the Grade 12
diploma and its evaluation certificates, overseas transcripts, First Aid Level 1, and
ten professional qualifications (ITIL Foundation, TOGAF, UCT Information Systems
Management, Diploma in Business Analysis, Disciplined Agile, Agile Samurai, SQL
Bootcamp, Scrum Master, LSS White Belt, 2004 Softrain workshops).

These are exactly the class of document the phase's DR escalation was written to
protect — irreplaceable identity and qualification records.

### Root cause

Keeper selection assumed each group had at least one member outside the action set.
Where a group's members were *all* in scope, every member was moved and no keeper was
retained. This is common in `5 Certificates\`, where the same certificate legitimately
sits in both the certificates folder and an employer folder — both in scope, so both
moved.

The dry-run and per-file preflight both **passed correctly**: they verified each file
existed and matched size before moving it. That is a *per-file* precondition. The
missing precondition is a *per-group* invariant:

> **after the move, at least one member of every group must remain in the live tree.**

`344/344 moved successfully` is true whether or not the keeper was among them.

---

## 3. Pattern across v1.0 and v1.1

Two consecutive defects, opposite in direction, identical in mechanism: **the run
verified its own execution, not its own intent.**

- v1.0 — classifier routed 260 groups away from the queue → work omitted; file-count
  reconciliation balanced anyway, because it reconciled against the queue.
- v1.1 — keeper selection moved every copy → work over-applied; dry-run and preflight
  passed anyway, because they checked file-level preconditions.

Both were found only by an **external** check with an independent notion of what the
correct end state is. This is the concrete argument for the standing practice proposed
in v1.0 §5.4 and still listed as unadopted: a post-action re-scan asserting the
intended invariants, run every phase, not just when someone thinks to ask.

---

## 4. Required actions, in order

1. **Restore the 31 documents.** `COWORK_ORPHANED_KEEPERS_v1.1.json`
   (`_raw_local_only/`) gives one entry per document with `restore_from`,
   `restore_to` and `other_copies_safe_to_delete`. `restore_to` is the shallowest
   original path — adjust if a different canonical location is preferred; what matters
   is that exactly one copy returns to the live tree.
2. **Re-run the orphan check** and require **`orphan_files == 0`** as the gate. This is
   the release condition for step 3.
3. **Then permanently delete** the remaining quarantine — **578.3 MB**, all verified
   redundant.
4. **Fix keeper selection**: enforce the per-group invariant — if every member of a
   group is in the action set, exclude the chosen keeper from the move rather than
   moving all members.
5. **Adopt the post-action re-scan** as standing practice (carried over from v1.0 §5.4,
   still open). Minimum assertions: every previously-reported group has ≥1 surviving
   copy, and no group retains >1.
6. **RAID**: recommend a new Issue for the over-quarantine, and keep I28 at Monitoring
   until step 2 passes. This is a near-miss on irreplaceable records, caught before
   deletion — worth logging at that weight.

---

## 5. Caveats

- Orphan test is **content-based** (full MD5), not name-based: a document counts as
  surviving only if a byte-identical copy exists in `00-My Folders\` or
  `<family-member-1>\`. Files moved elsewhere and renamed would still be detected.
- Live-tree scope is the two mounted roots. A surviving copy in another `1. Documents`
  subfolder outside that scope would not be seen — if any of the 31 look wrong, check
  there before restoring.
- Two profile-picture groups reported as "all copies gone" against the v1.0 baseline
  are **not** part of this finding: they were deliberately fully quarantined and
  deleted on 2026-08-02 per `LIVE_RUN_INTERNAL_DUPLICATES.md` Groups 5–6.
- `AI-Agent-Build-Handoff_v1.0.md` / `v1.1.md` are absent from both live tree and
  quarantine — removed in an earlier phase, outside this finding's scope.
- Verified 2026-08-03. Nothing was deleted, moved or renamed to produce this finding;
  the only writes are this file and its two companion JSONs.
