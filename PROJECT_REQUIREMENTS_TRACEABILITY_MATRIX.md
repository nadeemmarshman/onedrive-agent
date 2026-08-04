# Requirements Traceability Matrix (RTM)

**Retroactively authored at project closure, 2026-07-20 06:12** (same session and dating convention as `PROJECT_CHARTER.md`) — compiled from requirements that were tracked live throughout the build (in the handoff document's Decision log, `RAID_LOG.md`, and `BACKLOG.md`), not invented after the fact. Its purpose is to show, in one place, that every stated objective traces forward to a concrete requirement, and every requirement traces forward to a specific test case and a verified result — the standard Business Analysis (BA) traceability chain: **Objective → Requirement → Test case → Result → Evidence**.

**Acronyms:** expanded on first use; full register in [`GLOSSARY.md`](./GLOSSARY.md).

---

## 1. How to read this matrix

- **Source** references `PROJECT_CHARTER.md` §2 (Objectives) or §4 (Scope) — every requirement below traces back to one of those.
- **Test case** references the Green-line/Red-line (GB/RB) case IDs defined in `TEST_BED_AND_CASES.md`, or the CP1/CP2/CP3 audit checkpoints defined there (§8).
- **Result** is the actual outcome, stated precisely — including the one case (RB-10) that is exploratory by design and the one case (RB-13) that required redefinition, both disclosed rather than smoothed over in `PILOT_SIGNOFF_SUMMARY.md`.
- **Evidence** points to the RAID Issue ID (`RAID_LOG.md`) and/or the pilot sign-off document section that carries the full write-up. This matrix summarizes; it does not duplicate the full evidence trail.

---

## 2. Functional requirements

| Req ID | Requirement | Source | Test case(s) | Result | Evidence |
|---|---|---|---|---|---|
| REQ-01 | Detect true duplicates by content hash (MD5), not filename | Charter §2 (agent loop objective); §4 in-scope | GB-01, GB-02, GB-04, GB-06 | PASS | `PILOT_SIGNOFF_SUMMARY.md` §2 |
| REQ-02 | Correctly exclude near-duplicates (false-positive guard) — content differs by even one byte | Charter §4 in-scope (exact-hash matching only) | RB-01 | PASS | `PILOT_SIGNOFF_SUMMARY.md` §2 |
| REQ-03 | Document and honor the ratified behaviour for same-content/different-extension files | Charter §4 in-scope; Decision log 2026-07-09 (Decision 4a) | RB-02 | PASS (ratified intended behaviour, not a defect) | `PILOT_SIGNOFF_SUMMARY.md` §2; `TEST_BED_AND_CASES.md` §8.4 |
| REQ-04 | Flag convertible legacy file formats and propose (not silently execute) conversion | Charter §4 in-scope | GB-03 | PASS (proposal path proven; conversion itself is a documented stub) | `PILOT_SIGNOFF_SUMMARY.md` §2 |
| REQ-05 | Leave genuinely unique files untouched — no false positives | Charter §2 (no overclaiming) | GB-05 | PASS | `PILOT_SIGNOFF_SUMMARY.md` §2 |
| REQ-06 | Handle an empty folder gracefully — no crash | Charter §2 (governed against reliably-occurring risks) | RB-03 | PASS | `PILOT_SIGNOFF_SUMMARY.md` §2 |
| REQ-07 | Handle unicode and long filenames without error | Charter §4 (within `pathlib` native support) | RB-04 | PASS | `PILOT_SIGNOFF_SUMMARY.md` §2 |
| REQ-08 | Handle a read-only file's delete attempt safely (succeed or fail gracefully with alert) | Charter §2 (human-approval gate, graceful failure) | RB-05 | PASS | RAID I10; `PILOT_SIGNOFF_SUMMARY.md` §2 |
| REQ-09 | Handle a true ACL-denied delete safely: catch `PermissionError`, log, alert, skip, continue — no crash, no bypass | Charter §2 (human-approval gate) | RB-06 | PASS (proven via standalone targeted fallback run, 2026-07-19 — main run's non-deterministic keep-choice left it unexercised twice) | RAID I12; `PILOT_SIGNOFF_SUMMARY.md` §2–3 |
| REQ-10 | No destructive action executes without explicit human approval; a rejected proposal is skipped and the run continues with the rest | Charter §2 (core objective) | RB-07 | PASS | `PILOT_SIGNOFF_SUMMARY.md` §2 |
| REQ-11 | A deleted file is recoverable via OneDrive's own recycle bin / version history | Charter §2; RAID R6 | RB-08 | PASS (proven live in real synced OneDrive, secondary bed) | RAID I14; `PILOT_SIGNOFF_SUMMARY.md` §2 |
| REQ-12 | "No snapshot, no actions" — execution is hard-blocked if the pre-run audit snapshot cannot be written | Charter §2 (governed UAT/Pilot); RAID R6 | RB-09 | PASS (proven via standalone targeted fallback run — blocks before any approval prompt is even shown, the strongest form of the guarantee) | RAID I13; `PILOT_SIGNOFF_SUMMARY.md` §2–3 |
| REQ-13 | Behaviour on a OneDrive online-only placeholder is investigated and a conscious handle-vs-accept decision made | Charter §4 (explicitly not overclaimed beyond this case) | RB-10 | OBSERVED / EXPLORATORY, by design — not pass/fail. Hydration-on-read confirmed; correctness unaffected; bandwidth/UX trade-off identified. Decision ratified: Option C (opt-in flag, skip-by-default), deferred to post-pilot implementation | RAID I15; Backlog #9; `PILOT_SIGNOFF_SUMMARY.md` §2, §4 |
| REQ-14 | Handle a file exclusively locked by another process gracefully — skip, no crash, rest of run unaffected | Charter §2 (graceful failure handling) | RB-11 | PASS (skip is safe but silent — diagnostic-logging gap logged as Backlog #11, UX polish, not a safety issue) | RAID I17; `PILOT_SIGNOFF_SUMMARY.md` §2 |
| REQ-15 | Handle a zero-byte file without a hashing/divide-by-zero edge case | Charter §2 | RB-12 | PASS | `PILOT_SIGNOFF_SUMMARY.md` §2 |
| REQ-16 | An unplanned crash/interruption during the approval step never results in unapproved execution | Charter §2 (core safety objective); RAID R1 | RB-13 | REDEFINED AND VERIFIED — the literal state-file-resume mechanism (Phase 4.5) was found not wired into the live path; the behavioural safety property that actually matters was verified instead, via a genuine unplanned process kill. Disclosed precisely, not smoothed over. Live wiring deferred to Backlog #10 | RAID I16, R1 (Monitoring); `PILOT_SIGNOFF_SUMMARY.md` §3 |

## 3. Non-functional / governance requirements

| Req ID | Requirement | Source | Test case(s) / mechanism | Result | Evidence |
|---|---|---|---|---|---|
| REQ-17 | Detection is provably read-only — scanning/proposing changes nothing on disk | Charter §2 (no overclaiming); RAID R6 | CP1 → CP2 comparison | PASS — zero differences | `PILOT_SIGNOFF_SUMMARY.md` §1 |
| REQ-18 | Post-execution state equals baseline minus exactly the approved deletions — nothing else moved, renamed, or vanished | Charter §2 (change control) | CP1 → CP3 comparison | PASS | RAID I11 (CP1 baseline recovery nuance, disclosed); `PILOT_SIGNOFF_SUMMARY.md` §1, §3 |
| REQ-19 | Detection results are independently verified by a deterministic, non-AI tool, not the agent auditing itself | Charter §2; `TEST_BED_AND_CASES.md` §8.1 | CP1/CP2/CP3 vs. `Get-FileHash` manifests | PASS | `TEST_BED_AND_CASES.md` §8; `PILOT_SIGNOFF_SUMMARY.md` §1 |
| REQ-20 | Governance artifacts (RAID log, Decision log, backlog) are maintained live throughout the build, evidenced by dated entries and commit history, not reconstructed after the fact | Charter §2 | N/A — process requirement | PASS — evidenced by `RAID_LOG.md`, `BACKLOG.md` Daily Scrum log, and the handoff document's Decision log, all dated and commit-referenced throughout | This RTM itself; `RAID_LOG.md`; `BACKLOG.md` |
| REQ-21 | A formal, explicit sign-off decision is obtained before considering expansion beyond pilot scope | Charter §2 | N/A — governance gate | PASS — signed off by Nadeem Marshman, 2026-07-20 05:46 | `PILOT_SIGNOFF_SUMMARY.md` §5; Backlog #6, #8 |
| REQ-22 | The system does not claim fuzzy/visual near-duplicate detection — exact content-hash matching only, disclosed precisely | Charter §4 (explicitly out of scope) | N/A — scope statement, checked at sign-off | PASS — sign-off wording checked and confirmed non-overclaiming | RAID A10 (Closed at sign-off); `PILOT_SIGNOFF_SUMMARY.md` §4 |
| REQ-23 | Artefacts derived from scanning **real** personal data must be reviewed for disclosure before being committed to a repository whose visibility is public, and must not carry real file paths, filenames or identifiers | Raised 2026-08-02 from RAID I27 (breach), not from the original Charter — the Charter scoped the agent against synthetic `sample_data/`, so the risk did not exist at baseline and was introduced by the live-run phases | Automated: `check_staged_for_personal_data.py` pre-commit hook, run on every commit; covered by `test_personal_data_guard.py` (structural + token-layer unit tests). Manual: scrub-check of any new content against specifically-named sensitive terms before commit, not solely reliant on the automated token list (see `LESSONS_LEARNED.md` §2 lesson 10) | **FAIL then REMEDIATED, control now live and exercised repeatedly.** Breached for ~2 days (3 commits, repo public) in the original incident; repo made private and verified via unauthenticated API (200 → 404), all scan artefacts sanitised and independently verified to contain zero sensitive tokens. The pre-commit guard has since blocked real leaks pre-commit on at least 5 separate occasions across this project (documented per-incident in `LESSONS_LEARNED.md` §2 lesson 8) and been extended twice for defects found in its own logic (RAID I29's placeholder-masking bug; RAID I30's substring-matching lesson). Git-history purge and re-publication still open | `RAID_LOG.md` I27, I29, I30, I31; `LESSONS_LEARNED.md` §2 lessons 8, 9, 10; `check_staged_for_personal_data.py`; `test_personal_data_guard.py`; `.githooks/pre-commit`; `sanitize_repo_artifacts.py`; `.gitignore`; `BACKLOG.md` #18, #19 |

---

## 4. Coverage summary

- **23 requirements** traced. REQ-01–22 are all derived from `PROJECT_CHARTER.md` §2/§4 — none invented for this matrix that weren't already implicit in the charter's stated objectives and scope. **REQ-23 is the sole exception and is deliberately marked as such**: it was raised 2026-08-02 from RAID I27, a real breach, and could not have come from the charter because the charter scoped the agent against synthetic `sample_data/`. The risk it addresses was introduced later, by the live-run phases pointing the agent at real personal data.
- **19 of 19** green-line/red-line test cases closed (16 functional above map 1:1 to GB/RB cases; GB-01/02/04/06 are grouped under REQ-01 as they all prove the same detection requirement at different structural angles).
- **3 governance/audit requirements** (REQ-17–19) verified via the CP1/CP2/CP3 independent audit-control regime, not the agent's own self-report.
- **2 requirements carry an honest, non-clean *result***, stated precisely rather than rounded up to a plain PASS: REQ-13 (RB-10, exploratory by design, not pass/fail) and REQ-16 (RB-13, redefined and verified empirically after the originally-specified mechanism was found not wired into the live path).
- **3 further requirements carry a non-clean *execution path* but a clean result**: REQ-09 (RB-06), REQ-12 (RB-09), and REQ-14 (RB-11, arguably — the substitution and single-script mechanics were adjusted, not the outcome) all required a standalone, targeted fallback run rather than being naturally exercised by the main pilot sequence (RB-06's precondition — the model's own non-deterministic keep-choice never selected the target file — recurred on both the dry run and the live run). Each did ultimately reach a genuine PASS with real evidence; this line exists so "which cases needed extra work to prove" is visible alongside "which results were less than clean," rather than the two being conflated.
- **One requirement failed outright: REQ-23.** This line previously read "Zero requirements failed outright" and was correct at pilot sign-off (2026-07-20); it is corrected here rather than quietly reworded, because the failure happened afterwards, during the live-run phases. Real personal file paths were published to a public repository for ~2 days across three commits (RAID I27). It is recorded as **FAIL then REMEDIATED**, not softened to a PASS: the repo was made private and independently verified, and all scan artefacts were sanitised and verified clean — but the breach genuinely occurred, and a control that has to be retrofitted after an incident is not the same as one that held. Git-history purge and the re-publication decision remain open.
- **All requirements up to pilot sign-off passed.** Every limitation disclosed at that point (RB-10's hydration trade-off, RB-13's mechanism gap, RB-11's silent-skip UX gap) is carried forward as a tracked, deliberately post-pilot backlog item — not a hidden gap.

---
*Companion artifacts: `PROJECT_CHARTER.md`, `STAKEHOLDER_REGISTER.md`, `LESSONS_LEARNED.md`, `PILOT_SIGNOFF_SUMMARY.md`, `TEST_BED_AND_CASES.md`, `RAID_LOG.md`, `BACKLOG.md`.*
