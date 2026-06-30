# OneDrive Cleanup Agent (work in progress)

A small, hand-built AI agent that finds duplicate and bloated files in a
folder (using OneDrive as the live use case), proposes clean-up actions,
and — once complete — will execute them only after human approval.

**Status: in progress.** This repo is being built incrementally, phase by
phase, with each phase committed separately so the build process itself
is visible in the commit history. A full README (problem, approach,
architecture, outcome) will replace this placeholder once the build is
complete.

## Why this project

I'm a hybrid Business Analyst / IT Project Manager, not a software
engineer by background. This project exists to give me a real,
hands-on technical artifact to point to — built with the same
requirements → design → build → risk/governance discipline I'd bring
to any BA/PM deliverable, applied here to a small AI agent instead of
a business process.

The agent automates a genuinely useful task (deduplicating and
optimizing files in a cluttered OneDrive folder), but the real goal is
to understand — and be able to demonstrate understanding of — the
core agent loop that underlies tools like Claude Code, MCP connectors,
and Claude Cowork:

**tool definition → decision (LLM) → action → observation → repeat**

## Build plan

| Phase | What it covers |
|---|---|
| 1 | Plain Python tool functions (no AI) — scanning, duplicate detection, format-conversion candidates, proposed actions |
| 2 | JSON-schema tool contracts for each function (the same format used by MCP and the Anthropic API) |
| 3 | The decision loop itself, built against the Anthropic API |
| 4 | Running the loop end-to-end against a real/sample folder |
| 5 | A human-approval gate before any destructive action executes |
| 6 | Polish: documentation, architecture diagram, full README |
| 7 | A written comparison against Claude Cowork (Anthropic's own production agent), once the hand-built version is complete |

## Current state

- ✅ Phase 1 complete: `tools.py` — `scan_folder()`, `find_duplicates()`,
  `find_convertible_files()`, `propose_action()`, tested against a sample
  folder with deliberately planted edge cases (true duplicates, a
  same-name/different-content near-miss, and a convertible file format)
- ✅ Phase 2 complete: `tool_contracts.py` — JSON-schema tool contracts
  for all four functions, validated by a two-layer test suite
- ✅ Phase 3 complete: `decision_loop.py` — first live call to the
  Anthropic API; Claude correctly read the tool contracts and chose to
  call `find_duplicates` and `find_convertible_files` in the same turn,
  having recognized the two checks are independent of each other
- ⏳ Phase 4 in progress

## Design philosophy: proactive design, not lucky edge-case handling

A recurring risk in agent-style code is writing something that happens
to work because of how a loop or data structure is shaped, without
having deliberately decided to handle that scenario. This project
draws an explicit line between two categories:

- **Things that will reliably occur**, given how an LLM-driven agent
  behaves (e.g. the model returning zero, one, or several tool calls
  in a single turn; malformed or unexpected tool arguments; an
  unrecognized tool name; a loop that needs an explicit stopping
  condition; real API/network failures) — these are designed for
  deliberately, with a stated reason, before they cause a problem.
- **Things that are rare or out of scope** for what this project is
  trying to demonstrate — these are explicitly *not* engineered for,
  on purpose, rather than left as an unconsidered gap. Out of scope,
  and why:
  - **Extremely large folders (thousands of files)** — sample-data
    scale is sufficient for a portfolio demo; real performance tuning
    isn't the point of this project.
  - **Multi-user/concurrent access to the same folder** — not
    relevant; this is a single-user local tool.
  - **Internationalization/unicode filename edge cases** beyond
    whatever Python's `pathlib` already handles natively — not a
    focus area for this build.

This distinction itself is meant to be a visible signal: the goal
isn't defending against every conceivable input, it's recognizing
which risks are real for an LLM-driven tool-calling loop specifically,
and building for those on purpose.

## Repo contents (so far)

- `tools.py` — Phase 1 tool functions
- `tool_contracts.py` — Phase 2 JSON-schema tool contracts (the format
  used by MCP and the Anthropic API to describe each function to an LLM)
- `test_phase2.py` — Phase 2 test suite (see Testing approach below)
- `sample_data/` — disposable test folder used to validate the functions
  safely, before any work happens against a real OneDrive folder

## Testing approach

Every phase that introduces new functions is tested in two ordered
layers, growing in scope as the project does:

1. **Unit tests** — each function tested in isolation, including edge
   cases (empty input, missing folders, near-miss false positives, etc.).
   These run first and must all pass before integration tests are
   considered meaningful.
2. **Integration tests** — functions tested chained together, with data
   flowing from one into the next exactly as it will in the real agent
   loop. This is where contract-shape mismatches and "forgot to handle
   the previous step's output" bugs would surface.

This two-layer structure repeats and expands with each new phase (e.g.
Phase 3's decision loop gets its own unit tests, then an integration
test layered on top of the existing chain) rather than being replaced.

## Notes

- No destructive action (delete, convert, move) happens without an
  explicit human approval step — that gate is being built in Phase 5,
  and nothing before it touches real files.
- Build/design decisions with real trade-offs (architecture, risk,
  scope) are logged with their reasoning as the project progresses;
  this will be summarized in the final README.
