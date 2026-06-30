# OneDrive Agent — RAID Log

**Purpose:** Risks, Assumptions, Issues, and Dependencies tracked for this
project, as a standard PM control artifact — separate from `BACKLOG.md`
(which tracks Agile/Scrum-style delivery and process) and the handoff
document (which tracks agreed project state and standing rules). RAID
tracks *what could go wrong, what we're assuming, what has gone wrong, and
what we depend on* — complementary to, not a duplicate of, the other two.

Status values: **Open** (active, not yet resolved/mitigated) | **Closed**
(resolved, mitigated, or no longer applicable, with resolution noted) |
**Monitoring** (not currently active, but being watched)

---

## Risks

Things that **might** happen, with a negative impact if they do.

| # | Raised | Risk | Likelihood | Impact | Mitigation | Status |
|---|---|---|---|---|---|---|
| R1 | 2026-06-28 | Load shedding / power loss interrupts the agent mid-loop, losing progress or leaving an action in an unsafe partial state. | High (recurring, locale-specific operational reality in South Africa) | Medium-High — could lose work, or worse, resume incorrectly into a destructive action without approval. | Phase 4.5: explicit state-machine design with persisted state; `AWAITING_HUMAN_APPROVAL` must never be silently skipped on resume. | Open — design decided (handoff doc v4.0), not yet implemented |
| R2 | 2026-06-30 | Verbal/status-only confirmation between sessions could drift from actual file/repo/Project-knowledge state, since there is no automatic way to verify "done" claims. | Medium (already materialized once — see Issue I1) | Medium — could lead to working from a stale or incorrect document/codebase without realizing it. | Screenshot-verification standing rule adopted (handoff doc v4.0) — checklist items require visual evidence, not verbal confirmation alone. | Monitoring — mitigation in place, watching for recurrence |
| R3 | 2026-06-28 | Real API/network failures (rate limits, connectivity, insufficient credit) during a live Anthropic API call. | Medium (normal for any real API integration) | Low-Medium — would crash the script ungracefully if unhandled. | Specific exception handling implemented in `decision_loop.py` (Phase 3, v3.2) for auth, rate limit, connection, and general API errors. | Closed — mitigated and verified (simulated test of each branch) |
| R4 | 2026-06-28 | An LLM-driven decision loop could return zero, multiple, or unrecognized tool calls, or malformed arguments, none of which a "happy path only" execution loop would handle correctly. | High (normal LLM agent behavior, already observed once — Claude returned two tool calls in the same turn during Phase 3 testing) | Medium — could silently skip work, crash, or call an undefined function. | Named explicitly as a proactive-design standing rule (handoff doc v3.1); to be implemented in Phase 4's execution loop. | Open — design decided, implementation pending (Phase 4) |

---

## Assumptions

Things taken as true without proof, which could turn out to be wrong.

| # | Raised | Assumption | Risk if wrong | Status |
|---|---|---|---|---|
| A1 | 2026-06-30 | A successful `git commit`/`git push` (no error output) means the intended, correct file content was committed. | **Proven false** — see Issue I1. A commit can succeed with completely wrong content (e.g. an accidental overwrite) and show no error at all. | Closed — disproven; replaced by the practice of checking commit insertion/deletion stats and, where it matters, verifying actual committed content (e.g. `git show HEAD:file`). |
| A2 | 2026-06-26 | SendGrid's free tier (100 emails/day) will be sufficient for this project's alerting volume. | Low risk if wrong — alert volume for a personal portfolio project should be very low; would only become a problem under a failure loop sending repeated alerts. | Monitoring |
| A3 | 2026-06-26 | The $6 / minimum Anthropic API credit balance will be sufficient to complete Phases 3 through 7 of testing and development. | Low-Medium — if wrong, would require topping up credit; not a functional blocker, just a cost one. | Monitoring |
| A4 | 2026-06-26 | Python 3.14 (a very new release) will continue to have adequate third-party package support (prebuilt wheels) for the libraries this project needs. | Medium if wrong — already caused one build failure (`tokenizers`/Rust compiler issue), resolved by updating pip; could recur with a different package. | Monitoring |
| A5 | 2026-06-30 | Claude's own approximate dating of log entries (based on system context "today") would be accurate enough for project record-keeping purposes. | Low-Medium — not disproven as factually wrong, but identified as an unreliable practice for a portfolio artifact valuing accuracy; could understate precision if ever scrutinized closely. | Closed — addressed proactively before becoming an Issue, by adopting an explicit convention (handoff doc v4.0) requiring {{owner}} to state dates/times directly rather than Claude approximating them. |

---

## Issues

Things that **have already happened** and required resolution.

| # | Raised | Issue | Root cause | Resolution | Status |
|---|---|---|---|---|---|
| I1 | 2026-06-30 | `README.md` and `BACKLOG.md` were overwritten with one-line placeholder text (via `echo "..." > file`) instead of containing their real, previously-generated content, and this was committed and pushed to GitHub before being caught. | Combination of **Risk R2** (status drift between sessions) and **Assumption A1** (wrongly trusting a clean commit/push as proof of correct content) — the actual files on disk were placeholder versions at the time of commit, not the real ones generated earlier in the session. | Caught via the newly-adopted screenshot-verification rule, by noticing the commit's `84 deletions(-)` stat didn't match what should have been a pure-addition commit. Real files re-downloaded, re-saved locally, re-committed (`198 insertions(+), 2 deletions(-)` — correct signature this time), and verified directly via `git show HEAD:README.md` confirming the actual committed content, not just commit stats. | Closed — resolved 2026-06-30, verified by content inspection, not just commit success |
| I2 | 2026-06-26 | `pip install anthropic` failed during Phase 3 setup: the `tokenizers` dependency attempted to compile from Rust source, and no Rust compiler was present on the machine. | Python 3.14 is a very new release; a prebuilt wheel for `tokenizers` may not yet have been available for it at the time, causing pip to fall back to a source build. | Updated pip first (`python -m pip install --upgrade pip`), after which a prebuilt wheel installed cleanly without needing Rust. | Closed — resolved 2026-06-26 |
| I3 | 2026-06-30 | Confusion over which handoff document version (v3.0 vs v3.2) was actually loaded in Project knowledge, due to an intermediate swap that wasn't explicitly confirmed back in chat. | Same root cause as R2/A1 — reliance on verbal/remembered status rather than verified evidence. | Clarified via direct question and screenshot; correct version (v4.0) confirmed loaded via Project knowledge files panel screenshot. | Closed — resolved 2026-06-29/30 |

---

## Dependencies

Things this project relies on, often external, that aren't directly controlled.

| # | Raised | Dependency | Why it matters | Status |
|---|---|---|---|---|
| D1 | 2026-06-26 | Anthropic API availability and billing (console.anthropic.com) | Phase 3 onward cannot function without a live, funded API key. | Active — funded, key created and working |
| D2 | 2026-06-26 | GitHub availability, as the portfolio repo's host | The actual shareable deliverable lives here; repo visibility (Phase 6) also depends on GitHub. | Active |
| D3 | 2026-06-28 | SendGrid account, sender verification, and API availability | Phase 4.5's email alerting cannot function without this. | Pending — account setup not yet complete |
| D4 | 2026-06-26 | Local machine stability / power supply | The agent's own resilience design (Phase 4.5) exists specifically because this dependency is unreliable (load shedding) — see Risk R1. | Active — ongoing operational reality, not something to "resolve," only design around |

---

## Notes

- This log is reviewed and updated alongside the Daily Scrum entries in
  `BACKLOG.md` — going forward, Daily Scrum retrospective notes should
  reference RAID items by ID (e.g. "see I1") rather than re-narrating full
  incident detail inline, keeping each artifact focused on its own purpose.
- New Risks/Assumptions should be raised proactively, at or before the
  start of a phase where they become relevant — not only logged
  retroactively once they've already become Issues.
