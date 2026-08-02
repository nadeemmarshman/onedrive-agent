# OneDrive AI Agent — Live Run Handoff Brief: Pictures Root

**Purpose of this document:** Companion to `Live-Run-Handoff_v1.0.md`
(Camera Roll phase), covering the **second** live-run exercise — a
top-level scan of `OneDrive\Pictures` root — retroactively documented by
Claude Cowork from CODE's own session transcript and the actual repo state
(RAID_LOG.md, BACKLOG.md, `LIVE_RUN_PICTURES_ROOT.md`, commit `f746446`),
not re-derived or guessed.

**Current version: v1.0**

**Acronyms:** as defined in `GLOSSARY.md` in the repo.

---

## Relationship to the existing project

The Camera Roll live-run phase is formally closed via its own closing tag,
`v2.1-live-run-camera-roll-complete` (cut in commit `a858028`, immediately
before this exercise began). Following the same reasoning CODE already
applied to `AI-Agent-Build-Handoff_v9.2.md` (don't reopen a closed phase's
document to log a new phase's decisions), this is a **new** document, not
an extension of `Live-Run-Handoff_v1.0.md`.

This document covers: a read-only scan and quarantine-move exercise
against `OneDrive\Pictures` root (top-level files only), run 2026-07-31.

---

## Scope note

`Camera Roll` and `Screenshots` are subfolders of `Pictures` and were
**deliberately excluded** from this run — `Camera Roll` because it's
already its own closed, tagged phase; `Screenshots` as a candidate future
phase of its own. See Decision log entry 2 below for why top-level-only,
rather than a single recursive pass over all of `Pictures`, was chosen.

---

## What happened in this live-run phase (chronological)

1. **Scan and quarantine-move run.** `quarantine_pictures_root_dedup.py`
   (new script, same read-only-scan-then-reversible-quarantine pattern as
   Camera Roll) run against `OneDrive\Pictures` root — 6,426 files,
   top-level only. Run in the background given the file count. Result:
   477 duplicate groups, 478 files quarantined, 98.7 MB moved into
   `_Duplicates_PendingDeletion\`. Nothing deleted.

2. **Defect caught by checking actual output, not trusting it.** The tail
   of the run's own log was reviewed directly rather than accepting the
   script's success message at face value — this surfaced a pattern that
   looked backwards from the Camera Roll result.

3. **Root-caused before acting.** Verified against real file timestamps
   rather than assumed: confirmed systematic, not random — all 32 groups
   using OneDrive's parenthesized `"(1)"` conflict-copy convention (as
   opposed to Camera Roll's `" 1"` convention) had the wrong file kept.
   The keeper-selection helper built for Camera Roll (RAID I21) only
   matched the `" 1"` pattern; for `"(1)"` groups it silently fell through
   to arbitrary (alphabetical) scan order, and `"(1)"` happens to sort
   before `"."` — so the conflict copy won every time. Logged as **RAID
   I22**.

4. **Manually corrected the 32 wrong keepers**, each MD5-verified
   identical before acting.

5. **Fixed the root cause, not just the symptom.** Rather than patch the
   same regex in three separate scripts (`quarantine_camera_roll_dedup.py`,
   `propose_camera_roll_dedup.py`, `quarantine_pictures_root_dedup.py` —
   three copy-pasted copies of the same helper is exactly how I22 slipped
   through unnoticed), the logic was extracted into one shared module,
   `dedup_keeper.py`, covering both suffix styles, and all three scripts
   were updated to import from it. See Decision log entry 1.

6. **Second anomaly found during verification, not assumed away.** A
   final comprehensive re-check (all 478 groups, not a spot-check) found
   one pair left with both copies in quarantine and neither in root,
   despite the swap script reporting success for all 32. MD5-confirmed
   both copies identical, then manually restored the plain-named copy to
   root. Root cause not conclusively identified — logged as **RAID I23**,
   status **Monitoring**, not Closed, since the cause is unconfirmed. See
   Decision log entry 3.

7. **Full re-verification pass** — all 478 groups checked against the
   *corrected* keeper-selection logic (an initial check against the
   original, pre-fix log values produced a false alarm, caught and
   redone against the right ground truth) — 0 mismatches.

8. **Final totals confirmed directly**, not assumed from script output:
   5,948 files in root + 478 in quarantine = 6,426, matching the original
   scan exactly.

9. **Documented and committed.** `RAID_LOG.md` (I22, I23),
   `LIVE_RUN_PICTURES_ROOT.md` (full report) written, all changes
   committed as `f746446` and pushed to `origin`.

---

## Current state

- ✅ Scan and quarantine-move complete, read-only detection, reversible
  move only — nothing permanently deleted
- ✅ RAID I22 (keeper-selection gap) — Closed, fixed and re-verified
- ⚠️ RAID I23 (both-in-quarantine anomaly) — Monitoring, resolved for this
  instance, root cause unconfirmed
- ✅ `dedup_keeper.py` consolidation — all three quarantine/proposal
  scripts now share one keeper-selection implementation
- ✅ `LIVE_RUN_PICTURES_ROOT.md` full report committed
- ⬜ Final delete of `_Duplicates_PendingDeletion\` contents — left for
  {{owner}}, same as Camera Roll
- ⬜ Backlog #15 (real `tools.py` fix) still open and now covers this
  phase's findings too — `dedup_keeper.py` is a more complete call-site
  workaround than Camera Roll's, but `propose_action()` itself in
  `tools.py` remains unmodified
- ⬜ No GitHub Release tag/page has been cut for this phase yet (unlike
  Camera Roll's `v2.1-live-run-camera-roll-complete`) — not raised as a
  Backlog item here since {{owner}} has not indicated this folder needs its
  own separate resume URL; flagging only so it isn't assumed done

## Commits (this phase)

- `a858028` — Cut Camera Roll phase closing tag (`v2.1-live-run-camera-roll-complete`),
  update docs to point to it — done immediately before this phase, not part of it,
  but the reason this document doesn't extend `Live-Run-Handoff_v1.0.md`
- `f746446` — Live run: Pictures root dedup, find and fix keeper-selection
  gap (I22/I23)

---

## Decision log

Same table format as `Handoff-Briefs/AI-Agent-Build-Handoff_v9.2.md` and
`Live-Run-Handoff_v1.0.md`. None of these three were logged anywhere at
the time they were made — reconstructed here from the actual session
transcript and verified against the real repo state (commit `f746446`,
`RAID_LOG.md` I22/I23) before being written down, not from memory alone.

| Phase | Decision | Options considered | Key trade-off | Choice |
|---|---|---|---|---|
| Live-run (Pictures root) | How to fix the I22 keeper-selection gap | (a) patch the missing `"(1)"` pattern into each of the three scripts' own copy of the check; (b) extract the logic into one shared module used by all three | (a) is a smaller immediate diff, but three duplicated copies of the same logic is the exact condition that let I22 exist unnoticed in the first place — patching one place still leaves the other two capable of drifting again. (b) costs a small upfront refactor (one new module, three call-site updates) but removes the duplication that caused the defect class, not just this one instance of it. | **(b) — consolidated into `dedup_keeper.py`**, covering both `" 1"` and `"(1)"` suffix styles, imported by all three scripts |
| Live-run (Pictures root) | Scope of this run: `Pictures` root only vs. all of `Pictures` recursively | (a) one recursive pass covering `Pictures` and every subfolder (including `Camera Roll`) in a single run; (b) top-level files only, treating `Camera Roll` and `Screenshots` as separate phases | (a) is fewer total runs, but `Camera Roll` is already a closed, tagged phase — folding it back into a new scan would blur that closure and mix two phases' results into one report. (b) keeps each phase's report and tag scoped to one folder, consistent with the pattern already established, at the cost of needing a separate run for `Screenshots` later. | **(b) — top-level only**, `Camera Roll`/`Screenshots` excluded and left as their own (closed / future) phases |
| Live-run (Pictures root) | How to resolve the RAID I23 both-in-quarantine anomaly | (a) pause and fully root-cause it before touching either file, given the folder's real personal-photo content; (b) MD5-verify the two copies are genuinely identical, manually restore one, and log the unresolved root cause as Monitoring rather than Closed | (a) is more rigorous but risks stalling an otherwise-complete, already-verified run over a single ambiguous case with no clear next diagnostic step. (b) is safe specifically because the MD5 check removes any risk of data loss either way (the two files are provably identical content), and honestly disclosing "resolved, cause unconfirmed" is consistent with this project's existing practice (e.g. RAID I15/I16) of not overclaiming certainty. | **(b) — verify identical, manually restore, log as Monitoring** rather than Closed |

---

## What I'd still flag to CODE / {{owner}}

- This document, plus the RAID_LOG.md/BACKLOG.md check below, is written
  directly into the real, connected repo (`C:\Dev\onedrive-agent`), since
  Request 1 (this Pictures-root exercise) is complete. The separate,
  still-in-progress Documents-folder exercise (Request 2) is deliberately
  **not** touching this repo yet — that documentation is being held in
  this Cowork session's own sandbox until CODE's final steps are known.
