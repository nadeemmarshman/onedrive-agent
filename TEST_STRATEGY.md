# Test Strategy & Design — OneDrive Cleanup Agent

**Version:** v1.0
**Date:** 2026-07-05
**Repo:** `github.com/nadeemmarshman/onedrive-agent`
**Closes:** Backlog item #1 (test case design as a separate on-paper deliverable)
**Feeds:** Backlog item #6 / Phase 8 (UAT/Pilot)

---

## 1. Purpose and scope

This is the **on-paper test *design*** companion to the executable test suite. The two are deliberately different artifacts:

- The **test code** (`test_phase2.py`, `test_phase3_4_45.py`, `test_phase5_live.py`) proves *"does each piece work."*
- **This document** designs *"what must be tested, organised by functionality"*, makes coverage and gaps visible, and defines the Phase 8 UAT/Pilot plan. It is the planning layer that sits *above* the two-layer (unit → integration) testing standing rule, not a replacement for it.

Doing this on paper — rather than just describing the tests that already exist — is what surfaces the coverage gaps in Section 4. That is the point of the deliverable.

---

## 2. Coverage map by functionality (Phases 1–5)

Total automated tests: **67** (57 unit + 10 integration), across three suites, plus one manual live-run harness — _63 pre-existing + 4 added in `test_phase8_pre_pilot.py` (see §4)._ Every test below was inventoried directly from the committed source, not from memory.

| Functionality | Module | Unit tests | Integration tests |
|---|---|---|---|
| **File scan** | `tools.scan_folder` | finds-all-files, non-recursive, missing-path-raises, empty-folder (4) | — |
| **Duplicate detection** | `tools.find_duplicates` | detects-true-duplicate, ignores-near-miss, empty-input, no-duplicates-present (4) | — |
| **Convertible detection** | `tools.find_convertible_files` | flags-bmp, ignores-unlisted-extensions, empty-input (3) | — |
| **Action proposal** | `tools.propose_action` | keeps-one-per-group, empty-inputs, never-modifies-filesystem (3) | — |
| **Tool contracts** | `tool_contracts` | — | schema-valid-JSON, names-match-functions, required-fields-match-signature, full-chain (4) |
| **API client** | `decision_loop.get_client` | missing-key, with-key (2) | — |
| **Argument validation** | `agent_loop.validate_arguments` | missing-required, unexpected-arg, valid-passes, none-value (4) | — |
| **Tool execution** | `agent_loop.execute_tool_call` | unrecognised-tool, malformed-arguments, runtime-error-in-tool, valid-execution (4) | full-tool-chain-via-execute (1) |
| **Loop orchestration** | `agent_loop` (main loop) | **— see Gap G1 —** | (partially exercised via chain) |
| **State machine** | `resilience` (states/transitions) | all-states-defined, valid-transitions-complete, invalid-transition-raises, transition-persists-state (4) | state-machine-full-cycle (1) |
| **Resume safety** | `resilience.check_for_resume` | fresh-run, corrupted-json, invalid-state-name, **awaiting-human-approval-safety** (4) | — |
| **State persistence** | `resilience._save_state` | disk-write-failure (1) | — |
| **Credential masking** | `resilience._masked_user_id` | format, short-value, missing-env-vars (3) | — |
| **Alerting** | `resilience` (7 alert types) | auth, rate-limit, connection, api-status, resume-approval, corrupted-state, sendgrid-failure content (7); all-contain-masked-id (1); send-missing-key (1) | error-path-returns-dict-not-raises (1) |
| **Approval gate** | `approval_gate` | snapshot-writes, snapshot-blocked-on-failure, gate-blocked-when-snapshot-fails, invalid-input-reprompts, accepts-no, delete-missing-file, continues-after-failure, unknown-action-type, empty-proposals (9) | full-phase5-approve-all, full-phase5-reject-all (2) |

**Manual harness:** `test_phase5_live.py` — not an automated test; it is the human-supervised live run that writes the pre-run snapshot, presents proposals, and executes approved actions. This is effectively the Phase 8 pilot's execution vehicle.

---

## 3. State-transition test pack

Item #1 specifically called for a dedicated test pack for the Phase 4.5 state machine. The agent is always in exactly one of five states, with transitions defined explicitly in `VALID_TRANSITIONS` (verified from source):

```
SCANNING → AWAITING_DECISION → EXECUTING_TOOL → AWAITING_HUMAN_APPROVAL → DONE
                 ↑______________________|______________________|
                 (loop back for the next decision)
```

| From | Allowed → To | Trigger | Covered by |
|---|---|---|---|
| `SCANNING` | `AWAITING_DECISION` | Scan complete, ask Claude what to do | valid-transitions-complete; full-cycle |
| `AWAITING_DECISION` | `EXECUTING_TOOL` | Claude returns a read/analysis tool call | valid-transitions-complete; full-cycle |
| `AWAITING_DECISION` | `AWAITING_HUMAN_APPROVAL` | Claude proposes a destructive action | valid-transitions-complete |
| `AWAITING_DECISION` | `DONE` | Claude proposes nothing further | valid-transitions-complete |
| `EXECUTING_TOOL` | `AWAITING_DECISION` | Tool result fed back for next decision | valid-transitions-complete; full-cycle |
| `AWAITING_HUMAN_APPROVAL` | `AWAITING_DECISION` | Approved actions done, loop continues | valid-transitions-complete |
| `AWAITING_HUMAN_APPROVAL` | `DONE` | Run finished after approval step | valid-transitions-complete |
| `DONE` | *(terminal — no transitions)* | — | all-states-defined |
| **Any invalid pair** | *(must raise `ValueError`)* | e.g. `SCANNING → DONE` | invalid-transition-raises |

**Safety-critical property (the reason this is modelled explicitly):** on resume after an interruption, the agent must **never silently skip past `AWAITING_HUMAN_APPROVAL`** into executing a deletion. If power cuts out after Claude proposes a delete but before the human approves, resume must land back in "still awaiting approval." This is covered by `test_unit_check_for_resume_awaiting_human_approval_safety` and is the single most important test in the suite from a governance standpoint.

**Persistence:** every transition writes `agent_state.json` before proceeding — covered by transition-persists-state and disk-write-failure.

**Design boundary:** this is a *simple, explicit* state machine (named states + a transition map + a single persisted current-state in JSON), implemented in plain Python — deliberately not an external state-machine framework, which would be disproportionate to the project's scale.

---

## 4. Identified gaps and disposition

The on-paper pass surfaced three coverage gaps plus one recurrence-pattern concern. Each is given an explicit disposition so nothing is silently missing.

| ID | Gap | Type | Disposition |
|---|---|---|---|
| **G1** | **Loop termination is not automatically tested.** `agent_loop.py` has real termination logic — natural stop when Claude stops calling tools, and a `MAX_ITERATIONS = 6` safety cap — but no committed test exercises either path. Proven only by the one-time Phase 4 live run. | Coverage hole | **DONE** — delivered in `test_phase8_pre_pilot.py`: both paths covered (natural stop on a zero-tool-call turn; halt at the `MAX_ITERATIONS` cap), plus a no-execution-after-natural-stop ordering test. Verified green. |
| **G2** | **"Convert" is a stub, not a real action.** `_execute_convert()` only logs intent; actual format conversion is explicitly out of Phase 5 scope. In the pilot, convert *proposals* will appear and be "approved," but no file is converted. | Documented scope boundary (not a defect) | **DOCUMENT** in the UAT acceptance criteria (UAT-05 below), so a reviewer reads the stub as intended behaviour, not a bug. |
| **G3** | **Real-OneDrive conditions are untested and mostly unhandled.** Delete handles `PermissionError`, but nothing addresses online-only / placeholder (reparse-point) files, locked files, long paths, or unicode names — none of which exist in `sample_data/`. Phase 8 is where these first appear. | Real-data risk | **ENUMERATE** as UAT test cases (UAT-06, UAT-07 below) and make a conscious *handle-vs-accept* decision on each during the pilot. |

### 4a. Recurrence-pattern regression guard

Separate from the coverage gaps above: several issues in this project's history were *remediated but could recur*. These split into two classes, each needing a different kind of guard.

| Class | Example issues | Root fix |
|---|---|---|
| **Code-catchable** | **I5** — Phase 5 integration tests deleting the real `sample_data/` fixtures on every run. Verified fixed *once, manually*; nothing prevents a future destructive test reintroducing it. | **ADD a fixture-integrity guard test** (pre-pilot, small): assert `sample_data/` file MD5 hashes are byte-identical before and after the full suite runs. This closes the entire I5 *class* permanently, not just the one instance — the systemic fix, per the project's pattern-escalation rule. |
| **Process-only** | **I1** (placeholder text committed over real files), **I3** (wrong doc version loaded), plus non-persisted work and version-ordering slips. Not catchable by any automated test. | **Pre-commit verification checklist** (Section 6). These are *verification* failures, addressed by the existing screenshot-verify / commit-content-verify / fact-check-against-live-repo standing rules — captured here as one checklist rather than left implicit. |

**Net pre-pilot test additions — DELIVERED in `test_phase8_pre_pilot.py`** (3 unit + 1 integration, authored and verified green against the live source): loop natural-stop [G1], loop safety-cap at `MAX_ITERATIONS` [G1], no-tool-execution-after-natural-stop ordering [G1], and the fixture-integrity guard [I5 class]. Committing this file is a Phase 8 entry criterion (§5.3).

---

## 5. Phase 8 — UAT / Pilot plan

### 5.1 Objective
Validate the already-built, already-tested agent against a **real, limited subset** of live OneDrive data, under the human-approval gate, immediately before full rollout. Labelled **UAT/Pilot, not POC** — feasibility was already proven in Phases 1–4 against synthetic `sample_data/`; this stage validates the finished solution against real conditions.

### 5.2 Subset selection — criteria and process

**Selection criteria:**
- 10–50 files — small enough to review *every* proposed action by eye.
- Contains at least one **genuine duplicate** (same content) so dedup is actually exercised.
- Ideally one `.bmp` to exercise the convert-*proposal* path (stub — see G2).
- All files **downloaded locally**, not online-only placeholders, for run 1 (defers G3 to a deliberate later case).
- Low-stakes content — nothing irreplaceable (approval gate + OneDrive recycle bin are the safety nets, but choose defensively anyway).
- Not the repo folder, not a system or OneDrive-root folder.

**Recommended approach — construct a controlled pilot folder:** copy a handful of real files into a fresh subfolder and add one deliberate duplicate (copy a file, rename it). This gives *real conditions with known expected outcomes* — the strongest form of UAT.

**Scouting method (zero-risk):** point `agent_loop.py` at a candidate folder and run it. `agent_loop.py` **proposes only and never executes** (only `test_phase5_live.py` acts), so it previews what the agent *would* do without touching anything.

**Full construction guide:** see [`TEST_BED_AND_CASES.md`](./TEST_BED_AND_CASES.md) — the step-by-step recipe (test-bed location `C:\OneDrive-Agent_TestBed\`, folder name, per-case *source* and *create* instructions for every green- and red-line scenario, additional scenarios, and an answer key of expected results).

**Selected subfolder:** _[to be recorded here once chosen]_
**Selection rationale:** _[to be recorded]_

### 5.3 Entry criteria (Definition of Ready)
- [ ] All 67 automated tests green (`test_phase2.py`, `test_phase3_4_45.py`, `test_phase8_pre_pilot.py`).
- [ ] `test_phase8_pre_pilot.py` committed (loop termination [G1] + fixture-integrity guard [I5 class] — authored and verified green).
- [ ] Approval gate + snapshot precondition ("no snapshot, no actions") confirmed working.
- [ ] All three surfaces on `claude-sonnet-5`.
- [ ] `SENDGRID_API_KEY` valid (free trial to 2026-08-29).
- [ ] OneDrive recycle bin / version history confirmed available for recovery.
- [ ] Pilot subfolder selected and `starting_folder` updated in both `agent_loop.py` and `test_phase5_live.py`.

### 5.4 UAT test cases (real data)

| ID | Scenario | Expected result | Accept? |
|---|---|---|---|
| UAT-01 | Known duplicate present | Correctly identified via matching MD5; deletion proposed for all-but-one; nothing deleted before approval | Core |
| UAT-02 | Approval gate enforced | A rejected action is skipped; remaining approved actions still execute; no unapproved deletion ever runs | Core |
| UAT-03 | Snapshot precondition | `pre_run_snapshot.json` written *before* any action; records real paths/sizes/hashes; if snapshot fails, all execution blocked | Core |
| UAT-04 | Recovery | An approved-deleted file is recoverable from OneDrive recycle bin | Core |
| UAT-05 | Convert proposal (stub) | Proposal appears; on "approval" the stub logs intent; **no file is converted** — expected behaviour, not a defect [G2] | Core |
| UAT-06 | Online-only / placeholder file present | Observe behaviour (scan size, hash, download trigger); decide handle-vs-accept; document outcome [G3] | Exploratory |
| UAT-07 | Permission-denied / locked file | Graceful handling via the `PermissionError` path; alert fires; loop continues rather than crashing [G3] | Exploratory |
| UAT-08 | Natural termination on real data | Loop stops itself on a zero-tool-call turn — not at the `MAX_ITERATIONS` cap | Core |

### 5.5 Acceptance criteria
**Pass = all Core cases (UAT-01 to -05, -08) met.** Exploratory cases (UAT-06, -07) are for *learning and disposition*, not pass/fail — each produces a documented handle-vs-accept decision, logged in RAID/BACKLOG.

### 5.6 Exit criteria & sign-off
- Result recorded against every UAT case.
- Any defect logged in `RAID_LOG.md` (issue) or `BACKLOG.md`.
- Explicit **go / no-go** decision on expanding to the full OneDrive folder.
- Dated sign-off _(date supplied by Nadeem — Claude does not self-timestamp)_.

### 5.7 Rollback
Primary recovery is OneDrive's built-in recycle bin and version history (30–180 days by plan) — the accepted mechanism per RAID R6. `pre_run_snapshot.json` provides the audit trail of what existed before the run. No agent-managed restore is built (deliberately out of scope — Decision log).

---

## 6. Pre-commit verification checklist (process regression guard)

Run before *any* commit that touches documents or committed content — this is the guard for the process-only recurrence class (I1, I3, non-persisted work, version drift):

- [ ] **Content verified, not assumed:** confirm the file on disk holds the intended content (not a placeholder), e.g. `git show HEAD:<file>` after commit, or a screenshot of the actual content.
- [ ] **Commit stats sanity-checked:** insertions/deletions match the intended change shape (a pure addition should not show large deletions — how I1 was caught).
- [ ] **Right version loaded:** if Project-knowledge files are involved, confirm via screenshot which version is actually loaded before relying on it.
- [ ] **Fact-checked against the live repo:** claims about the build verified against the committed source, not a prior summary.
- [ ] **Handoff-doc staleness check:** after the batch of changes, confirm whether the handoff document has gone stale (repo contents, status lines, decisions) and bump it if so.

---

## Analyst contributions (Nadeem, BA/PM)

Recorded for portfolio visibility. The analytical direction on this test strategy came from Nadeem in his BA/PM capacity — specifics so the contribution is verifiable, not generic:

- **Pre-phase configuration control:** insisted on re-checking `BACKLOG.md`/`RAID_LOG.md` against the *live repo* before starting Phase 8, not trusting a prior-session summary — which surfaced the forgotten open item #1 this document closes.
- **Systemic (not point) controls:** identified that some remediated issues recur, and asked whether a regression pack was needed — directly driving the **fixture-integrity guard** (§4a, RAID I5 class) and the code-catchable vs process-only split.
- **Handover-grade test design:** required the reproducible, red/green-line Test Bed artifact (`TEST_BED_AND_CASES.md`) so any reviewer can prove the solution independently.
- **Traceability:** required that BA/PM contributions be recorded and visible across artifacts.

(Fuller table in `TEST_BED_AND_CASES.md` §10. A standing rule to attribute BA/PM contributions is being added to the handoff document at its next bump.)

---

## Document control

| Field | Value |
|---|---|
| Version | v1.0 |
| Supersedes | — (new artifact) |
| Companion | `TEST_BED_AND_CASES.md` (bidirectional reference) |
| Related | Backlog #1 (closes), Backlog #6 / Phase 8 (feeds), RAID I5 / R6, handoff doc v6.0 |
| Next review | On Phase 8 completion, or when new functions are added |
