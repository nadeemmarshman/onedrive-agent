# AI Agent Build — Handoff Brief

**Purpose of this document:** This is a context handoff for a project in progress, written so Claude (in a new chat, with no prior memory) can pick up exactly where things left off. Upload this as a Project knowledge file.

**Current version: v4.0**

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

---

## Who I am / context

{{owner}} — hybrid Business Analyst / IT Project Manager based in Johannesburg, South Africa. Targeting both BA and PM roles. Currently unemployed and job hunting. Background includes {{employerA}} (BA-focused), NCR Atleos/{{employerB}} (PM-focused), Agile delivery, payments systems, stakeholder management. Holds a Diploma in Business Analysis and Project Management, PSM I certification. No PMP/PRINCE2.

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
| 5 | Add a human-approval gate before any destructive action (e.g. deletion) executes | "Risk & governance" — the BA/PM differentiator |
| 6 | Polish: clean documented code, README (problem → approach → architecture → outcome), Git/GitHub repo, optional architecture diagram, draft resume bullet | The actual shareable/linkable deliverable |
| 7 | Compare the hand-built agent to Claude Cowork (Anthropic's own production agent) — try Cowork (e.g. a free trial of Pro, if available) on a similar file-organizing task and note where it matches/exceeds the hand-built version, and why | "Evaluating other agent products" section in README — demonstrates I can assess production agent tooling, not just build a toy one |

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

**Status: Phase 1, 2, and 3 complete; Phase 4 next (Phase 4.5 newly added, follows Phase 4).**
- Python: ✅ confirmed installed — Python 3.14.5, 64-bit, Windows
- GitHub account: ✅ confirmed
- Anthropic API key: ✅ activated — billing set up on console.anthropic.com, key created (named `onedrive-agent`), stored safely outside any code file, loaded via the `ANTHROPIC_API_KEY` environment variable (Windows User-level variable). Never hardcoded into any script.
- SendGrid account: ⏳ in progress — needed for Phase 4.5's email alerting. Requires account creation, Single Sender Verification (verifying one "from" email address), and an API key with Mail Send permission only. Key will be stored the same way as the Anthropic key, as a second environment variable (`SENDGRID_API_KEY`).
- Alert recipients (for now): `nadeemmarshman@gmail.com`, `narshman@duck.com` — to be built as a configurable list, not hardcoded, since the real distribution list may change later.
- `anthropic` Python package: ✅ installed (`anthropic-0.112.0`). Note: initial `pip install anthropic` failed on this machine due to a `tokenizers` dependency trying to compile from Rust source (no Rust compiler present) — resolved by updating pip first (`python -m pip install --upgrade pip`), after which a prebuilt wheel installed cleanly. Worth knowing if this resurfaces on a fresh machine.
- Phase 1 (`tools.py`): ✅ complete — `scan_folder()`, `find_duplicates()`, `find_convertible_files()`, `propose_action()` built and tested against a planted sample folder.
- Phase 2 (`tool_contracts.py`): ✅ complete — JSON-schema tool contracts written for all four Phase 1 functions, in the exact format the Anthropic API and MCP use. Validated via `test_phase2.py`: 14 unit tests (per-function, including edge cases) + 4 integration tests (contract validation + full chained flow), all passing.
- Phase 3 (`decision_loop.py`): ✅ complete — first live Anthropic API call succeeded. Sent a goal + the four tool contracts + real scanned folder state; Claude responded with `stop_reason: tool_use` and chose to call **both** `find_duplicates` and `find_convertible_files` in the same turn, correctly reasoning they're independent of each other. This phase proves the decision step only — no tool execution or looping yet (that's Phase 4). **API error handling implemented**: authentication failure, rate limiting, connection failure, and general API errors (e.g. insufficient credit) are each caught specifically and exit gracefully with an actionable message rather than a raw crash.
- GitHub repo: ✅ created and pushed — `github.com/nadeemmarshman/onedrive-agent`, currently **Private**. Contains `tools.py`, `tool_contracts.py`, `test_phase2.py`, `decision_loop.py`, `README.md`, `sample_data/`.

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

---

## How to resume

Next concrete step: Phase 4 — execute the tool(s) Claude decides to call, feed the real result back to Claude as an observation, and let it decide the next step, looping until the goal is complete (or a stopping condition is hit). This is where Phase 3's "decision only" script becomes a real, looping agent. Phase 4.5 (resilience & alerting) follows immediately after, and is currently waiting on SendGrid account setup (Single Sender Verification + API key).

Per the proactive-design standing rule, Phase 4 must explicitly handle:
1. Claude returning zero, one, or multiple tool calls in a single turn
2. Tool-call arguments that don't match what the function expects (validation before calling)
3. A tool name Claude requests that isn't recognized
4. An explicit loop-termination condition (e.g. max iteration count, or detecting no further tool calls)
5. Real API/network failures during the call itself (already implemented in Phase 3's single-call version; Phase 4 must carry this into the loop)

Phase 4.5 must explicitly handle:
1. Sending an email alert (via SendGrid) to a configurable recipient list when a serious/unhandled failure occurs during the loop
2. Persisting enough state to disk at each meaningful loop step that the process could be restarted and resume from that point
3. Being honest in the README about what "restart-and-resume" actually covers — the script resuming from saved state on its own startup, not the script causing the machine itself to reboot or relaunch it (that part requires an OS-level mechanism, e.g. Windows Task Scheduler)

When resuming, Claude should:
- Treat this as already-agreed scope — don't re-ask whether I want to do this or re-explain what an agent is from scratch.
- Pick up at the phase marked "in progress"/"next" above, or wherever I indicate we left off.
- Keep README/resume framing hybrid BA/PM throughout.
- For decisions with a real trade-off, present pros/cons/risks before locking in (see standing rule below), and log the outcome in the Decision log table.
- Apply the two-layer (unit, then integration) testing standing rule to any new functions introduced in Phase 4 onward.
- Apply the proactive-design standing rule (see below) when architecting Phase 4's execution loop and Phase 4.5's resilience features.

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
