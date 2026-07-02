# OneDrive Cleanup Agent

A small, hand-built AI agent that finds duplicate and bloated files in a
OneDrive folder, proposes clean-up actions, and executes them — but only
after explicit human approval of each action.

Built from scratch in Python against the Anthropic API to demonstrate the
core agent loop (tool definition → LLM decision → action → observation)
and the BA/PM discipline applied to a technical build: requirements, design,
risk management, governance, and iterative delivery.

**The repo is a portfolio artefact, not a finished product.** The build
process itself is the point — each phase is committed separately so the
decision-making behind it is visible, not just the outcome.

---

## Why this project

I'm a hybrid Business Analyst / IT Project Manager, not a software engineer
by background. This project exists to give me a concrete technical artefact
to point to — built with the same requirements → design → build →
risk/governance discipline I'd bring to any BA/PM deliverable.

Many BA/PM candidates can talk about AI conceptually. Few can point to
something they actually built. Fewer still apply formal PM artefacts
(RAID log, Agile backlog, decision log, two-layer test suite) to the build
process itself.

The agent automates a genuinely useful task (deduplicating a cluttered
OneDrive folder), but the real goal is to understand — and be able to
demonstrate — the core loop that underlies tools like Claude Code, MCP
connectors, and Cowork:

**tool definition → LLM decision → action → observation → repeat**

---

## Architecture

![OneDrive Cleanup Agent architecture diagram](architecture.svg)

The agent runs in phases, each building on the last:

```
[Scan folder]
     │
     ▼
[Claude reads tool contracts → decides which tools to call]
     │
     ├──▶ find_duplicates()      ─┐
     ├──▶ find_convertible_files() ┼──▶ [propose_action()]
     └──▶ (loop back if needed)  ─┘
                │
                ▼
     [Full proposal list shown to user]
                │
                ▼
     ┌─────────────────────────┐
     │   HUMAN APPROVAL GATE   │  ◀── pre-run snapshot written first
     │  approve / reject each  │      ("no snapshot, no actions")
     └─────────────────────────┘
          │             │
       approved       rejected
          │             │
     [Execute]      [Skip · continue]
          │             │
          └──────┬──────┘
                 ▼
              [Done]

Supporting layer (Phase 4.5):
  State machine   — persisted to disk at each step for restart-and-resume
  SendGrid alerts — 5W incident framework, masked user ID, per-error
                    troubleshooting steps
```

**User roles:** single-user model — the person running the agent is also
the approver. A multi-role model (separate operator and approver,
role-based alert routing) is a logged future consideration, not an
unconsidered gap (see BACKLOG.md item #5).

---

## Project location and key paths

Alert emails reference this table — check here first if an alert tells
you to "see README.md for the correct path."

| Item | Default location |
|---|---|
| Project folder | `C:\Dev\onedrive-agent\` |
| Run the agent | `python agent_loop.py` (from the project folder) |
| State file | `agent_state.json` in the project folder |
| Pre-run snapshot | `pre_run_snapshot.json` in the project folder |
| Run logs | `logs\` subfolder inside the project folder |
| Environment variables | Windows User-level — set via PowerShell, persist across sessions |

If you move the project, update this table so alert instructions stay accurate.

---

## Build plan

| Phase | What it covers | Status |
|---|---|---|
| 1 | Plain Python tool functions — scanning, duplicate detection, format-conversion candidates, proposed actions | ✅ Complete |
| 2 | JSON-schema tool contracts for each function (the format used by MCP and the Anthropic API) | ✅ Complete |
| 3 | The decision loop — live Anthropic API call; Claude reads contracts and returns structured tool calls | ✅ Complete |
| 4 | Full execution loop — decide, execute, observe, repeat; all 5 proactive-design risks handled explicitly | ✅ Complete |
| 4.5 | Resilience & Alerting — SendGrid email alerts (5W incident framework), state machine with restart-and-resume for load-shedding resilience | ✅ Complete |
| 5 | Human-approval gate — pre-run manifest snapshot, full proposal review, per-item approve/reject | ✅ Complete |
| 6 | Polish — full README, architecture diagram, repo public | ✅ Complete |
| 7 | Comparison against Claude Cowork (Anthropic's own production agent) — evaluate the hand-built version against a finished product | Planned |

---

## Design philosophy: proactive design, not lucky edge-case handling

A recurring risk in agent-style code is writing something that happens to
work because of how a loop or data structure is shaped — without having
deliberately decided to handle that scenario.

This project draws an explicit line between two categories:

**Things that will reliably occur**, given how an LLM-driven agent
behaves — e.g. the model returning zero, one, or several tool calls in
a single turn; malformed tool arguments; an unrecognised tool name; a
loop that needs an explicit stopping condition; real API/network failures
— are designed for deliberately, with a stated reason, before they cause
a problem.

**Things that are rare or out of scope** for what this project
demonstrates are explicitly *not* engineered for, on purpose:
- Extremely large folders (thousands of files) — sample-data scale is
  sufficient for a portfolio demo
- Multi-user/concurrent access — not relevant; this is a single-user tool
- Internationalization/unicode edge cases beyond what `pathlib` handles

This distinction itself is meant to be visible: the goal is recognising
which risks are real for an LLM-driven tool-calling loop specifically,
and building for those on purpose.

---

## Governance and risk management

This project applies BA/PM discipline to a technical build — not just to
the code, but to the process itself:

- **RAID_LOG.md / RAID_Log.xlsx** — Risks, Assumptions, Issues, and
  Dependencies tracked throughout the build (6 risks, 5 assumptions,
  4 issues, 4 dependencies at time of writing)
- **BACKLOG.md** — Agile Product Backlog and Daily Scrum log, including
  retrospective notes on what went wrong and what process changes resulted
- **Decision log** (in the handoff document) — every design trade-off
  recorded with options considered, key trade-off, and choice made
- **Pre-run manifest snapshot** — `pre_run_snapshot.json` written before
  any destructive action executes, recording each affected file's path,
  size, and MD5 hash as an audit trail. "No snapshot, no actions" is a
  hard precondition, not an optional extra
- **DR/rollback** — OneDrive's built-in recycle bin and version history
  accepted as the primary recovery mechanism (proportionate); the manifest
  snapshot provides agent-level audit without redundant file copying

---

## Testing approach

Every phase that introduces new functions is tested in two ordered layers:

1. **Unit tests** — each function tested in isolation, including realistic
   negative/red-line cases (empty input, missing folders, near-miss false
   positives, corrupted state files, invalid API keys, disk write failures)
2. **Integration tests** — functions tested chained together, with data
   flowing as it will in the real agent loop

The test suite scales with the project: `test_phase2.py` covers Phases 1–2;
`test_phase3_4_45.py` covers Phases 3–5 (45 tests: 40 unit + 5 integration,
all passing). Unit tests run first; if any fail, integration tests are
skipped and flagged as not meaningful until the unit layer is clean.

---

## Current state

- ✅ Phase 1 complete: `tools.py` — four tool functions, tested against a
  sample folder with deliberately planted edge cases (true duplicates, a
  same-name/different-content near-miss, a convertible file format)
- ✅ Phase 2 complete: `tool_contracts.py` — JSON-schema tool contracts
  for all four functions, validated by a two-layer test suite
- ✅ Phase 3 complete: `decision_loop.py` — first live Anthropic API call;
  Claude correctly identified and called two independent tools in the same
  turn, without being told to
- ✅ Phase 4 complete: `agent_loop.py` — full loop run end-to-end; Claude
  called two tools in parallel in iteration 1, chained their results into a
  third call in iteration 2, then correctly stopped on its own in iteration
  3 (natural termination, not the safety-limit fallback)
- ✅ Phase 4.5 complete: `resilience.py` — SendGrid alerting (7 named alert
  functions, 5W incident framework, masked user credentials, README-reference
  pattern on all commands) and explicit state machine (5 named states,
  persisted to disk, `AWAITING_HUMAN_APPROVAL` never silently skipped)
- ✅ Phase 5 complete: `approval_gate.py` — proven in a live run: invalid
  input caught and re-prompted, real file deleted on approval, rejected
  action correctly skipped, pre-run snapshot verified with matching MD5 hashes
- ✅ Phase 6 complete: full README, architecture diagram (`architecture.svg`
  rendering inline on the repo landing page), repo switched to Public
- 🔜 Phase 7 planned — comparison against Claude Cowork

---

## Repo contents

- `tools.py` — Phase 1 tool functions
- `tool_contracts.py` — Phase 2 JSON-schema tool contracts
- `test_phase2.py` — Phase 2 two-layer test suite
- `decision_loop.py` — Phase 3 decision loop (live Anthropic API)
- `agent_loop.py` — Phase 4 full execution loop with structured logging
- `resilience.py` — Phase 4.5 resilience and alerting
- `approval_gate.py` — Phase 5 human-approval gate
- `test_phase3_4_45.py` — Phase 3–5 test suite (45 tests)
- `test_phase5_live.py` — end-to-end live test runner (Phases 1–5)
- `sample_data/` — disposable test folder with planted edge cases
- `BACKLOG.md` — Agile Product Backlog and Daily Scrum log
- `RAID_LOG.md` / `RAID_Log.xlsx` — Risks, Assumptions, Issues, Dependencies
- `build_raid_log.py` — script that generated `RAID_Log.xlsx`

---

## Running the agent

```
cd C:\Dev\onedrive-agent
python agent_loop.py
```

Requires `ANTHROPIC_API_KEY` and `SENDGRID_API_KEY` set as Windows
User-level environment variables (see README table above for setup).
