# Project Charter

**Retroactively authored at project closure, 2026-07-20 06:12.** This charter documents the objectives, scope, and authorization that governed this project from its start (2026-06-26) — written now, honestly, rather than backdated to imply it existed on day one. This is a deliberate practice, not an oversight: the same discipline (the quantified-figure-drift rule, the honest-attribution rule) has been applied throughout this project, recorded in the handoff document's Decision log.

**Acronyms:** expanded on first use; full register in [`GLOSSARY.md`](./GLOSSARY.md).

---

## 1. Project purpose / business justification

Nadeem Marshman is a hybrid Business Analyst / Project Manager (BA/PM), not a software engineer by background, targeting both BA and PM roles in the job market. Many BA/PM candidates can discuss AI conceptually; few can point to a concrete technical artifact built under their own direction, with formal BA/PM discipline (requirements, design, risk management, governance, User Acceptance Testing) applied to the build process itself — not just the outcome.

This project exists to produce exactly that artifact. The chosen build — an AI agent that deduplicates and proposes clean-up actions on OneDrive files — is the vehicle, not the goal. The goal is a portfolio-grade, publicly verifiable demonstration of BA/PM judgement applied to a real technical delivery, executed with the same tool-calling agent loop (tool definition → LLM (Large Language Model) decision → action → observation → repeat) that underlies production agent tooling such as Claude Code, Model Context Protocol (MCP) connectors, and Claude Cowork — giving Nadeem direct, first-hand understanding of that mechanism, not just familiarity with the products built on it.

## 2. Objectives and success criteria

**Objectives:**
- Build a working, tool-calling AI agent demonstrating the full agent loop end-to-end, governed by explicit human approval before any destructive action
- Apply real BA/PM governance artifacts to the build itself — a RAID (Risks, Assumptions, Issues, Dependencies) log, a Decision log, an Agile-influenced backlog, and a two-layer test discipline — maintained live throughout, not reconstructed after the fact
- Validate the finished build against real, live data via a formally governed User Acceptance Testing (UAT) / Pilot stage, independently verified, before claiming completion
- Produce a public, portfolio-grade repository suitable for résumé, LinkedIn, and interview use — honest about what it is (a demonstration artifact) and isn't (a production system)

**Success criteria:**
- All planned build phases delivered and independently validated (Phase 7's comparison against Claude Cowork, an existing production agent, served this purpose)
- Governance artifacts genuinely live throughout the build, evidenced by commit history and dated entries, not retrofitted at the end
- UAT/Pilot executed against a real, limited OneDrive subset, with detection independently verified by a deterministic, non-AI tool rather than the agent auditing itself
- A formal, explicit sign-off decision obtained before considering any expansion beyond the pilot scope
- No overclaiming, at any point — every disclosed limitation, every unproven claim, and every honest gap stated precisely rather than smoothed over

All of the above were achieved; see `PILOT_SIGNOFF_SUMMARY.md` for the pilot's formal result and this document's Requirements Traceability Matrix companion for the evidence trail.

## 3. Sponsor, Project Manager, and key stakeholders

This is a self-directed, solo portfolio initiative. Stated plainly rather than inventing a structure that didn't exist:

| Role | Who | Note |
|---|---|---|
| Sponsor | Nadeem Marshman | Authorized the project and its objectives (§7) |
| Project Manager | Nadeem Marshman | Same person as Sponsor — honest for a solo initiative, not a gap |
| Business Analyst | Nadeem Marshman | Requirements framing, scope decisions, governance design, RAID and Decision logs, phase planning, and test strategy are his, in this capacity |
| Delivery | Claude (Claude Code / Claude Project sessions) | The Python implementation was written collaboratively with an AI assistant, under Nadeem's direction — not an equal "partner" role, and not unassisted solo engineering either; see this project's honest-attribution standing rule |
| End reviewer / real "customer" | Prospective employers and interviewers | The artifact's actual audience — the project is built to be read, not just to run |

## 4. High-level scope

**In scope:**
- An agent that scans a folder, detects true duplicates by content hash, flags convertible legacy file formats, proposes clean-up actions, and executes only approved actions
- A human-approval gate, pre-run audit snapshot, structured logging, and email alerting on failure
- A governed UAT/Pilot against a real, limited OneDrive subset, with an independent deterministic audit trail

**Explicitly out of scope, by design (not an oversight):**
- Very large folders (thousands of files) — sample-data scale is sufficient to demonstrate the pattern
- Multi-user or concurrent access — a single-user tool by deliberate design (see Decision log, user roles)
- Internationalization/unicode edge cases beyond what Python's `pathlib` handles natively
- Fuzzy or visually-similar duplicate detection — exact content-hash matching only (RAID A10)
- A formal Business Requirements Document (BRD) — lightweight, Decision-log-captured requirements practice used instead; see handoff Decision log

## 5. High-level risks known at the outset

Risks identifiable before the build began (the full risk register, including issues discovered during delivery, lives in `RAID_LOG.md`):
- Local infrastructure instability (load shedding / power loss) interrupting a long-running process mid-action
- Real API/network failures during live calls to the Anthropic API
- The reliably-occurring behavioural risks of an LLM-driven, tool-calling loop (multi/zero tool calls per turn, malformed arguments, unrecognized tool names, undefined loop termination)

## 6. High-level milestones

| Milestone | Approximate date |
|---|---|
| Project start / Phase 1 (tool functions) | 2026-06-26 |
| Phase 4 (full agent loop, live) | 2026-06-30 |
| Phase 5 (human-approval gate) | 2026-07-02 |
| Phase 6/7 (polish, public repo, Cowork comparison) | 2026-07-02 |
| Phase 8 Definition of Ready gate | 2026-07-05 |
| Pilot audit-control regime adopted | 2026-07-09 |
| Pilot execution (Sessions 1–2b, all test cases closed) | 2026-07-15 – 2026-07-19 |
| Formal pilot sign-off | 2026-07-20 |
| Project closure (this charter and its companion closure artifacts) | 2026-07-20 |

## 7. Authorization

Authorized by Nadeem Marshman, in his capacity as Sponsor, to proceed as a self-directed portfolio initiative. No external funding, formal governance board, or organizational approval applies — authorization here means the deliberate decision to commit time and effort under the objectives stated in §2, which is the honest equivalent for a solo initiative.

## 8. Delivery methodology — how this project actually ran

Stated precisely rather than reaching for the nearest recognizable framework name. This project is **not** Scrum: there were no fixed-length sprints, no sprint ceremonies, and no distinct Scrum roles (Product Owner, Scrum Master, Development Team) — `BACKLOG.md`'s own footnotes have disclosed this honestly since 2026-06-28, describing "Daily Scrum" as adapted terminology for an irregular, session-driven cadence, not literal Scrum practice. It is also **not** Kanban in the strict sense: there was no visualized board, no enforced work-in-progress (WIP) limit, and no cycle-time tracking.

What actually happened is a hybrid: **a phase-gated delivery structure — sequential phases with explicit Definition-of-Ready/Definition-of-Done-style gates between them (e.g. the pre-Phase-5 quality gate, the Phase 8 DoR gate) — with Kanban-influenced continuous backlog management within and across those phases** (items pulled into the backlog as discovered, such as Backlog #9 when RB-10 was observed mid-pilot, rather than batched into planned iterations; work visualized via a live status column rather than a board). This precise characterization is deliberately chosen over either single buzzword: claiming "Scrum" or "Kanban" outright invites a knowledgeable interviewer to probe for practices (sprint length, WIP limits) that were never actually there — the accurate hybrid description is the stronger signal of real methodology judgement, not a weaker one.

---
*Companion artifacts: `PROJECT_REQUIREMENTS_TRACEABILITY_MATRIX.md`, `STAKEHOLDER_REGISTER.md`, `LESSONS_LEARNED.md` (includes the Scope Evolution & Change Log), `RAID_LOG.md`, `BACKLOG.md`, `AI-Agent-Build-Handoff` (current version).*
