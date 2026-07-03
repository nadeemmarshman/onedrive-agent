# Root Cause Analysis & Remediation Report

**Report ID:** REMEDIATION_2026-07-02_cowork-peer-review
**Date:** 2026-07-02
**Trigger:** Independent peer review of project files, conducted via Claude
Cowork at {{owner}}'s request, following completion of Phase 7.
**Related RAID entry:** I5 (see `RAID_LOG.md`)
**Status:** Closed — all findings remediated and verified same day

---

## Purpose of this report

This document exists as a standalone artefact separate from `RAID_LOG.md`
because the RAID log is deliberately terse — one row per item — and cannot
hold a full root-cause narrative, step-by-step remediation account, or
verification detail without breaking the table's readability. This report
is the detailed backing record; `RAID_LOG.md` Issue I5 is the tracker
entry that points here.

This follows standard incident-management practice: a Root Cause Analysis
(RCA) report sits alongside a RAID or issue log as supporting evidence,
not as a replacement for it.

---

## Review scope and method

Claude Cowork (`claude-sonnet-5`) was given the project's `README.md` first
for context, then asked to review the following files for syntax validity,
internal consistency, and (for the README specifically) standalone
readability:

`README.md`, `BACKLOG.md`, `RAID_LOG.md`, `tools.py`, `tool_contracts.py`,
`decision_loop.py`, `agent_loop.py`, `resilience.py`, `approval_gate.py`,
`test_phase2.py`, `test_phase3_4_45.py`

Critically, Cowork did not just read the code — it **actually ran the test
suite** and **independently fact-checked** the Phase 7 model-comparison
claims against live search, rather than trusting the files at face value.
This is what surfaced Finding 1, which a read-only review would have missed.

---

## Findings, root cause analysis, and remediation

### Finding 1 (Critical) — Test isolation bug causing fixture drift

**What was found:** `test_phase3_4_45.py`'s two Phase 5 integration tests
(`test_integration_full_phase5_approve_all`, `test_integration_full_phase5_reject_all`)
scanned and operated on the **real** `sample_data/` fixture folder rather
than an isolated copy. Because `_execute_delete()` is not mocked in these
tests, running "approve all" genuinely deleted real fixture files
(`notes_copy.txt`, `another_copy.txt`) on every test run.

**Impact observed:** `sample_data/` drifted to 5 files instead of the
expected 6, with only a 2-file duplicate group instead of 3. This caused
`test_phase2.py` to fail 2 unit tests (`Expected 6 files, got 5`;
`Expected the group to contain 3 files, got 2`), which in turn triggered
the test suite's own "skip integration tests if unit tests fail" rule —
so the entire integration test layer was silently not running.

**Root cause:** No test in the suite created an independent copy of test
fixtures before performing destructive operations on them. The tests'
own "rebuild" logic at the top (recreating two files via `Path.write_text()`)
only patched the immediate symptom and would recur on every subsequent run
— not a one-time fluke, a structural gap.

**Remediation:**
1. Rebuilt both integration tests to copy `sample_data/` into a temporary
   directory (`tempfile.mkdtemp()`) via `shutil.copytree()`
2. All scanning and execution within the test now operates entirely on
   the temp copy — the real fixture folder is never touched
3. Temp directory cleaned up in a `finally` block regardless of test outcome

**Secondary drift found during verification:** while confirming the fix,
a related but distinct drift was discovered in the working sandbox: the
buggy tests' `Path.write_text()` recreation of `notes_copy.txt` and
`another_copy.txt` did not include a trailing newline, while the original
fixture file (`original_notes.txt`, created via a shell `echo` command in
Phase 1) does — producing files with matching visible content but
different bytes and MD5 hashes. This meant even "successfully rebuilt"
duplicate files weren't true duplicates by hash, silently breaking the
3-file duplicate-group test case.

**Remediation:** duplicate files recreated as exact byte-for-byte copies
(`shutil.copy`) of the original file, rather than retyping the content
as a string literal.

**Verification:**
- Full 45-test suite (40 unit + 5 integration) re-run: **all 45 pass**
- Fixture file MD5 hashes captured before and after the full suite run:
  **byte-identical**, confirming the real fixture folder is genuinely
  untouched, not just "probably fine"
- `notes_copy.txt`, `another_copy.txt`, and `original_notes.txt` confirmed
  to share the same MD5 hash (`e7aa2172c4e4ec6901bead804306e47e`) after
  the secondary drift fix

---

### Finding 2 (Low) — Broken cross-reference in `resilience.py`

**What was found:** `_masked_user_id()`'s docstring referenced the
credential-exposure risk as "Risk R_SEC_01" in `RAID_LOG.md`. No such
entry ID exists — the actual entry is **R5**.

**Root cause:** An early working label (`R_SEC_01`) used during initial
design discussion was never updated to the real RAID entry ID once R5
was formally logged.

**Remediation:** Docstring corrected to reference `R5`.

**Verification:** Confirmed `R5` exists in `RAID_LOG.md` and the
docstring now matches exactly.

---

### Finding 3 (Low) — Stale status on RAID Risk R1

**What was found:** R1 (load-shedding / power-loss risk) was still
marked "Open — design decided, not yet implemented," despite Phase 4.5
(`resilience.py`) — which directly implements the state-machine mitigation
for this exact risk — being marked complete everywhere else in the project.

**Root cause:** The RAID row's status field was not updated at the point
Phase 4.5 was implemented and verified; the Decision log and phase status
sections were updated, but this particular RAID row was missed.

**Remediation:** R1 updated to "Closed — implemented and verified," with
a note added identifying the specific implementation (`resilience.py`'s
state machine, `agent_state.json` persistence, `check_for_resume()`) and
the unit test that verifies the safety guarantee.

**Verification:** Cross-checked against `resilience.py`'s actual code and
`test_phase3_4_45.py`'s
`test_unit_check_for_resume_awaiting_human_approval_safety` test, both
of which confirm the mitigation is genuinely implemented and tested.

---

### Finding 4 (Low) — README assumption count incorrect

**What was found:** README stated "6 risks, 5 assumptions, 4 issues,
4 dependencies," but `RAID_LOG.md` actually contained 6 assumptions
(A1–A6) at the time of review.

**Root cause:** The summary counts in the README's governance section
were written at an earlier point in the project and not updated when
assumption A6 (model version reproducibility) was added during Phase 7.

**Remediation:** Corrected to "6 risks, 6 assumptions, 5 issues,
4 dependencies" — the issue count also updated to reflect the addition
of I5 (this finding) itself.

**Verification:** Direct count of `RAID_LOG.md` table rows.

---

## Summary

| # | Finding | Severity | Status |
|---|---|---|---|
| 1 | Test isolation bug — real fixture deletion + secondary newline drift | Critical | Closed, verified |
| 2 | Broken cross-reference `R_SEC_01` → `R5` | Low | Closed, verified |
| 3 | Stale RAID R1 status | Low | Closed, verified |
| 4 | README assumption count incorrect | Low | Closed, verified |

**All findings remediated same day (2026-07-02).** No findings required
further investigation or remained open. This review is itself referenced
in the README's Testing approach section as a demonstration of the
project's own stated philosophy — verify rather than assume.
