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
- ⏳ Phase 2 in progress

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
