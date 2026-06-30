# OneDrive Agent — Product Backlog & Daily Scrum Log

**Purpose:** Agile/Scrum-style tracking artifact for this project, forming
part of the portfolio of evidence. Demonstrates lightweight application of
Scrum practices to a solo technical build — adapted deliberately, with the
adaptation made explicit (see footnotes) rather than presented as textbook
Scrum, since this project does not run fixed time-boxed Sprints.

## Update log (this file)

| Date | Change |
|---|---|
| 2026-06-28 | File created as "Backlog & Daily Standup Log"; Phase 3 closeout checklist item and test-pack backlog item #1 logged. |
| 2026-06-28 | Retitled to correct Scrum terminology ("Daily Scrum" rather than the colloquial "standup"); retrospective-style questions folded into each Daily Scrum entry rather than run as a separate ceremony, since this project has no fixed Sprint boundary for a true Sprint Retrospective; methodology footnotes added throughout; applied retroactively to the existing entry below without altering its original date or content, only its structure/labeling. |
| 2026-06-28 | Corrected the Daily Scrum entry to explicitly note that this file's own creation, and the fact it was not yet committed/pushed to GitHub, had been stated in chat but omitted from the artifact itself — added as a blocker/status note, since the Daily Scrum log should reflect everything discussed, not just a subset. |

---

## Product Backlog¹

Status values: **Open** (not yet discussed) | **In Discussion** | **Actioned**
(decision made, reflected in handoff doc/README — the Product Backlog item
is then analogous to a closed/delivered Backlog Item²) | **Deferred**
(explicitly out of scope for now, with reason) | **Rejected** (considered,
not adopted, with reason)

| # | Raised | Item | Status | Notes |
|---|---|---|---|---|
| 1 | 2026-06-28 | Testing strategy and test case design as a separate deliverable: develop test packs, segregated "on paper" by functionality (a design artifact distinct from the actual test code). Add a dedicated test pack for state-transition test cases (tied to the Phase 4.5 state-machine design). | Open | Raised alongside the state-machine framing discussion for Phase 4.5. Fits naturally with the existing two-layer (unit/integration) testing standing rule — this would sit "above" that as a planning artifact, not replace it. |
| 2 | 2026-06-28 | Frame Phase 4.5's restart-and-resume mechanism explicitly as a state machine (named states + transitions + persisted current-state), rather than ad hoc retry/variable-saving logic — including the safety property that `AWAITING_HUMAN_APPROVAL` must never be silently skipped past on resume. | Actioned | Added to handoff doc v4.0, "Note on Phase 4.5" section, with a proposed state diagram. Implementation deferred to when Phase 4.5 is actually built — this entry records the design decision, not the code. |

---

## Daily Scrum Log³

Held at the start of each working session. Three core questions (per the
Scrum Guide's Daily Scrum⁴), with a fourth, retrospective-style question
added to capture continuous-improvement thinking without requiring a
separate, Sprint-boundary-dependent ceremony⁵:

1. **What did we complete or solve since the last session?**
2. **What's planned / where are we headed next?**
3. **Any blockers?**
4. **Retrospective note⁶ — what did we miss, learn, or newly identify** (process or scope) that wasn't yet captured in the project artifacts, and has it been added to the Product Backlog?

| Date | Completed/solved since last session | Planned next | Blockers | Retrospective note |
|---|---|---|---|---|
| 2026-06-28 | Phase 3 confirmed complete in chat (live API call succeeded; error handling added). Phase 4.5 scoped and inserted into the plan (handoff doc v4.0 drafted). This `BACKLOG.md` file itself created and restructured to correct Scrum terminology. | Phase 4 build (core decision-execution loop), gated on Phase 3 closeout being confirmed done by {{owner}}. | Phase 3 closeout checklist outstanding (6 items — doc swap, local file saves, git commit/push). SendGrid account setup outstanding, needed before Phase 4.5. **`BACKLOG.md` itself is not yet committed/pushed to GitHub** — not part of the Phase 3 closeout checklist (didn't exist when that checklist was set), so it doesn't block Phase 4, but should be folded into the next git commit. | Identified that "restart-and-resume" is genuinely state-machine logic, not ad hoc retry logic — added to Product Backlog as a design approach for Phase 4.5, not yet formally scoped into the handoff doc. Also identified that test-case design itself deserves to be a separate, "on paper" deliverable (test packs) rather than only living as test code — added as Backlog item #1. |
| 2026-06-28 | State-machine framing for Phase 4.5 actioned: added to handoff doc v4.0 (still open, not yet version-bumped, since Phase 3's closeout checklist — not this content — is what gates progress). Backlog item #2 marked Actioned. | Still gated on Phase 3 closeout checklist confirmation by {{owner}} before Phase 4 build begins. | Same as above — Phase 3 closeout checklist and SendGrid setup both still outstanding. `BACKLOG.md` still not yet committed to GitHub. | Confirmed the distinction between "raising/discussing an idea" (Backlog) and "deciding and documenting it" (handoff doc) is working as intended — the state-machine idea moved cleanly from Backlog item #2 into the handoff doc's Phase 4.5 section without needing a version bump, since v4.0 was still open. |
| 2026-06-29/30 | Phase 3 closeout checklist worked through with {{owner}}, verified via screenshots at each step (handoff doc v4.0 swap confirmed in Project knowledge + local archive; `decision_loop.py` committed/pushed). New standing rule adopted mid-checklist: verbal "done" confirmations alone are no longer sufficient — screenshot or equivalent visual evidence now required before marking a checklist item confirmed. | Phase 4 build (core decision-execution loop) — checklist now fully closed, no longer gated. | None remaining for Phase 4. SendGrid setup + `SENDGRID_API_KEY` (items 8–9) still outstanding, but these gate Phase 4.5, not Phase 4. | **Caught a real error via the new screenshot-verification rule**: an initial attempt to commit `README.md` and `BACKLOG.md` actually used `echo "..." > file` commands, which overwrote both files with one-line placeholder text instead of adding the real, previously-generated content — confirmed by the commit's `84 deletions(-)` stat and matching file-modified timestamps. Caught before being accepted as "done," corrected by re-downloading and re-saving the real files, then re-committing — verified this time via `git show HEAD:README.md` showing the actual file content (not just commit stats) live on GitHub. Direct, concrete evidence that verbal/stat-only confirmation is insufficient and the screenshot+content-verification rule is justified, not just process overhead. |
| 2026-06-30 | Built `RAID_LOG.md` and `RAID_Log.xlsx` (via `build_raid_log.py`) at {{owner}}'s request — a standard PM control artifact (Risks, Assumptions, Issues, Dependencies) separate from this Scrum tracking file. Retroactively decomposed the placeholder-overwrite incident into proper RAID components (R2 risk, A1 assumption, I1 issue), demonstrating the framework's analytical use rather than just adopting its name. | Phase 4 build, once a short "Phase 3.5" documentation closeout (RAID log files saved/committed, README repo-contents list updated) is confirmed by {{owner}}. | RAID log files not yet saved locally or committed to GitHub. | Caught that the README's "Repo contents" list had silently gone stale — `decision_loop.py` and `BACKLOG.md` were both already in the repo but never added to that list when first created, only noticed while adding the RAID log entry. Fixed in this session. A small instance of the same underlying pattern as Issue I1 (documentation drifting from actual repo state) — but caught proactively this time, before being committed, rather than after. |
| 2026-06-30 12:03 | Adopted new standing rule: Claude does not have a reliable live clock and cannot accurately timestamp chat responses or infer {{owner}}'s local time — {{owner}} now states the date/time explicitly alongside checklist confirmations and logged events, and Claude uses that rather than approximating "today." | Phase 4 build, once Phase 3.5 documentation closeout (RAID log files committed) is confirmed. | Same as previous entry — RAID log files not yet committed. | Recognized that several existing log entries above (e.g. the 2026-06-28/29/30 entries) were dated by Claude's approximation rather than a date {{owner}} explicitly confirmed — these are left as-is rather than retroactively rewritten, since the approximate dates are still reasonably accurate, but this entry marks the point from which dates are sourced from {{owner}} directly, not inferred. |
| 2026-06-30 12:44 | **Phase 3.5 documentation closeout fully confirmed and verified**: handoff doc v4.0 → v4.1 swap in Project knowledge (screenshot, 12:42), v4.0 archived locally (screenshot, 12:44), `RAID_LOG.md`/`RAID_Log.xlsx`/`build_raid_log.py`/`README.md`/`BACKLOG.md` all committed and pushed (earlier screenshot + `git ls-tree` verification, commit `6e657d0`). No open items remain. | **Phase 4** — execute the tool(s) Claude decides to call, feed results back as observations, loop until goal complete or a stopping condition is hit. Must explicitly handle the 5 proactive-design risks named in the standing rule (zero/multi tool calls, malformed arguments, unrecognized tool names, loop termination, API failures carried into the loop). | None — fully unblocked for Phase 4. SendGrid setup (items D3 in RAID log) still outstanding but only gates Phase 4.5. | The earlier missed-commit incident (staged files, no commit, "Everything up-to-date" on push) was caught and self-corrected by {{owner}} before being reported as done — a good example of the screenshot-verification habit being internalized rather than only enforced by Claude asking for evidence. Not yet formally logged as a RAID Issue, since it was self-caught and resolved within the same exchange; noted here for completeness. |

---

## Footnotes (methodology reference)

1. **Product Backlog** — standard Scrum artifact: an ordered list of
   everything that might be needed, not yet committed to a Sprint. Used
   here for ideas/scope questions raised mid-build, before being actioned
   into the handoff document.
2. In real Scrum, Backlog Items are typically refined into a Sprint
   Backlog and "Done" per a Definition of Done. This project substitutes
   "Actioned → reflected in handoff doc/README" as its lightweight
   equivalent, given there is no formal Sprint cycle.
3. **Daily Scrum** is the correct Scrum Guide term (commonly nicknamed
   "stand-up" in industry, but "Daily Scrum" is the formal name used here
   deliberately).
4. The Scrum Guide's three Daily Scrum questions are adapted here as
   "what did we complete," "what's planned," and "blockers" — functionally
   equivalent to "what I did yesterday / what I'll do today / impediments."
5. A **Sprint Retrospective** is formally an end-of-Sprint ceremony focused
   on process improvement, requiring a fixed Sprint boundary. This project
   is phase-driven with irregular session cadence, not time-boxed Sprints,
   so a separate Retrospective ceremony would misuse the term. Instead,
   retrospective-style reflection is folded into each Daily Scrum entry —
   an explicit, intentional adaptation, not a terminology error.
6. This column is the project's adapted substitute for a Sprint
   Retrospective's "what went well / what didn't / what will we change"
   reflection — scoped to a single working session rather than a Sprint.
