# Glossary — Acronyms & Abbreviations

**Project:** OneDrive Cleanup Agent — `github.com/nadeemmarshman/onedrive-agent`
**Status:** Canonical. This file is the single authoritative register of every acronym and abbreviation used anywhere in this project. Other documents expand terms on first use (per document and per major section) and point here — they do not duplicate this table.

**Maintenance rule:** whenever a new acronym or abbreviation is introduced in any project artefact, it is (a) written in full with the short form in brackets on first use in that artefact, and (b) added as a row here in the same piece of work. Entries are kept alphabetical. (Standing rule adopted 2026-07-09 — see `AI-Agent-Build-Handoff_v8.0.md`.)

**Scope note:** this glossary covers the build's technical and governance terms only. Career-credential acronyms (e.g. PSM I, PMP, PRINCE2) belong to the Job Search — Resume & LinkedIn project's lane and are deliberately excluded.

| Acronym / Term | Full term | Meaning in this project |
|---|---|---|
| ACL | Access Control List | Windows permission system; test case RB-06 uses an ACL "deny" to prove the agent handles a permission-denied delete gracefully. |
| API | Application Programming Interface | How the agent's Python code communicates with the Anthropic model; also the format the tool contracts follow. |
| BA | Business Analyst | One half of the hybrid role the project demonstrates — requirements, analysis, governance discipline. |
| CP | Checkpoint | The pilot audit's three verification points: CP1 (baseline), CP2 (read-only proof), CP3 (change control). See `TEST_BED_AND_CASES.md` §8. |
| CSV | Comma-Separated Values | File format used for the pilot audit hash manifests exported by `Get-FileHash` at each checkpoint. |
| DoD | Definition of Done | Exit criteria confirming a phase or task is genuinely complete. |
| DoR | Definition of Ready | Entry gate confirming the Phase 8 pilot is safe and ready to run (met and verified 2026-07-05). |
| DR | Disaster Recovery | The recover-from-failure concern behind the pre-run snapshot design decision. |
| GB | Green-line Baseline | Test-case prefix for happy-path cases the agent *should* detect and propose correctly (e.g. GB-01, a true duplicate it must find). |
| GRC | Governance, Risk and Compliance | The assurance-discipline lens applied throughout the build. |
| JSON | JavaScript Object Notation | Data format for the tool contracts and the pre-run snapshot (`pre_run_snapshot.json`). |
| MCP | Model Context Protocol | Anthropic's open standard for tool/connector integration; the tool-contract format mirrors it. |
| MD5 | Message-Digest Algorithm 5 | Hash function used to identify byte-identical duplicate files (chosen for dedup, not as a security control). |
| OG | Open Graph | Metadata standard behind the GitHub repo's link-preview card. |
| PM | Project Manager | The delivery/planning/governance half of the hybrid role. |
| POC | Proof of Concept | An early *feasibility* test — deliberately **not** what Phase 8 is (that role was filled by Phases 1–4 on sample data). |
| RAID | Risks, Assumptions, Issues, Dependencies | The project's governance log (`RAID_LOG.md`). |
| RB | Red-line Baseline | Test-case prefix for negative/edge/adversarial cases the agent must handle *safely* (e.g. RB-01, a near-miss it must **not** flag). |
| SDLC | Software Development Life Cycle | The standard delivery lifecycle the project maps itself onto. |
| SVG | Scalable Vector Graphics | Format of the architecture diagram (`architecture.svg`). |
| UAT | User Acceptance Testing | Validating the built solution against real conditions before rollout — what Phase 8 is. |

---

## Document control

| Field | Value |
|---|---|
| Version | v1.0 |
| Created | 2026-07-09 05:16 |
| Canonical for | All acronym/abbreviation definitions project-wide |
| Referenced from | `README.md`, `AI-Agent-Build-Handoff_v8.0.md`, `TEST_BED_AND_CASES.md` |
| Change rule | New acronym anywhere in the project → new row here, same piece of work |
