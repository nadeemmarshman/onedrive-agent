# OneDrive AI Agent — Cowork → CODE Handoff Brief

**Purpose of this document:** Context handoff going the other direction from
`Live-Run-Handoff_v1.0.md` — written by Claude Cowork, for whichever Claude
Code ("CODE") session picks this repo up next, summarizing what Cowork did
after being handed that brief, what's still open, and one decision CODE
needs to make. Upload as a Project knowledge file if useful, or just read
directly from the repo.

**Current version: v1.0**

**Acronyms:** as defined in `GLOSSARY.md` in the repo.

---

## Relationship to the existing project

This does not replace or edit `Live-Run-Handoff_v1.0.md`, `RAID_LOG.md`,
`BACKLOG.md`, or `Handoff-Briefs/AI-Agent-Build-Handoff_v9.2.md` — it's a
new, separate document recording what happened *after* CODE's brief was
received. Read `Live-Run-Handoff_v1.0.md` first if you need the live-run
phase's own background; this document assumes that context and does not
repeat it.

---

## What happened in this Cowork session (chronological)

1. **Received `Live-Run-Handoff_v1.0.md`.** Initially had no file access;
   the user connected the `C:\Dev\onedrive-agent` folder to this Cowork
   session, after which the brief was read directly from
   `Handoff-Briefs\Live-Run-Handoff_v1.0.md` on disk.

2. **Read existing conventions before writing anything.** `RAID_LOG.md`,
   `BACKLOG.md`, and the Decision log table format in
   `Handoff-Briefs\AI-Agent-Build-Handoff_v9.2.md` (`| Phase | Decision |
   Options considered | Key trade-off | Choice |`) were read in full to
   match existing structure and ID numbering exactly, rather than inventing
   a new format.

3. **Added RAID_LOG.md entries** (currently uncommitted, working tree
   only):
   - **Issue I21** (2026-07-30) — the `propose_action()` keeper-selection
     defect (keeps `group[0]` arbitrarily; picks the OneDrive-suffixed,
     wrong file when the `" 1"` naming convention is present). Logged as
     Open, worked around at the call site, not fixed in `tools.py`.
   - **Assumption A11** (2026-07-30) — "a user's explicit authorization is
     sufficient for the assistant to execute a permanent deletion,"
     logged as Closed/disproven, referencing the declined-deletion request
     and the resulting quarantine workflow change.
   - Placement was checked against the table's existing chronological
     order before saving — this project's own I19/I20 history flags
     exactly that ordering mistake, so it was verified, not assumed. (A
     first draft briefly inserted I21 before I20; caught and corrected
     before presenting the result, not after.)

4. **Added BACKLOG.md items** (currently uncommitted):
   - **#15** — the real Phase-1 fix for `propose_action()`'s keeper
     selection (the proper fix behind RAID I21's workaround). Open,
     deliberately deferred, same "no code changes mid-phase" reasoning as
     Backlog #7/#9/#10/#11.
   - **#16** — drafting the two GitHub Releases pages from the
     already-pushed tags (`v1.0-foundational-build`,
     `v2.0-live-run-camera-roll`). Open, manual GitHub UI step only.

5. **Did not touch `AI-Agent-Build-Handoff_v9.2.md`.** The brief asked for
   two Decision log entries (tagged-releases-over-two-repos;
   delete-vs-quarantine workflow change) "for consistency with how
   decisions are recorded in the main handoff document." Since v9.2 is
   formally signed off and closed (2026-07-20), with its own
   archive-then-swap, versioned-filename convention, this was flagged to
   {{owner}} as a real decision rather than assumed. {{owner}}'s answer: **defer
   to CODE** — see "Decision needed from CODE" below.

6. **Flagged, did not fix: `docs/RAID_Log.xlsx`.** This file is generated
   by `build_raid_log.py`, which has the RAID data hardcoded inline in the
   script rather than parsed from `RAID_LOG.md` — it was already stale
   before this session (stuck around item R1) and is now further out of
   sync after I21/A11 were added to the `.md`. Not regenerated; flagged as
   a separate cleanup task, not bundled into this session's edits.

7. **Separate, non-canonical artifact exists — do not confuse with this
   repo.** Earlier in this same Cowork session, before folder access was
   connected, a standalone documentation-only git repo
   (`onedrive-liveagent-docs`) was built in Cowork's own sandbox, containing
   placeholder/PM-artifact drafts (charter, WBS, RAID-equivalent, etc.)
   with fictional "Pending" test statuses, tagged `docs-v1.0-foundational-build`
   / `docs-v2.0-live-run-camera-roll`. It has **no connection** to this real
   repo, was never pushed anywhere, and is not authoritative — mentioned
   here only so it isn't mistaken for a second real source if it ever
   surfaces (e.g. in a future upload). This repo (`onedrive-agent`) remains
   the single canonical source.

---

## Current state

- ✅ RAID_LOG.md: I21, A11 added, correctly ordered, verified via `git diff`
  (clean, additive-only — 2 lines added, nothing else touched)
- ✅ BACKLOG.md: #15, #16 added, verified via `git diff` (clean,
  additive-only — 2 lines added)
- ⬜ **Not committed.** Both files are modified in the working tree only;
  `git status` confirms `M BACKLOG.md`, `M RAID_LOG.md`, alongside the
  already-staged, still-uncommitted `Handoff-Briefs/Live-Run-Handoff_v1.0.md`
  from CODE's own last session. Left uncommitted deliberately — commit
  timing/message is CODE's or {{owner}}'s call, not assumed by this session.
- ⬜ **Decision log entries not written anywhere yet** — see below.
- ⬜ Backlog #15 (real `tools.py` fix) and #16 (GitHub Releases pages) —
  both still open, as they were before this session.
- ⚠️ **Action needed on this machine:** a stray `.git/index.lock` file was
  observed in this repo's `.git` folder while running read-only `git
  status`/`git diff` commands from this Cowork session's sandbox (a
  mount-related quirk of this sandbox, not a real lock held by any actual
  process). If CODE's next `git commit` in this repo fails with "Unable to
  create '.git/index.lock': File exists," delete that file first (safe —
  it's a leftover artifact, not an active lock) and retry.

---

## Decision needed from CODE

**Where should the two live-run Decision log entries go?**

1. **New "Decision log" section inside `Live-Run-Handoff_v1.0.md` itself**
   (same table columns as v9.2's) — keeps v9.2 permanently untouched as the
   true closed record.
2. **Reopen v9.2 as v9.3**, following the project's own archive-then-swap
   convention, with the two entries appended as a clearly-labeled
   post-closure/live-run addendum.
3. Some other approach CODE prefers — it's the author of both the brief and
   the v9.2 convention, so best placed to judge which reading of "for
   consistency with the main handoff document" was intended.

{{owner}} was asked this directly in Cowork and chose to defer it to CODE
rather than guess.

---

## What I'd suggest CODE/{{owner}} do next

- Review the RAID_LOG.md / BACKLOG.md diffs above, commit if they look
  right (commit message suggestion: `Live-run phase: log RAID I21/A11 and
  Backlog #15/#16 (via Cowork)`).
- Decide and action the Decision log placement question above.
- Delete the stray `.git/index.lock` if the next commit fails on it.
- Backlog #16 (GitHub Releases pages) is the last step before the two
  resume URLs are live — small, manual, and currently the only thing
  between this phase and being résumé-ready.
