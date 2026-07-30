# OneDrive AI Agent — Live Run Handoff Brief

**Purpose of this document:** Context handoff for the *live-run phase* of the OneDrive AI Agent project, written so Claude Cowork (with no prior memory of this conversation) can pick up from here and produce project-management artifacts (RAID log entries, backlog items, decision log, lessons learned, etc.) for this phase specifically. Upload as a Project knowledge file.

**Current version: v1.0** (this document starts fresh for the live-run phase; it does not replace or continue the closed foundational-build handoff below)

**Acronyms:** as defined in `GLOSSARY.md` in the repo.

---

## Relationship to the existing project

This is **not** a continuation of the main handoff document
(`Handoff-Briefs/AI-Agent-Build-Handoff_v9.2.md`). That document covers
Phases 1–8 of the foundational build, which was **formally signed off and
closed on 2026-07-20** (`PILOT_SIGNOFF_SUMMARY.md`). Read that document
first for full background if you need it — this brief assumes the
foundational build already exists and works, and does not repeat its
history.

This document covers a new, separate exercise: a **live run of the
already-built duplicate-detection tool against real data**, started
2026-07-30, deliberately kept distinguishable from the closed build for
resume/portfolio purposes (see "Release phases" below).

---

## Who I am / context

{{owner}} — Delivery Lead | Senior Business Analyst, based in Johannesburg,
South Africa. Same person/context as the main handoff document. This
project is a portfolio artefact: the point is to demonstrate BA/PM
discipline (requirements → design → build → governance) applied to a
technical build, not just to get the file cleanup done.

---

## Why a separate live-run phase, and why tagged releases

Goal: be able to link the foundational build and this live-run exercise
as two distinct items on a resume, without splitting into two GitHub
repos (more overhead than a solo portfolio project needs).

**Mechanism chosen: two annotated git tags on the same `main` branch**,
each becoming its own GitHub Releases URL:

- `v1.0-foundational-build` — tags the exact commit at project closure
  (2026-07-20). Points to Phases 1–8, the full BA/PM artefact suite, pilot
  sign-off.
- `v2.0-live-run-camera-roll` — tags the commit where the live-run script
  and report first landed (2026-07-30).

Tags are fixed points; work committed after `v2.0-live-run-camera-roll`
(including everything below) does not move that tag. Both tags are pushed
to `origin`. GitHub Releases still need to be manually drafted from each
tag (Repo → Releases → Draft a new release → pick existing tag) — not yet
done as of this document.

---

## What happened in this live-run phase (chronological)

1. **Live run against real data.** `tools.py`'s existing `scan_folder()` /
   `find_duplicates()` (MD5 content hash, unmodified) run against the real
   `OneDrive\Pictures\Camera Roll` folder (218 files) instead of the
   disposable `sample_data/` fixture. Result: 2 true duplicate groups, 2
   redundant files, 5.8 MB reclaimable. Read-only — no files touched.
   Script: `live_run_camera_roll_dedup.py`. Report: `LIVE_RUN_CAMERA_ROLL.md`.

2. **Defect found: keeper-selection bug in `propose_action()`.**
   `propose_action()` (Phase 1, `tools.py`) keeps `group[0]` as the
   "original" arbitrarily. Both duplicate groups found here follow
   OneDrive's own sync-conflict naming convention — a `" 1"` suffix before
   the extension marks the file OneDrive created on a naming conflict, not
   the original — and in both cases `group[0]` happened to be the
   suffixed (i.e. wrong) file. **Not fixed in `tools.py` itself** (would
   change Phase 1 behaviour retroactively, out of scope for this
   exercise); instead handled at the call site.

3. **Proposal drafted.** `propose_camera_roll_dedup.py` reorders each
   duplicate group so a plain-named file is preferred as keeper, then
   calls the existing `propose_action()`. Output: `PROPOSED_ACTIONS_CAMERA_ROLL.json`
   — for human review only, matching the original project's approval-gate
   philosophy (nothing executes without a human decision).

4. **Direct deletion requested, then declined.** {{owner}} asked for the two
   duplicate files to be deleted outright. Declined: permanent deletion is
   a prohibited action for this assistant regardless of user
   authorization — a deliberate safety boundary, not a project-specific
   rule. Full paths and a manual PowerShell/File-Explorer command were
   given instead so {{owner}} could do it himself.

5. **Process change: quarantine instead of direct delete.** {{owner}} asked
   for the workflow itself to change — move identified duplicates to an
   aptly-named subfolder instead of deleting them, so the final delete
   stays a deliberate, separate, human-initiated step.
   `quarantine_camera_roll_dedup.py` added: moves duplicates (using the
   same keeper-selection fix as step 3) into
   `Camera Roll\_Duplicates_PendingDeletion\`. Moving is reversible
   (nothing destroyed), so it proceeded as a regular action rather than
   requiring the same declined-deletion treatment.

6. **Executed and verified.** Both duplicate files
   (`IMG_20260326_123420 1.jpg`, `IMG_20260713_153505 1.jpg`) moved into
   the quarantine subfolder; both plain-named originals confirmed still
   in place in the main folder via a direct `ls` check on disk (not
   assumed from script output alone).

---

## Current state

- ✅ Live run executed, findings documented, read-only
- ✅ Keeper-selection defect found, documented, worked around at the call
  site (original `tools.py` deliberately left unmodified)
- ✅ Proposal file drafted for human review
- ✅ Quarantine workflow built and executed — two duplicates moved to
  `_Duplicates_PendingDeletion\`, originals verified untouched
- ⬜ **Not yet done:** final delete of the two files inside
  `_Duplicates_PendingDeletion\` — left for {{owner}} to do himself, on his
  own schedule
- ⬜ **Not yet done:** GitHub Releases pages drafted from the two existing
  tags (tags exist and are pushed; the Releases UI step itself is manual
  and outstanding)

## Commits (chronological, this phase, all on `main`)

- `bc00a77` — Live run: byte-for-byte dedup against real OneDrive Camera
  Roll folder
- (tag `v2.0-live-run-camera-roll` points here)
- `9dd73a4` — Draft proposal for the two live-run duplicates, fix
  keeper-selection bug
- `6b62d5e` — Add quarantine-move step, replacing direct delete of live
  duplicates

Tag `v1.0-foundational-build` points to `a18ba91` (the commit immediately
before this phase began).

---

## Decision log

Same table format as `Handoff-Briefs/AI-Agent-Build-Handoff_v9.2.md`.
Kept in this document rather than reopening v9.2 — v9.2 is formally
signed off and closed, and this phase's own tagging scheme
(`v1.0-foundational-build` / `v2.0-live-run-camera-roll`) exists
specifically to keep the closed build and this live-run phase separately
linkable; reopening v9.2 to log two live-run decisions would undercut the
closure it's meant to preserve. (Raised to Cowork as a real question, not
assumed; Cowork flagged it rather than guessing, {{owner}} deferred the call
to CODE, CODE decided this — 2026-07-30.)

| Phase | Decision | Options considered | Key trade-off | Choice |
|---|---|---|---|---|
| Live-run | How to split the closed foundational build from this live-run phase for separate resume URLs | (a) two GitHub repos, (b) one repo/two long-lived branches, (c) one repo/two tagged releases on `main` | (a) cleanest separation but doubles repo-maintenance overhead for a solo portfolio project; (b) cheaper than two repos but branch URLs read as work-in-progress, not two distinct deliverables; (c) simplest, and GitHub Releases pages give genuinely separate URLs despite being one repo — the main risk is it reading as "one project with versions" rather than two, judged an acceptable trade for a portfolio artefact | (c) — `v1.0-foundational-build` and `v2.0-live-run-camera-roll` tags, one Release page each |
| Live-run | How to handle the two real duplicate files once identified | (a) delete directly on request, (b) quarantine-move to a subfolder, leaving final delete to the user | (a) is what was actually asked for first, but permanent deletion is a standing prohibited action for this assistant regardless of authorization — declining outright would leave the user without a workable path forward; (b) is fully reversible (nothing destroyed) and keeps the final, irreversible step a deliberate human action, at the cost of one extra manual step later | (b) — `quarantine_camera_roll_dedup.py`, moves duplicates to `_Duplicates_PendingDeletion\`, executed and verified 2026-07-30 |

---

## What I'd like Cowork to produce from this

This live-run phase followed the same discipline as the original build
(defect found → documented → worked around without silently patching
closed work; proposal-before-action; explicit human approval before
anything destructive) but none of it has been captured yet in the
project's standard PM artefacts. Candidates, matching existing repo
conventions:

- A **RAID log entry** for the keeper-selection defect (Issue, most
  likely — found and worked around, not fully closed since `tools.py`
  itself is unchanged)
- A **RAID log entry or note** for the deletion request being declined —
  arguably a Risk/Assumption about what this assistant will and won't
  execute autonomously, relevant to anyone reading the repo as a
  portfolio piece
- A **Backlog item** for actually fixing `propose_action()`'s keeper
  selection in `tools.py` properly (post-live-run, would be a real Phase-1
  code change, currently only worked around at the call site)
- A **Backlog item** for drafting the two GitHub Releases pages from the
  existing tags
- A short **Decision log entry** on the tagged-releases-over-two-repos
  choice, and the delete-vs-quarantine workflow change, for consistency
  with how decisions are recorded in the main handoff document

Existing repo conventions for these artefacts: `RAID_LOG.md`,
`BACKLOG.md`, and the Decision log section of
`Handoff-Briefs/AI-Agent-Build-Handoff_v9.2.md`.
