# OneDrive Cleanup Agent (OneDrive AI Agent) — Executive Project Summary

**Repo:** `github.com/nadeemmarshman/onedrive-agent` (public)
**Prepared by:** Claude Code, under Nadeem Marshman's (Business Analyst / Project Manager, BA/PM) direction
**Acronyms:** expanded on first use; full register in [`GLOSSARY.md`](./GLOSSARY.md).

---

## What this is

The **OneDrive AI Agent** is a small, tool-calling AI agent (Python + the Anthropic API) that scans a folder, finds duplicate and bloated files, proposes clean-up actions, and executes them — but only after a human explicitly approves each action. Designed, governed, and directed as a BA/PM exercise, with the Python implemented collaboratively with an AI assistant under that direction.

**The repo is a portfolio artefact, not a finished product.** The point isn't the file-cleanup task itself — it's demonstrating BA/PM discipline (requirements, design, risk management, governance, User Acceptance Testing) applied to an actual technical build, with every phase committed separately so the decision-making is visible, not just the outcome.

## The build, briefly

Seven build phases, each proving a piece of the standard agent loop — **tool definition → LLM decision → action → observation → repeat** — the same loop underlying Claude Code, Model Context Protocol (MCP) connectors, and Claude Cowork:

| Phase | What it proved |
|---|---|
| 1–2 | Tool functions and their JSON-schema contracts (the format the Anthropic API and MCP both use) |
| 3–4 | The decision loop live against the Anthropic API, then the full decide → execute → observe loop end-to-end, with all reliably-occurring LLM-agent risks (multi/zero tool calls, malformed arguments, unrecognized tools, loop termination, API failures) explicitly handled |
| 4.5 | Resilience — email alerting and a state machine designed for restart-and-resume after an abrupt stop (e.g. load shedding) |
| 5 | The human-approval gate — nothing destructive executes without a pre-run audit snapshot and per-item explicit approval |
| 6 | Polish — README, architecture diagram, public repo |
| 7 | Independent comparison against Claude Cowork (Anthropic's own production agentic tool) — same findings on every test case, validating the hand-built OneDrive AI Agent's core logic; Cowork has no visible equivalent of the governance layer (audit trail, alerting, state-machine resilience) |

Full phase-by-phase detail: `README.md`.

## The differentiator: governance and independent verification

The technical build is validated the way an engineer would; the *process* is governed the way a BA/PM would. Both are demonstrated as real artefacts in this repo, not asserted:

- **Risks, Assumptions, Issues, Dependencies (RAID) log** (`RAID_LOG.md`) — tracked live throughout the build, including issues found and root-caused by an independent reviewer (Claude Cowork peer review, 2026-07-02) and issues found during the pilot itself
- **Decision log** — every real trade-off (options considered, key trade-off, choice made) recorded at the point of choice, in the project's handoff document
- **Agile backlog** (`BACKLOG.md`) — Product Backlog and Daily Scrum log, with retrospective notes on what went wrong and what changed as a result
- **"No snapshot, no actions"** — a pre-run audit manifest (path, size, MD5 hash per affected file) is a hard precondition for any destructive action, not an optional extra
- **Independent, deterministic audit trail for the pilot** — Phase 8's checkpoints (below) were verified against `Get-FileHash`, a separate non-AI tool, specifically because Claude auditing Claude would be correlated evidence, not independent evidence

## Phase 8: User Acceptance Testing / Pilot (UAT/Pilot) — complete, signed off 2026-07-20

Phase 8 deliberately validates the already-built, already-tested OneDrive AI Agent against real conditions immediately before rollout — distinct from a Proof of Concept, which Phases 1–4 already covered against synthetic data.

Three checkpoints (CP), each independently verified against `Get-FileHash` — a separate, deterministic, non-AI tool, not the OneDrive AI Agent auditing itself:

| Checkpoint | Result |
|---|---|
| CP1 (baseline) | Dry-run matched the independent `Get-FileHash` manifest with zero discrepancies |
| CP2 (read-only proof) | Zero differences from CP1 — detection is provably non-destructive |
| CP3 (change control) | Post-execution state = baseline minus exactly the approved deletions, nothing else |

All 19 green-line/red-line test cases (happy-path and adversarial/edge-case scenarios) closed. One result is stated honestly rather than rounded up: the pilot's most safety-critical test — does an interrupted run ever execute an action without approval — could not be proven via its originally-specified mechanism (a saved-state resume that turned out not to be wired into the live code path). The property that actually matters was verified empirically instead, via a genuine unplanned process interruption: no unapproved execution occurred. **That behavioral safety guarantee is proven; the specific resume mechanism is not yet live** — logged and disclosed precisely, not smoothed over. Full detail: `PILOT_SIGNOFF_SUMMARY.md`.

A small number of known, low-risk limitations are carried forward as deliberately post-pilot work (documented in `BACKLOG.md`) — none of them affect the safety guarantees above.

## Honest scope

This is a **portfolio-grade demonstration, not a production system**. Explicitly out of scope by design: very large folders, multi-user/concurrent access, and fuzzy/visual duplicate detection (exact content-hash matching only). Where limitations exist, they're disclosed in the project's own RAID log and backlog rather than left implicit.

## Where the BA/PM contribution actually is

The Python was written collaboratively with an AI assistant. The requirements framing, scope decisions, governance design, RAID and decision logs, phase planning, and test strategy — the discipline and judgement applied throughout — are Nadeem's, in his BA/PM capacity. Neither side is overstated: the portfolio value is BA/PM discipline applied to a genuine build, not a claim of unassisted solo software engineering.

## Further reading

All in `github.com/nadeemmarshman/onedrive-agent`:

- `README.md` — full build narrative, architecture, governance, and testing approach
- `architecture.svg` — the agent-loop architecture diagram (renders inline on the repo landing page)
- `PILOT_SIGNOFF_SUMMARY.md` — the Phase 8 pilot sign-off summary this document draws on
- `TEST_STRATEGY.md` / `TEST_BED_AND_CASES.md` — the pilot's technical test design and execution recipe
- `TEST_USE-CASES_PLAIN_ENGLISH.md` — every test case restated as a plain-English user story, for a non-technical reviewer
- `RAID_LOG.md` (Risks, Assumptions, Issues, Dependencies) and `BACKLOG.md` (Agile Product Backlog and Daily Scrum log) — the live governance trail behind every claim above
- `docs/REMEDIATION_2026-07-02_cowork-peer-review.md` — the independent Claude Cowork peer review referenced above, in full
- `GLOSSARY.md` — the canonical register for every acronym used across this project's documentation
