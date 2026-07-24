# AI Agent Build — Handoff Brief

**Purpose of this document:** This is a context handoff for a project in progress, written so Claude (in a new chat, with no prior memory) can pick up exactly where things left off. Upload this as a Project knowledge file.

**Current version: v6.0**

## Version History

| Version | Date | Summary of Change | Reason |
|---|---|---|---|
| v1.0 | 2026-06-26 | Initial handoff document created — project context, 6-phase plan, decisions made, resume instructions | Free tier has no cross-conversation memory; needed a persistent context anchor for the Project knowledge file |
| v1.1 | 2026-06-26 | Added "Standing rule" section instructing Claude to proactively offer to regenerate this document at the start of each new phase or after significant decisions | Prevent the document from going stale as the build progresses across sessions |
| v2.0 | 2026-06-26 | Added Phase 7 (compare hand-built agent to Claude Cowork) as a new structural step at the end of the plan, with supporting note on access requirements and rationale | New phase changes the scope/structure of the plan (MAJOR change), not just a status update (MINOR) |
| v2.1 | 2026-06-26 | Added standing rule requiring Claude to spell out concrete action steps whenever a rule applies (e.g. file swap, archiving), rather than just stating the rule or that an update occurred | Rules without explicit prompted actions were being stated but not actively surfaced as to-dos — closing that gap |
| v2.2 | 2026-06-26 | Updated Phase 0 status (GitHub confirmed, API key deliberately deferred — new blocker); added new standing rule for logging decision trade-offs (pros/cons/risks) at the point of choice; recorded first three Phase 1 design decisions with their trade-offs | Status update + new tracking practice = MINOR (no change to overall scope/structure); decisions logged retroactively under the new practice |
| v2.3 | 2026-06-26 | Phase 1 marked complete: `tools.py` built and tested against sample data, repo created and pushed to GitHub (`onedrive-agent`, currently Private); local project structure decisions recorded (code on local C: drive, away from OneDrive sync; handoff docs stay under OneDrive for backup); added repo-visibility (Private → Public) as an explicit Phase 6 to-do; Phase 2 now in progress | Status update / phase completion = MINOR (no change to overall scope/structure) |
| v3.0 | 2026-06-26 | Phase 2 marked complete: `tool_contracts.py` (JSON-schema tool contracts) written for all four Phase 1 functions; added new standing rule requiring a two-layer test structure (unit tests, then integration tests, in that order) for every phase that adds new functions, with scope expanding as the project grows; `test_phase2.py` rebuilt to this structure (14 unit tests + 4 integration tests, all passing); README updated with a "Testing approach" section reflecting this practice; Phase 3 now next | New standing rule changes how all future phases must be built and tested — a structural/process change, not just a status update (MAJOR) |
| v3.1 | 2026-06-28 | Phase 3 marked complete: `decision_loop.py` built and successfully called the live Anthropic API; Claude correctly read the four tool contracts and chose to call `find_duplicates` and `find_convertible_files` in the same turn (recognizing they're independent); added a new standing rule on proactive design (deliberately designing for things that will reliably occur in an LLM-driven agent, rather than relying on incidental code structure that happens to work); added an explicit out-of-scope list with reasons; README updated with a "Design philosophy" section reflecting this; Phase 4 now next | New standing rule changes how all future phases are designed (not just tested) — a structural/process change (MAJOR) |
| v3.2 | 2026-06-28 | Closed a gap between documentation and code: v3.1 named API/network failure handling as a proactive-design risk but `decision_loop.py` had no actual error handling yet. Added specific handling for authentication failure, rate limiting, connection failure, and general API errors (e.g. insufficient credit) — each returns cleanly with an actionable message instead of a raw crash. Verified via a standalone simulation of each failure branch. | Implementing a rule already documented (not introducing a new one) = MINOR (no change to scope/structure) |
| v4.0 | 2026-06-28 | Inserted a new **Phase 4.5: Resilience & Alerting** between Phase 4 and Phase 5 — covers email alerting on serious/unhandled failures (via SendGrid, to a configurable recipient list) and state persistence enabling restart-and-resume after an abrupt stop (e.g. load shedding / power loss), kept structurally separate from Phase 4's core decision-execution loop so each phase's portfolio narrative stays focused. Logged as a Decision log entry (split vs. merge into Phase 4). Phase 3 reconfirmed closed; Phase 4 next. | New phase inserted into the plan — scope/structure change (MAJOR) |
| v4.1 | 2026-06-30 12:03 | Added new standing rule: Claude cannot reliably timestamp chat responses or infer local time, so {{owner}} now states the date/time explicitly alongside checklist confirmations and logged events, rather than Claude approximating "today." Also: Phase 3.5 documentation closeout completed — `RAID_LOG.md`/`RAID_Log.xlsx`/`build_raid_log.py` created (Risks, Assumptions, Issues, Dependencies log, separate from `BACKLOG.md`'s Scrum tracking), README "Repo contents" list corrected (had silently gone stale, missing `decision_loop.py` and `BACKLOG.md`), all committed/pushed and verified via `git ls-tree`. | New standing rule (date/time sourcing) = structural/process change (MAJOR); documentation closeout itself is a status update, bundled into the same version since both landed in the same session |
| v4.2 | 2026-06-30 23:50 | Phase 4 marked complete: `agent_loop.py` built and run successfully end-to-end against the live Anthropic API. Full decide → execute → observe → repeat loop proven: Claude called two tools in parallel in iteration 1, chained their results into a third tool call in iteration 2, then correctly stopped on its own in iteration 3 (natural termination, not the MAX_ITERATIONS safety cap). All 5 proactive-design risks explicitly handled in code. No files modified or deleted — agent correctly deferred to Phase 5's human-approval gate. Phase 4.5 (Resilience & Alerting) next, gated on SendGrid setup. | Phase completion = MINOR (status update, no structural/scope change) |
| v4.3 | 2026-07-01 16:04 | Phase 4.5 marked complete: `resilience.py` built and committed — email alerting via SendGrid (`alert_on_error()` fires on ERROR-level events only, sends to configurable recipient list `nadeemmarshman@gmail.com` + `narshman@duck.com`) and explicit state machine (`SCANNING → AWAITING_DECISION → EXECUTING_TOOL → AWAITING_HUMAN_APPROVAL → DONE`) with state persisted to `agent_state.json` at each transition. `AWAITING_HUMAN_APPROVAL` safety guarantee implemented: resume logic raises a prominent warning and never auto-skips past this state. `agent_loop.py` updated with Option A lean structured logging (INFO/WARNING/ERROR level discipline). `.gitignore` added (excludes `logs/`, `__pycache__/`, `.env`). RAID log D3 (SendGrid) updated to Active. Phase 5 (human-approval gate) next. | Phase completion = MINOR (status update, no structural/scope change) |
| v4.4 | 2026-07-01 17:16 | Added pre-Phase-5 quality gate condition to Phase 5 row in the plan table, status section, and "How to resume" section — formalising that `test_phase3_4_45.py` (negative/red-line test suite) and enriched alert troubleshooting messages (Backlog items #3 and #4) must be committed before Phase 5 build begins. Documented the GRC rationale: this is assurance work on capabilities already built, tracked in the Backlog rather than as a new phase, per the distinction between delivery controls and quality controls. | Status/gate-condition update = MINOR (no new phase, no new standing rule) |
| v4.5 | 2026-07-01 23:01 | Pre-Phase-5 quality gate confirmed complete and committed (commit `a8fce07`): `test_phase3_4_45.py` (34 tests — 31 unit + 3 integration, all passing, covering explicit negative/red-line scenarios for Phases 3, 4, and 4.5); `resilience.py` enriched with 7 named alert functions structured around a 5W incident-management framework (WHAT/WHEN/WHERE/TRIGGERED BY/WHY/STEPS), graduated urgency, `_masked_user_id()` partial credential masking, and README-reference pattern on all commands; RAID R5 added (alert email credential exposure, Monitoring); Backlog items #3 and #4 marked Actioned. Phase 5 (human-approval gate) is next. | Pre-Phase-5 gate completion = MINOR (status update, no new phase or standing rule) |
| v4.6 | 2026-07-02 10:01 | Phase 5 complete: `approval_gate.py` built — pre-run manifest snapshot as a governance precondition ("no snapshot, no actions"), full proposal list review, per-item approve/reject, skips rejected actions and continues, executes only approved actions. Proven in a live run: invalid input caught and re-prompted, real file deleted on approval, rejected action correctly skipped, convert stub logged. Test suite extended to 45 tests (40 unit + 5 integration, all passing), covering Phase 5 approval gate scenarios. RAID I4 added (snapshot precondition, Closed). BACKLOG item #5 added (user roles and assignment, Open). Handoff doc Decision log updated with DR/rollback Option A vs B trade-off. Phase 6 (polish) next. | Phase 5 completion = MINOR (status update, no structural/scope change) |
| v4.7 | 2026-07-02 12:06 | Phase 6 complete: full README written (problem → approach → architecture → governance → testing → current state → repo contents → run instructions); architecture diagram built as standalone SVG (`architecture.svg`) and linked inline from README; user roles design decision recorded (single-user model, multi-role as logged future consideration, Backlog item #5 marked Actioned); repo switched from Private to Public at `github.com/nadeemmarshman/onedrive-agent`. README renders with architecture diagram visible on the repo landing page. Phase 7 (Cowork comparison) planned; resume bullets and market positioning discussion next. | Phase 6 completion = MINOR (status update, no structural/scope change) |
| v4.8 | 2026-07-02 13:48 | Phase 7 complete: Claude Cowork comparison run on `sample_data/` using `claude-sonnet-5` (released 2026-06-30) vs hand-built agent using `claude-sonnet-4-6`. Key findings: Cowork reached the same conclusions on all test cases (same duplicate, same near-miss exclusion, same conversion candidate) — core agent logic validated. Hand-built version differs in governance layer (pre-run snapshot, structured logging, email alerting, state machine resilience) not visible in Cowork output. Cowork added one out-of-scope suggestion (rename recommendation). Model capability one-liner added to README. RAID A6 added (model version reproducibility assumption). All phases now complete. | Phase 7 completion = MINOR (status update, no structural/scope change) |
| v5.0 | 2026-07-02 22:03 | Independent Claude Cowork peer review completed and remediated: found and fixed a critical test isolation bug (Phase 5 integration tests were deleting real `sample_data/` fixture files on every run — root cause and fix documented in new `REMEDIATION_2026-07-02_cowork-peer-review.md`) plus 3 minor documentation drifts (broken cross-reference, stale RAID status, incorrect count). Agent's own model switched from `claude-sonnet-4-6` to `claude-sonnet-5`, aligning all three surfaces (Claude Chat, Cowork, agent API calls) — see Decision log item 7. New Phase 8 (UAT/Pilot, deliberately not POC — see Decision log item 8) added to the plan: validate against a real, limited OneDrive subset before full rollout. SDLC retrospective mapping added to README. Two new standing rules: confirm before producing files for download; SDLC terminology labeling applied project-wide. | New standing rules + new phase (UAT/Pilot) + structural terminology correction = MAJOR (process and scope change, not just a status update) |
| v6.0 | 2026-07-05 07:18 | Cross-project fact-check and sync contract with the Job Search — Resume & LinkedIn project completed. This project fact-checked the résumé/LinkedIn portfolio bullets against the live repo, finding and correcting: "production-grade" overstatement, wrong RAID issue count, Phase 7/peer-review conflation, 45-test figure wrongly pinned to the pre-Phase-5 gate, format-conversion described as executing rather than proposing, and a dead non-hyphenated repo slug on LinkedIn. All corrections applied on the Job Search side; the master résumé's PORTFOLIO PROJECT bullet set is now the canonical fact-set there (variants regenerated from it). New standing sync contract adopted (see new section below): this project is guardian of Phase status (README build-plan table) and the repo slug, and must proactively notify the Job Search project when Phase 8 completes or its status changes. RAID-count guardianship was offered but is moot — {{owner}} decided to drop quantified RAID numbers from the résumé (drift-proofing). Résumé stays `.md` until a `.docx` conversion is requested at send-time (owned by the Job Search project); this project's send-time duty is the repo pre-publish check (public / README current / Phase 8 status accurate), run on request. | New standing cross-project obligation (proactive Phase 8 status notification + named guardian roles) = process/structural change (MAJOR), not just a status update |
| v5.1 | 2026-07-04 18:24 | Reviewed and resolved four cross-project "refinement" suggestions from the Job Search — Resume & LinkedIn Claude project, which had been written without full context of this project's code. One (a proposed demo capture via `agent_loop.py`) was rejected — it incorrectly assumed that script invokes the approval gate, when only `test_phase5_live.py` does. Three were implemented through this project's own verification process: sourced the SWE-bench Pro benchmark claim in the README with a direct citation (independently re-confirmed via search first); moved `RAID_Log.xlsx` and the remediation report into a new `docs/` folder, with a reference check that — unlike the original instructions — correctly included the handoff document (confirmed its only mentions are historical version-history entries that correctly stay unedited); relocated the README's "Project location and key paths" section below the build narrative. A `LICENSE` file (MIT) was also added directly on GitHub via the web UI and merged in without conflict. GitHub repo contents updated below to reflect `docs/` and `LICENSE`. Phase 8 (UAT/Pilot) remains the next and only outstanding step. | Status/repo-contents update = MINOR (no new phase, no new standing rule) |

---

## Who I am / context

{{owner}} — hybrid Business Analyst / IT Project Manager based in Johannesburg, South Africa. Targeting both BA and PM roles. Currently unemployed and job hunting. Background includes First National Bank (BA-focused), NCR Atleos/Altron (PM-focused), Agile delivery, payments systems, stakeholder management. Holds a Diploma in Business Analysis and Project Management, PSM I certification. No PMP/PRINCE2.

This Project ("Career Portfolio & Job Search") holds career portfolio work generally — resume drafting, job search tracking, and technical portfolio projects. This document covers one specific build within that Project.

---

## The project: build a small, portfolio-grade AI agent

**Origin of the idea:** Started from a practical task (cleaning up duplicate/bloated files in OneDrive) but was deliberately reframed as a *learning + portfolio* exercise rather than just getting the cleanup done. The OneDrive cleanup is the live example/use case the agent operates on — not the end goal in itself.

### Why this project, specifically

I'm a BA/PM with strong Agile and stakeholder skills, but no hands-on technical build artifact. Many BA/PM candidates can talk about AI conceptually; few can point to something they actually built. This project is meant to:

1. **Differentiate on my resume** — e.g. a bullet like: *"Designed and built a tool-calling AI agent (Python + Anthropic API) automating file deduplication and format optimization, including a human-in-the-loop approval gate for destructive actions."*
2. **Serve as a portfolio artifact** — something to show in an interview, walk through live, or link to (GitHub repo with a clean README).
3. **Demonstrate BA/PM discipline applied to a technical build** — framed as requirements → design → build → safety/governance, not just "I learned to code."

### What I'll personally walk away with

- A working (if small) agent that organizes a real folder
- A clear mental model of the agent loop: **tool-definition → decision → action → observation**
- Reusable knowledge for evaluating any agent product (Claude Code, MCP connectors, Cowork, etc.) since they all run on this same loop at larger scale

---

## The core concept (agent loop)

An "agent" is fundamentally:

1. **Tools** — discrete functions with a defined input/output contract (e.g. `list_files(folder)`, `get_file_hash(path)`, `delete_file(path)`)
2. **Decision (the LLM)** — given a goal and current state, the model decides which tool to call and with what arguments
3. **Action** — the tool actually executes
4. **Observation** — the result feeds back to the model
5. Repeat until the goal is done

Every agent product (Claude Code, Claude in Chrome, MCP connectors) is this same loop with different tools plugged in. This build makes that loop small, visible, and hand-built so I understand it directly rather than just using a finished product.

---

## The 6-phase plan

| Phase | What we build | Portfolio angle / README section |
|---|---|---|
| 0 | Confirm GitHub + Python + API key | Setup (not shown in portfolio) |
| 1 | Define tools as plain Python functions (no AI yet) — e.g. `scan_folder()`, `find_duplicates()`, `find_convertible_files()`, `propose_action()` | "Requirements & functional design" |
| 2 | Wrap each function with a JSON-schema tool contract (name, description, parameters) — same format used by MCP and the Anthropic API | "Technical design / tool contracts" |
| 3 | Build the decision loop manually via the Anthropic API (a script, not claude.ai) — send goal + tool definitions + folder state, Claude responds with a structured tool call | Core build — the actual agent |
| 4 | Execute the chosen tool, feed result back, let Claude decide the next step, loop 3–4 iterations on a real/sample OneDrive folder | Demo / walkthrough section (maybe screen recording) |
| 4.5 | Resilience & Alerting: email alerts (via SendGrid) on serious/unhandled failures during the loop, sent to a configurable recipient list; state persisted to disk at each meaningful step so the agent can restart-and-resume after an abrupt stop (e.g. load shedding / power loss) rather than losing progress | "Operational resilience" — a differentiator reflecting real local constraints (budget, power stability), not just textbook agent design |
| 5 | Add a human-approval gate before any destructive action (e.g. deletion) executes. **Gated on a pre-Phase-5 quality assurance step** (not a separate phase — a Definition of Done condition): `test_phase3_4_45.py` (negative/red-line test suite for Phases 3, 4, and 4.5) must be written and committed, and `resilience.py` alert messages must be enriched with per-error troubleshooting instructions, before Phase 5 build begins. This is assurance work on capabilities already built, tracked in the Backlog (items #3 and #4) rather than as a new phase, per GRC best practice distinguishing delivery controls from quality controls. | "Risk & governance" — the BA/PM differentiator |
| 6 | Polish: clean documented code, README (problem → approach → architecture → outcome), Git/GitHub repo, optional architecture diagram, draft resume bullet | The actual shareable/linkable deliverable |
| 7 | Compare the hand-built agent to Claude Cowork (Anthropic's own production agent) — try Cowork (e.g. a free trial of Pro, if available) on a similar file-organizing task and note where it matches/exceeds the hand-built version, and why | "Evaluating other agent products" section in README — demonstrates I can assess production agent tooling, not just build a toy one |
| 8 | UAT/Pilot — validate the agent against a real, limited subset of live OneDrive data immediately before full production rollout. Deliberately labelled UAT/Pilot, not POC — the POC stage (proving technical feasibility) was effectively already covered by Phases 1–4 against synthetic `sample_data/`. This stage validates the already-built, already-tested solution against real conditions. | "Deployment readiness" — demonstrates disciplined go-live practice, not just "it worked on test data" |

**Note on Phase 4.5:** "Restart-and-resume" means the *script itself* checks for saved, unfinished state on startup and resumes from there rather than starting blind — it does not mean the script can make itself run again after the whole machine reboots (that requires an OS-level mechanism, e.g. Windows Task Scheduler configured to run the script at logon/startup). This distinction will be made explicit when this phase is built, so the README doesn't overstate what the Python code alone provides.

**Phase 4.5 design approach: explicit state machine.** Restart-and-resume is genuinely state-machine logic, not ad hoc retry logic, and should be designed and documented as such rather than as "save some variables and hope." A state machine is a model where the system is always in exactly one of a defined, finite set of **states**, moves between them via defined **transitions**, and — the property that matters here — its current state can be inspected and recorded independently of whether the program is currently running. That last property is exactly what surviving a power loss requires: resuming correctly depends on a well-defined, nameable state ("scanning," "awaiting Claude's decision," "executing tool X," "awaiting human approval") having been written to disk *before* the interruption, not an arbitrary dump of in-progress variables.

Proposed states for this agent (to be finalized when Phase 4.5 is actually built):

```
SCANNING → AWAITING_DECISION → EXECUTING_TOOL → AWAITING_HUMAN_APPROVAL → DONE
                  ↑_________________________________|
                  (loop back for the next decision)
```

The safety-relevant reason this matters, not just the engineering-cleanliness reason: **`AWAITING_HUMAN_APPROVAL` is a state the restart logic must never silently skip past.** If power cuts out after Claude proposes a deletion but before the human approves it, resuming must land back in "still waiting for approval" — never auto-resume into "proceed with the deletion." Modeling this explicitly as named states makes that guarantee checkable (each state and its allowed transitions can be unit-tested) rather than relying on incidental code structure to happen to preserve it — directly consistent with the project's existing proactive-design standing rule.

Scope note, to avoid over-engineering: this means a **simple, explicit state machine** — a small, named set of states plus a single "current state + minimal supporting data" written to a JSON file — implemented in plain Python. It does **not** mean adopting an external state-machine framework/library, which would be disproportionate to this project's scale. The README should name this explicitly as a state machine (a recognizable, correct systems-design term), while being honest that the implementation is intentionally minimal.

**Note on Phase 7:** Cowork is essentially Anthropic's own polished version of the exact tool-definition → decision → action loop built by hand in Phases 3-4. Comparing the two — after, not before, building my own — is the point: it shows I understand the mechanics well enough to evaluate a finished product critically, rather than just using it. Requires a paid plan (Pro/Max/Team/Enterprise) and macOS or Windows; not available on the free tier. Do this last, once Phases 1-6 are complete.

**Status: Phases 1–7 complete; Phase 8 (UAT/Pilot) planned. Repo public at `github.com/nadeemmarshman/onedrive-agent`. Independent Cowork peer review completed and all findings remediated (2026-07-02). Resume bullets drafted (private).**
- Python: ✅ confirmed installed — Python 3.14.5, 64-bit, Windows
- GitHub account: ✅ confirmed
- Anthropic API key: ✅ activated — billing set up on console.anthropic.com, key created (named `onedrive-agent`), stored safely outside any code file, loaded via the `ANTHROPIC_API_KEY` environment variable (Windows User-level variable). Never hardcoded into any script.
- SendGrid account: ⏳ in progress — needed for Phase 4.5's email alerting. Requires account creation, Single Sender Verification (verifying one "from" email address), and an API key with Mail Send permission only. Key will be stored the same way as the Anthropic key, as a second environment variable (`SENDGRID_API_KEY`).
- Alert recipients (for now): `nadeemmarshman@gmail.com`, `narshman@duck.com` — to be built as a configurable list, not hardcoded, since the real distribution list may change later.
- `anthropic` Python package: ✅ installed (`anthropic-0.112.0`). Note: initial `pip install anthropic` failed on this machine due to a `tokenizers` dependency trying to compile from Rust source (no Rust compiler present) — resolved by updating pip first (`python -m pip install --upgrade pip`), after which a prebuilt wheel installed cleanly. Worth knowing if this resurfaces on a fresh machine.
- Phase 1 (`tools.py`): ✅ complete — `scan_folder()`, `find_duplicates()`, `find_convertible_files()`, `propose_action()` built and tested against a planted sample folder.
- Phase 2 (`tool_contracts.py`): ✅ complete — JSON-schema tool contracts written for all four Phase 1 functions, in the exact format the Anthropic API and MCP use. Validated via `test_phase2.py`: 14 unit tests (per-function, including edge cases) + 4 integration tests (contract validation + full chained flow), all passing.
- Phase 3 (`decision_loop.py`): ✅ complete — first live Anthropic API call succeeded. Sent a goal + the four tool contracts + real scanned folder state; Claude responded with `stop_reason: tool_use` and chose to call **both** `find_duplicates` and `find_convertible_files` in the same turn, correctly reasoning they're independent of each other. This phase proves the decision step only — no tool execution or looping yet (that's Phase 4). **API error handling implemented**: authentication failure, rate limiting, connection failure, and general API errors (e.g. insufficient credit) are each caught specifically and exit gracefully with an actionable message rather than a raw crash.
- Phase 4 (`agent_loop.py`): ✅ complete — full decide → execute → observe → repeat loop proven end-to-end against the live API (2026-06-30 23:50). Three iterations: Claude called `find_duplicates` + `find_convertible_files` in parallel (iteration 1, both genuinely executed with real results returned); independently chained those results into a `propose_action` call (iteration 2); returned zero tool calls + clean summary in iteration 3, triggering the natural loop-termination condition — not the MAX_ITERATIONS safety cap. No files modified or deleted; human approval (Phase 5) explicitly required before any action executes. All 5 proactive-design risks explicitly handled in code. Lean structured logging added (Option A: abbreviated INFO, full detail on WARNING/ERROR, timestamped log file per run under `logs/`).
- Phase 4.5 (`resilience.py`): ✅ complete — email alerting via SendGrid (`alert_on_error()` sends to configurable recipient list on ERROR-level events only); explicit state machine (`SCANNING → AWAITING_DECISION → EXECUTING_TOOL → AWAITING_HUMAN_APPROVAL → DONE`) with state persisted to `agent_state.json` at each transition; `AWAITING_HUMAN_APPROVAL` safety guarantee: resume logic never silently skips past this state. Committed 2026-07-01 16:04.
- Phase 5 (`approval_gate.py`): ✅ complete — pre-run manifest snapshot (`pre_run_snapshot.json`) as governance precondition ("no snapshot, no actions"); full proposal list presented for review before any prompts; per-item approve/reject with invalid-input re-prompting; skips rejected actions, continues with remaining; executes only approved actions. Proven in live run (2026-07-02 10:06): invalid input caught and re-prompted, real file deleted on approval, rejected action correctly skipped, convert stub logged, snapshot verified with matching MD5 hashes confirming genuine duplicates. RAID I4 added (Closed).
- Test suite (`test_phase3_4_45.py`): ✅ extended to 45 tests (40 unit + 5 integration, all passing) covering Phases 3, 4, 4.5, and 5.
- GitHub repo: ✅ current — `github.com/nadeemmarshman/onedrive-agent`, **Public**. Contains: `tools.py`, `tool_contracts.py`, `test_phase2.py`, `decision_loop.py`, `agent_loop.py`, `resilience.py`, `approval_gate.py`, `test_phase3_4_45.py`, `test_phase5_live.py`, `README.md`, `BACKLOG.md`, `RAID_LOG.md`, `architecture.svg`, `LICENSE` (MIT), `sample_data/`, `docs/` (`RAID_Log.xlsx`, `REMEDIATION_2026-07-02_cowork-peer-review.md`, generated via `build_raid_log.py`).

---

## Decisions already made (don't re-litigate these)

- **Framing:** Hybrid BA/PM positioning, not BA-only or PM-only.
- **Why not just clean the OneDrive folder directly:** A connector-based approach (Microsoft 365 MCP connector) was tried first and failed — the connector requires a work/school Microsoft account, and I only have a personal Microsoft account, so that route is closed.
- **Why not just use Claude in Chrome or a one-off script:** Considered, but rejected as the *primary* path because the goal is to learn agent architecture, not just get OneDrive tidied — those options either don't teach the tool-calling loop (script) or don't let me configure/see the underlying mechanics (Claude in Chrome is a finished product, good for observing agent behavior but not for building it).
- **Repo will be portfolio-grade from the start** — not a throwaway script. Clean code, documented, version-controlled, README written the way a hiring manager/recruiter would read it.
- **Local folder structure:** the code repo lives on the local C: drive (`C:\Dev\onedrive-agent\`), deliberately *outside* the OneDrive-synced folder tree — avoids Git/OneDrive sync conflicts (especially `.git` internal files) and avoids the codebase sitting inside its own future scan target. The handoff-brief documents, by contrast, stay *under* OneDrive (`OneDrive\...\AI Project Portfolio\Handoff-Briefs\`) since they're low-churn, not Git-managed, and benefit from OneDrive's backup/cross-device sync — the opposite need from the code.
- **API key handling:** the key is stored only as a Windows User-level environment variable (`ANTHROPIC_API_KEY`), read at runtime via `os.environ.get(...)`. It is never hardcoded in any script, and therefore safe to push scripts that use it to a public GitHub repo.

### Out of scope (deliberately not engineered for, and why)

To keep effort proportionate to what this project is actually trying to demonstrate, the following are explicitly **not** being built for. This is a deliberate scope boundary, not an unconsidered gap:

- **Extremely large folders (thousands of files)** — sample-data scale is sufficient for a portfolio demo; real performance tuning isn't the point of this project.
- **Multi-user/concurrent access to the same folder** — not relevant; this is a single-user local tool.
- **Internationalization/unicode filename edge cases** beyond whatever Python's `pathlib` already handles natively — not a focus area for this build.

### Decision log (options considered, trade-offs, and what was chosen)

This log captures decisions that involved a real trade-off (risk, scope, architecture, or portfolio narrative impact) — not minor implementation details like variable naming.

| Phase | Decision | Options considered | Key trade-off | Choice |
|---|---|---|---|---|
| 1 | Test environment | Real OneDrive folder now vs. sample/dummy folder first | Real folder is immediately useful but risky before Phase 5's approval gate exists (bugs could act on real data); OneDrive "online-only" placeholder files add complications. Sample folder is zero-risk and fully controllable for testing edge cases, at the cost of an extra setup step. | **Sample/dummy folder first**, switch to real OneDrive folder once Phase 5 (approval gate) exists |
| 1 | `scan_folder()` recursion | Recurse into subfolders vs. top-level only | Recursing is more realistic (duplicates often live across folders) and a stronger portfolio demo, at the cost of more edge cases (nested permission issues, deeper "online-only" files) and slightly more code. Top-level-only is simpler but misses the common cross-folder duplicate case. | **Recurse, but as a toggle** — `scan_folder(path, recursive=True)` — so it's a deliberate, visible design choice, not hardcoded |
| 1 | Duplicate detection method | Content hash vs. filename match | Filename match is trivial but unreliable both directions (misses real dupes with different names, false-flags same-named different files) and weak as a portfolio artifact. Content hash is technically correct and demonstrates real engineering judgment, at the cost of slightly more compute and needing chunked reads for large files. | **Content hash** (MD5 is sufficient — this is dedup, not a security context) |
| 1 | Code repo location (local) | Inside OneDrive-synced folder vs. local-only C: drive folder | Inside OneDrive risks Git/sync conflicts (many small `.git` files syncing constantly, possible lock conflicts) and means the codebase sits inside its own future scan target. Local-only C: drive avoids both, at the minor cost of not having OneDrive's automatic backup for the working code copy (mitigated by GitHub being the real backup/source of truth once pushed). | **Local C: drive** (`C:\Dev\onedrive-agent\`), outside OneDrive sync |
| — | GitHub repo visibility | Public vs. Private | Private is the safe default while the repo is incomplete/rough, but the entire point of the repo is to be viewable by recruiters/hiring managers — a private repo is invisible to them unless explicitly invited as a collaborator. Public is the only option that actually serves the portfolio goal, but means work-in-progress code is visible before it's polished. | **Private for now; flagged as an explicit Phase 6 to-do to switch to Public** once the full README and polish are in place |
| 2 | Test structure | Single flat test file (mixed checks) vs. explicit two-layer unit-then-integration structure | A flat test file is quicker to write but doesn't distinguish "does each function work alone" from "does data flow correctly between functions" — so a failure doesn't clearly tell you which layer broke, and the practice wouldn't scale cleanly as more phases add more functions. An explicit two-layer structure (unit tests first, integration tests second, integration skipped/flagged as not-meaningful if unit tests fail) costs more upfront code but gives a clear, scalable, and portfolio-credible testing story. | **Two-layer structure (unit, then integration)**, adopted as a standing rule for every future phase, with scope expanding as the project grows |
| 4 (upcoming) | API key storage | Hardcoded in script vs. environment variable | Hardcoding is faster to set up but is a real, common security mistake once the repo is public (bots scan public GitHub repos for exposed keys). An environment variable costs one extra one-time setup step, but means the key never appears in any file that gets committed. | **Environment variable** (`ANTHROPIC_API_KEY`), read via `os.environ.get(...)` |
| 3→4 | Engineering proactiveness vs. scope control | Design for every conceivable failure mode vs. design only for what will reliably occur in this specific architecture | Designing for everything risks overkill for a portfolio-scale project and wastes effort on unlikely scenarios (e.g. concurrent multi-user access). Designing reactively (only fixing what breaks) risks shipping fragile code that "happened to work" rather than was deliberately built — a weaker portfolio signal. A middle path — explicitly listing what will reliably occur given an LLM-driven tool-calling loop, and deliberately designing only for those — balances rigor with proportionate effort. | **Proactive design for LLM-agent-specific reliable risks only** (multi/zero tool calls per turn, malformed tool arguments, unrecognized tool names, loop termination, API failures) — formalized as a standing rule; everything else (scale, concurrency, i18n) explicitly out of scope, see Out of scope list above |
| 4.5 | Email alerting service | Gmail with an app password vs. a transactional email API (SendGrid/Resend) | Gmail is free and uses an account already owned, but requires enabling 2-Step Verification for an app password and reads as "personal automation" rather than real infrastructure. A transactional email API is the actual real-world pattern production alerting systems use, has a generous free tier, and is a stronger, more authentic portfolio signal — at the cost of one more third-party signup and one more API key/secret to manage safely. | **SendGrid** (transactional email API) — chosen specifically for name recognition value on a resume/portfolio, over the simpler-to-set-up Resend alternative |
| 4.5 | Resilience scope: merge into Phase 4 vs. split into a new phase | Fold email alerting + restart/resume directly into Phase 4's loop-building work vs. create a new, separately-named Phase 4.5 | Merging keeps the plan shorter but blurs two different portfolio narratives together — "the agent loop works" vs. "the agent survives real-world failure conditions like load shedding" are different stories worth telling separately. Splitting costs a bit more plan structure/documentation overhead, but keeps each phase's README section focused and lets the resilience work stand out as its own deliberate engineering concern rather than a footnote. | **Split into a new Phase 4.5: Resilience & Alerting**, inserted between Phase 4 and Phase 5 |
| 5 | DR/rollback before destructive actions | Option A: manifest snapshot (write a JSON record of all affected files' paths, sizes, and hashes before any action executes) vs. Option B: full file backup (copy every affected file to a backup folder before execution) | Option B provides true file-level recovery but adds storage overhead, complexity, and potential OneDrive sync conflicts — and is redundant given OneDrive's built-in recycle bin and version history (30–180 days) already provides adequate platform-level recovery for this project's scope. Option A is lightweight (5 lines of code, negligible storage), provides an audit trail of what existed before the run, and is proportionate to the project's actual risk profile. | **Option A: manifest snapshot** (`pre_run_snapshot.json`) written before any Phase 5 action executes. OneDrive's built-in recycle bin and version history accepted as the primary recovery mechanism. Risk logged in RAID (R6). |
| 6 | User roles and approval authority | Single-user model (the person who runs the agent is also the approver) vs. multi-role model (separate operator and approver roles, role-based alert routing, named approver audit trail) | Multi-role model is more realistic for a corporate deployment but disproportionate for a single-user portfolio project — it would require authentication infrastructure, role configuration, and additional complexity with no practical benefit at this scale. Single-user model is honest, proportionate, and explicitly documented as a deliberate scope decision rather than an oversight. | **Single-user model** — the person running the agent is the approver. Multi-role model (operator vs. approver separation, role-based alert routing) logged in Backlog item #5 as a deliberate future consideration, not an unconsidered gap. Noted in README's governance section. |
| 7 | Model selection: stay on `claude-sonnet-4-6` vs. switch to `claude-sonnet-5` | Keep the agent on the model it was originally built and tested against (`claude-sonnet-4-6`, used for free via Claude Chat during the budget-constrained early phases) vs. switch to `claude-sonnet-5` (the model actually used for Claude Chat and Claude Cowork once a paid subscription was justified). | Staying on Sonnet 4.6 avoids any risk of behaviour change in a fully working, tested agent — "if it isn't broken, don't touch it." But it leaves the project running on a model Anthropic has already superseded, and — critically — creates a three-way mismatch: Claude Chat (this conversation) now runs on Sonnet 5, Claude Cowork (Phase 7) ran on Sonnet 5, but the agent's own API calls still targeted Sonnet 4.6. That mismatch risks duplicated effort and wasted tokens on future troubleshooting (e.g. debugging a "difference" that's actually just a model-version difference, as nearly happened when Cowork's peer review had to fact-check the model strings). Switching aligns all three surfaces on one model, removing that confound going forward. | **Switch to `claude-sonnet-5`** in `decision_loop.py` and `agent_loop.py`. Rationale explicitly tied to budget history: the project was originally built on Sonnet 4.6 specifically because it was accessible on the free tier during a period of real budget constraint; once the value of Claude was proven through this project, a paid subscription became justifiable, and Claude Chat/Cowork moved to Sonnet 5 as a result. Keeping the agent's own model pinned to the now-superseded free-tier model would be inconsistent with that upgrade and risks confusing future comparisons. All three surfaces (Claude Chat, Claude Cowork, the agent's own API calls) are now aligned on Sonnet 5. |
| — | Quantified RAID counts on the résumé | Keep hard numbers (e.g. "6 risks, 5 issues") vs. drop to unquantified ("a RAID log tracking risks, assumptions, issues and dependencies") | Quantified reads more concrete on a résumé, but the counts live in this repo's `RAID_LOG.md`, will change again when Phase 8 adds items, and were exactly the fact that drifted in the cross-project fact-check — keeping them means maintaining live cross-project sync machinery for a marginal credibility gain. Unquantified is drift-proof; the numbers remain available for LinkedIn or interview talking points, which tolerate "as of now" better than a résumé line. | **Drop the numbers** from the résumé (decided 2026-07-05). RAID-count guardianship moot; numbers may still be cited live in interviews or LinkedIn where they can be verified at time of use. |
| 8 | Terminology for the final pre-rollout validation stage: POC vs. UAT/Pilot | "Proof of Concept" (the term {{owner}} initially proposed) vs. "User Acceptance Testing / Pilot" | POC is technically incorrect for what's being proposed: a POC proves a concept is *feasible*, done early, typically on synthetic/minimal data — that role was already filled by Phases 1–4 against `sample_data/`. What's actually being proposed — validating an already-built, already-tested solution against real data immediately before full rollout — is UAT/Pilot by standard SDLC definition. Using the wrong term would read as a credibility gap to anyone with formal SDLC background reviewing the project. | **UAT/Pilot**, not POC. Terminology corrected at the point of proposal, before being written into any project document, and confirmed explicitly with {{owner}}. Added as Phase 8 in both the phase plan and a new "This project mapped to standard SDLC terminology" section in the README. |

---

## How to resume

**Phases 1–7 are complete and remediated.** The repo is public at
`github.com/nadeemmarshman/onedrive-agent`.

Next concrete step: **Phase 8 — UAT/Pilot.**
1. Select a specific, contained OneDrive subfolder (not the full folder)
2. Update `starting_folder` in `agent_loop.py` and `test_phase5_live.py`
   to point at that real subfolder
3. Run the agent end-to-end with the approval gate active
4. Review the pre-run snapshot and proposed actions carefully before
   approving anything
5. Sign off on the pilot before considering expansion to the full
   OneDrive folder

Remaining work (outside this project):
- **Resume and LinkedIn** — owned by the Job Search — Resume & LinkedIn
  Claude project. Cross-project fact-check completed 2026-07-05: all
  bullet corrections applied there, master résumé's PORTFOLIO PROJECT
  section is the canonical fact-set, and corrected knowledge files
  (`OneDrive-Agent_Project-Brief.md`, `OneDrive-Agent_README.md`,
  `Return-Handoff_to_JobSearch_Claude.md`) re-uploaded to that project.
  LinkedIn fix pack (including the dead non-hyphenated repo URL fix)
  being applied on the live profile. This project's remaining duties
  are in the sync contract section below.

When resuming in this project, Claude should:
- Treat Phases 1–7 as complete and remediated — don't re-explain them
- Pick up at Phase 8 (UAT/Pilot) unless told otherwise
- The repo is public — link is `github.com/nadeemmarshman/onedrive-agent`
- Resume bullets are in the Job Search project, not here
- Confirm before producing files for download (standing rule below)
- Honour the cross-project sync contract below — in particular, **when Phase 8 completes or its status changes, proactively remind {{owner}} to notify the Job Search project** so résumé/LinkedIn phase-status lines are updated in one coordinated pass

## Standing rule: cross-project sync contract with the Job Search — Resume & LinkedIn project

Adopted 2026-07-05 after a cross-project fact-check found the résumé/LinkedIn bullets had drifted from the actual build (overstated framing, a wrong RAID count, a conflated Phase 7 narrative, a dead repo link). The structural fix is named source-of-truth ownership per fact, so drift can't recur silently:

| Fact | Source of truth | Guardian |
|---|---|---|
| Portfolio bullet copy (all variants) | Master résumé's PORTFOLIO PROJECT section (Job Search project) | Job Search project |
| Phase status | Repo `README.md` build-plan table | **This project** |
| Repo slug | Live repo (`onedrive-agent`, hyphenated — the non-hyphenated slug is a dead 404) | **This project** |
| Résumé/LinkedIn placement & positioning | Job Search project docs | Job Search project |

**This project's live obligations:**
1. **Phase 8 status trigger:** when Phase 8 (UAT/Pilot) completes or its status otherwise changes, this project must proactively flag it so {{owner}} can notify the Job Search project — several résumé/LinkedIn lines are pinned to "Phases 1–7 complete, Phase 8 planned" and must be updated together.
2. **Repo pre-publish check, on request:** before any résumé/LinkedIn publish or CV send-out, when asked, verify: repo is public, README is current, Phase 8 status as stated is accurate. (Last run and passed: 2026-07-05.)

**Resolved / moot:**
- **RAID-count guardianship is moot** — {{owner}} decided (2026-07-05) to drop quantified RAID numbers from the résumé entirely ("a RAID log tracking risks, assumptions, issues and dependencies"), so no ongoing re-verification of counts is needed. If quantified counts are ever reintroduced anywhere public, guardianship of them returns here (they live in this repo's `RAID_LOG.md`).
- **Bullet regeneration direction:** if this project ever regenerates portfolio bullets (e.g. from the Project Brief or README), they must reconcile *to* the Job Search project's canonical master set — not create a competing fact-set.
- **Résumé file format:** stays `.md`; conversion to `.docx` happens at send-time on request and is owned by the Job Search project (which also owns the reminder to strip the internal red warning note before sending).

## Standing rule: explicit date/time confirmation for logged entries

Claude does not have a reliable live clock per message and cannot
accurately timestamp individual chat responses or infer the person's
local time of day. To keep `BACKLOG.md`, `RAID_LOG.md`, and other dated
log entries accurate (rather than approximated), **{{owner}} states the
current date (and time, where relevant) explicitly alongside any
checklist confirmation, decision, or logged event**, and Claude uses
that stated date/time rather than guessing or defaulting to "today" per
its own system context. This was adopted after recognizing that several
existing log entries were dated by approximation rather than confirmed
fact — going forward, entries should be dated only when an explicit
date has been provided.

## Standing rule: check for anything else before producing files for download

Before generating the final downloadable version of any file(s), Claude
should explicitly ask whether there is anything else to add or change —
giving {{owner}} a chance to raise something that occurred to him mid-session
before the files are finalized, rather than producing files, downloading
them, and then needing a second round of edits and re-downloads for
something that could have been folded in the first time. This applies
particularly when multiple files are being updated together in the same
piece of work (a "bundle") — check once before the whole bundle is
finalized, not after each individual file.

## Standing rule: verify checklist actions with a screenshot

Verbal confirmation alone ("done") is not sufficient for phase-closeout
checklist items. When I report a checklist action as complete, Claude
should ask for a screenshot (or equivalent visual evidence — e.g. a
terminal output, a file explorer view, a Project knowledge files panel)
that verifies the action actually took place, before marking that item
as confirmed. This was adopted after a mismatch arose where a verbal
"done" did not match what was actually loaded in Project knowledge
(v3.0 vs v3.2 confusion during Phase 3 closeout) — screenshots resolve
this ambiguity directly rather than relying on memory or assumption from
either side.

## Standing rule: prompt me through the actual actions, not just the policy

Whenever any rule in this document applies (regenerating this document, bumping a version, archiving a superseded file, end-of-phase clean-up, etc.), Claude should **explicitly tell me the concrete steps to perform**, not just note that the rule exists or that an update was made. For example, after generating a new version, Claude should spell out: which old file to delete from Project knowledge, what to upload in its place, and where/how to archive the superseded copy — as a short numbered action list, every time, even if it was done before. Don't assume I'll remember or infer the steps from the rule alone.

## Standing rule: keep this document current (free tier — no cross-conversation memory)

I'm on the free Claude tier. Project knowledge files like this one are visible across every chat in the Project, but the free tier doesn't carry the cross-conversation memory that paid accounts get — so this document is doing the job memory would otherwise do. If it goes stale, future chats will resume from outdated assumptions.

**At the start of every new phase (or whenever a significant decision is made — e.g. a changed tool stack, a finished phase, a new blocker), Claude should proactively offer to regenerate this handoff document** with the updated status, decisions, and next step, rather than waiting to be asked. I'll then re-upload the refreshed version to replace this one in the Project knowledge.

## Standing rule: log decision trade-offs at the point of choice

For any decision in this project that involves a **real trade-off** — risk, scope, architecture, or portfolio narrative impact (not minor implementation details like naming or formatting) — Claude should, before locking it in:

1. Present the options as a short pros/cons/risks comparison (2–4 bullets per option, not an essay).
2. State a recommendation, clearly marked as a recommendation rather than a silent default.
3. Once a choice is made, record it in the **Decision log** table above with: Phase | Decision | Options considered | Key trade-off | Choice.

This keeps the document itself as evidence of requirements/design-stage thinking — useful for the README's "approach" section and for GRC/document-control-style portfolio framing — without bloating the doc with trade-off analysis on things that don't matter.

## Standing rule: two-layer testing (unit, then integration) for every phase

Whenever a phase introduces new functions, they must be tested in two ordered layers, **unit tests first, integration tests second**:

1. **Unit tests** — each new function tested in isolation, including realistic edge cases (empty input, missing/invalid input, near-miss false positives, boundary conditions). These must all pass before integration tests are treated as meaningful.
2. **Integration tests** — the new functions tested chained together with prior-phase functions, using data shaped exactly as it will flow in the real agent loop (e.g. dict-shaped arguments matching the JSON-schema contracts, not hand-built native objects). This is where contract-shape mismatches and "didn't handle the previous step's output format" bugs surface.

**This test suite must scale with the project**: each new phase adds its own unit tests for its new functions, then extends the integration tests to cover the now-longer chain — it does not replace prior tests, it builds on them. The test runner should run unit tests first and clearly flag if integration results are not meaningful because a unit test failed.

This testing structure must be reflected in both **this handoff document** (status section, noting test counts/coverage per phase) and the **README** (a "Testing approach" section describing the two-layer practice), so the testing discipline itself is visible as a portfolio signal — not just the fact that "tests exist."

## Standing rule: proactive design for reliable LLM-agent risks (not incidental edge-case handling)

Before writing code for any phase involving the LLM decision loop, Claude should explicitly identify and design for the things that will **reliably occur** given how an LLM-driven, tool-calling agent behaves — rather than relying on code that happens to handle a scenario by coincidence of its structure.

**Reliably-occurring risks to design for explicitly, as they become relevant in each phase:**
- The model returning zero, one, or multiple tool calls in a single turn
- Tool-call arguments that don't match what the underlying function expects (validate before calling, don't assume well-formed input)
- The model requesting a tool name that isn't recognized
- A loop with no explicit termination condition (max iterations, or detecting "no further tool calls needed")
- Real API/network failures during a live call (rate limits, timeouts, connectivity)

**This is a deliberate scope boundary, not a call to handle everything:** things that are rare or out of scope for what this project demonstrates (see "Out of scope" list above — folder scale, concurrency, internationalization) are explicitly *not* engineered for, on purpose, so effort stays proportionate to the project's actual goals.

When this rule applies, Claude should name the specific risk being designed for and why, rather than silently adding defensive code — this keeps the reasoning visible as a portfolio signal (the "Design philosophy" section in the README exists for this reason) and avoids both extremes: fragile code that worked by luck, and over-engineered code that solves problems this project doesn't have.

## Standing rule: versioning convention

This document uses `vMAJOR.MINOR` versioning, filename format `AI-Agent-Build-Handoff_vX.X.md`:
- **MINOR** (e.g. v1.0 → v1.1): status updates, added notes, minor corrections — no change to structure or scope
- **MAJOR** (e.g. v1.x → v2.0): structural changes — new phase added, scope change, reversal of a prior decision, or a new standing rule that changes how future work is done

Every new version is a **new file**, not an overwrite — this preserves a real, demonstrable change history (relevant to GRC/document-control practice for portfolio purposes). Every version bump must add a row to the **Version History** table at the top of this document with: Version | Date | Summary of Change | Reason.

## Standing rule: clutter control at the end of each phase

To avoid accumulating stale files in the Project knowledge (and free-tier file-count limits):

- **Keep only the current version** of this document in the Project knowledge files. When a new version is generated, the superseded version should be removed from the Project and replaced with the new one.
- **Archive superseded versions outside the Project**, on my own machine, rather than deleting them outright — preserves the change history without cluttering the Project.
- **For now**, archiving is to my own machine (a simple local folder of old versions is fine — currently `OneDrive\...\AI Project Portfolio\Handoff-Briefs\`). Once I'm set up and comfortable with the GitHub repo (Phase 6), archiving should move there instead — Git is a better long-term fit for version control than manually-numbered files, and the repo's commit history can supersede this manual table going forward.
- This clean-up should happen **at the end of each phase**, before the next phase begins — i.e. before starting Phase 4, confirm Phase 3's version of this document is finalized, superseded versions archived locally, and only the latest sits in the Project.
