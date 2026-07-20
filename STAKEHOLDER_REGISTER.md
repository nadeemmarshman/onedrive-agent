# Stakeholder Register

**Retroactively authored at project closure, 2026-07-20 06:12** (same session and dating convention as `PROJECT_CHARTER.md` and the Requirements Traceability Matrix) — this register documents who had a stake in this project and how they were actually engaged, not an idealized org chart invented after the fact. For a solo portfolio initiative, most rows collapse onto one person; that is stated plainly rather than padded out to look larger than it was.

**Acronyms:** expanded on first use; full register in [`GLOSSARY.md`](./GLOSSARY.md).

---

## 1. Register

| Stakeholder | Role(s) | Category | Interest in the project | Influence / power | Engagement approach used |
|---|---|---|---|---|---|
| Nadeem Marshman | Sponsor, Project Manager, Business Analyst | Internal — sole principal | High — the project exists to build his portfolio and job-market case | High — sole decision authority on scope, sign-off, and direction | Continuous, direct: every scope decision, checkpoint gate, and the formal Phase 8 sign-off ran through him directly, in real time, logged in the handoff document's Decision log |
| Claude (Claude Code / Claude Project sessions) | Delivery collaborator | Internal — AI assistant, under direction | High — executes the build and governance-artifact drafting under Nadeem's direction | Low — no independent decision authority; every non-trivial choice escalated for a human decision rather than assumed | Instructed, session by session, per the honest-attribution standing rule; outputs presented for review before being treated as final (e.g. this register, the Charter, and the RTM were all drafted, reviewed, and only then committed) |
| Claude Cowork | Narrative auditor (Phase 7 comparison; advisory input during Phase 8) | Internal — AI tool, secondary surface | Medium — provided an independent peer-review pass (2026-07-02) and served as the non-gating narrative auditor in the CP1–CP3 audit-control regime | Low — advisory only; `TEST_BED_AND_CASES.md` §8.1 explicitly excludes it from the gating decision because it is correlated (same underlying model family) with the system under test | Used deliberately for what it's good at (narrative/organisation commentary, independent code review) and deliberately excluded from what it can't independently prove (deterministic duplicate-detection ground truth — that gate belongs to `Get-FileHash` alone) |
| Prospective employers / interviewers | End reviewer / real "customer" | External | High — the actual audience this artifact is built to be read by, even though they were never directly consulted during the build | None, formally — no direct input into scope or decisions during delivery | Represented indirectly throughout by design choices aimed at readability, honesty, and verifiability (e.g. `TEST_USE-CASES_PLAIN_ENGLISH.md` restates every test case for a non-technical reviewer; every claim is evidenced rather than asserted) — their interests were anticipated, not gathered |
| Parallel Claude Project session (Job Search — Resume & LinkedIn project) | Downstream consumer of this project's outputs (résumé bullets, executive summary, sign-off status) | Internal — a separate, related workstream under the same principal | Medium — depends on this project's outputs being accurate and current (e.g. the sign-off status, the exec summary) to do its own job correctly | Low-Medium — has flagged issues and suggested refinements into this project on occasion (see `BACKLOG.md`, 2026-07-04 Daily Scrum entry: "cross-project instruction spillover"), but every such suggestion was independently verified here before acting on it, not executed at face value | Cross-project notification pattern: this project notifies that workstream of material status changes (e.g. formal sign-off) rather than that workstream polling or assuming; suggestions flowing the other direction are reviewed here, not auto-applied — see the 2026-07-04 incident where one of four suggested refinements was rejected outright as factually wrong about this project's code structure |

## 2. Stakeholders deliberately not modelled as separate rows

Recorded so the register's boundaries are explicit, not accidental:

- **Anthropic (API provider) and GitHub (repo host)** are tracked as **Dependencies** (`RAID_LOG.md`, D1/D2), not stakeholders — they have no interest in or influence over this specific project's outcomes; they are infrastructure this project depends on, the opposite relationship.
- **SendGrid** is likewise a Dependency (D3), not a stakeholder, for the same reason.
- **A formal Product Owner, Scrum Master, or separate Development Team** do not exist as distinct roles — see `PROJECT_CHARTER.md` §8 for why this project is deliberately not described as textbook Scrum. Modelling these as separate stakeholder rows here would misrepresent a one-person initiative as a team of several.

## 3. Why this register matters for a solo project

A one-person initiative can make stakeholder analysis feel like a formality with an obvious, single answer. It is included here anyway, for two reasons: (1) it makes explicit that even a solo project has *multiple, distinct* stakeholder interests — Nadeem's own three roles (Sponsor/PM/BA) genuinely can and do pull in different directions at different moments (a Sponsor wants the project to look complete; a BA is the one who insists a limitation gets disclosed anyway) and separating them, even nominally, is what let the honest-disclosure standing rule survive scope pressure throughout the build; (2) it demonstrates the BA discipline of identifying *indirect* stakeholders (prospective employers, the parallel career-focused workstream) whose interests were never in the room but still shaped real decisions — the strongest portfolio signal a stakeholder register can carry for a solo project is showing that the analysis wasn't skipped just because the headcount was one.

---
*Companion artifacts: `PROJECT_CHARTER.md`, `PROJECT_REQUIREMENTS_TRACEABILITY_MATRIX.md`, `LESSONS_LEARNED.md`, `RAID_LOG.md`, `BACKLOG.md`.*
