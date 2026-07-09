# Test Bed & Test Cases — OneDrive Cleanup Agent

**Version:** v2.0
**Date:** 2026-07-09
**Repo:** `github.com/nadeemmarshman/onedrive-agent`
**Companion to:** [`TEST_STRATEGY.md`](./TEST_STRATEGY.md) — this document is the hands-on construction guide for the Phase 8 User Acceptance Testing (UAT) / Pilot test bed defined there (§5). Read `TEST_STRATEGY.md` first for the *why*; this document is the *how*.
**Acronyms:** expanded on first use per document and per major section; full register in [`GLOSSARY.md`](./GLOSSARY.md).

**What changed in v2.0:** added §8 — the pilot audit-control regime (checkpoints CP1/CP2/CP3, independent-tool reconciliation, and the signed-off materiality rule); updated the run sequence (§9) and handover checklist (§10) to weave the checkpoints in; recorded environment exclusions surfaced 2026-07-08; case prefixes GB/RB now defined explicitly. Test cases GB-01…GB-06 and RB-01…RB-13 and the answer key (§7) are unchanged from v1.0. Full change history in §12.

---

## 1. Purpose and handover intent

This is a **self-contained, reproducible recipe** for building a controlled test bed that proves the OneDrive Cleanup Agent works — as a concept and as a solution. It is deliberately written so that **anyone** (a reviewer, a new team member, an interviewer given the repo) can follow it start-to-finish and reach the same known-good result, with no reliance on the author's specific OneDrive contents.

It delivers the "controlled pilot folder" approach recommended in `TEST_STRATEGY.md` §5.2: **real files in a controlled folder, with a known answer key**, so every proposed action can be checked against a documented expected outcome — the strongest form of UAT.

Two ways to populate every case are given:
- **Source (real):** copy an existing file from OneDrive or the local drive — proves behaviour on genuine data.
- **Create (synthetic):** generate the file from a command — makes the bed fully reproducible by anyone, on any machine.

All commands are **Windows PowerShell** (the project's platform: Windows, Python 3.14).

**Case-ID prefixes used throughout:** **GB = Green-line Baseline** — happy-path cases the agent *should* detect and propose correctly. **RB = Red-line Baseline** — negative, edge, and adversarial cases the agent must handle *safely* (decline correctly, or fail gracefully without crashing or bypassing a safety control).

---

## 2. Test bed location and name

| Setting | Value | Why |
|---|---|---|
| **Root** | `C:\` (drive root) | Specified by Nadeem (Business Analyst / Project Manager, BA/PM). Top-level, obvious, and — critically — **outside both the repo and the OneDrive-synced tree**. |
| **Folder name** | `OneDrive-Agent_TestBed` | Apt and self-describing; hyphen mirrors the repo slug convention. |
| **Full path** | `C:\OneDrive-Agent_TestBed\` | The value to set as `starting_folder` for the pilot. |

**Why outside the repo:** the repo lives at `C:\Dev\onedrive-agent\`. Putting the test bed there would make the agent scan its own codebase and risk Git churn — the same reasoning that keeps the code out of OneDrive (see handoff Decision log).

**Why outside OneDrive sync — and the one nuance a reviewer should know (BA-surfaced):**
A `C:\`-root folder is *not* under OneDrive, so:
- ✅ No sync churn while you build/tear down the bed repeatedly.
- ✅ Deletions still go to a recycle bin — but the **Windows** Recycle Bin, *not* OneDrive's.
- ⚠️ RAID (Risks, Assumptions, Issues, Dependencies) item **R6** names *OneDrive's* recycle bin / version history as the recovery mechanism. To validate **that specific path** (test case **RB-08**), you need one run inside an actual OneDrive subfolder. This is called out explicitly rather than left as a silent gap.

**Recommendation:** use `C:\OneDrive-Agent_TestBed\` for the main bed (cases GB-01…RB-07, RB-09), and build a small **secondary bed under OneDrive** only for the two OneDrive-specific cases (RB-08 recycle-bin recovery, RB-10 online-only). Both are described below. *(This two-bed design was reviewed and deliberately reaffirmed on 2026-07-09 after the local OneDrive environment changed — see §8.5.)*

**The pilot bed is NOT the real Documents folder.** The live, fully-hydrated `Documents` tree is the eventual **rollout target** (post-sign-off), never the pilot bed: it holds irreplaceable files, and — the UAT-defining reason — it has real duplicates with *unknown ground truth*. UAT validates against a **known answer key** (§7); you cannot validate correctness against an answer you don't have.

---

## 3. Build the test bed — prerequisites and folder

**Prerequisites**
- Repo cloned at `C:\Dev\onedrive-agent\`, all automated tests green (`test_phase2.py`, `test_phase3_4_45.py`, `test_phase8_pre_pilot.py`).
- `ANTHROPIC_API_KEY` and `SENDGRID_API_KEY` set as environment variables.

**Create the root folder and a nested subfolder** (the nested one is for the cross-folder duplicate case):

```powershell
New-Item -ItemType Directory -Force -Path "C:\OneDrive-Agent_TestBed"
New-Item -ItemType Directory -Force -Path "C:\OneDrive-Agent_TestBed\archive"
Set-Location "C:\OneDrive-Agent_TestBed"
```

---

## 4. Green-line test cases (agent SHOULD detect / propose correctly)

Green-line = the happy path. The agent must correctly find what's there and propose the right action — but still **never act without approval**.

### GB-01 — True duplicate (identical content, different name)
*Proves:* content-hash dedup (not filename matching).
- **Source (real):** `Copy-Item "$HOME\OneDrive\Documents\<some-file>.pdf" ".\report.pdf"; Copy-Item ".\report.pdf" ".\report_COPY.pdf"`
- **Create (synthetic):**
  ```powershell
  Set-Content -Path ".\report.txt" -Value "Quarterly report body. Line two." -NoNewline
  Copy-Item ".\report.txt" ".\report_COPY.txt"
  ```
*Expected:* both flagged as one duplicate group (matching MD5 hash); delete proposed for one, keep the other. Nothing deleted before approval.

### GB-02 — Duplicate group of three
*Proves:* the "keep exactly one per group" rule at group size > 2.
```powershell
Copy-Item ".\report.txt" ".\report_v2.txt"   # third identical copy (after GB-01)
```
*Expected:* one group of three; keep 1, propose delete 2.

### GB-03 — Convertible file (`.bmp`)
*Proves:* the convert-*proposal* path. **Note:** conversion is a STUB (see `TEST_STRATEGY.md` gap G2) — a proposal appears, but no file is converted. That is expected, not a defect.
- **Source (real):** `Copy-Item "C:\path\to\any.bmp" ".\old_photo.bmp"`
- **Create (synthetic):**
  ```powershell
  Add-Type -AssemblyName System.Drawing
  $b = New-Object System.Drawing.Bitmap 8,8
  $b.Save("C:\OneDrive-Agent_TestBed\old_photo.bmp"); $b.Dispose()
  ```
*Expected:* `old_photo.bmp` flagged as convertible; convert proposed; on approval the stub logs intent, file unchanged.

### GB-04 — Cross-folder duplicate (recursion)
*Proves:* `scan_folder(recursive=True)` finds duplicates across subfolders.
```powershell
Copy-Item ".\report.txt" ".\archive\report_archived.txt"
```
*Expected:* the copy in `archive\` joins `report.txt`'s duplicate group.

### GB-05 — Unique file (true negative)
*Proves:* genuinely unique files are left alone (no false positives).
```powershell
Set-Content -Path ".\unique_memo.txt" -Value "This content appears nowhere else." -NoNewline
```
*Expected:* not part of any duplicate group; no action proposed for it.

---

## 5. Red-line test cases (agent must NOT act wrongly / must fail SAFELY)

Red-line = negative, edge, and adversarial conditions. The agent must either correctly decline to act, or handle the condition gracefully without crashing or bypassing a safety control.

### RB-01 — Near-miss (similar but NOT identical)
*Proves:* the false-positive guard — near-duplicates must **not** be flagged.
```powershell
Set-Content -Path ".\notes.txt"    -Value "Meeting notes. Action items below." -NoNewline
Set-Content -Path ".\notes_v2.txt" -Value "Meeting notes. Action items below!" -NoNewline  # one char differs
```
*Expected:* different MD5 → **not** flagged as duplicates. No deletion proposed.

### RB-02 — Same content, different extension
*Proves:* documented behaviour on an ambiguous case (content hash treats these as duplicates regardless of extension).
```powershell
Set-Content -Path ".\data.txt" -Value "identical payload" -NoNewline
Copy-Item ".\data.txt" ".\data.log"
```
*Expected:* flagged as a duplicate group (content-identical). **Ratified 2026-07-09 (Decision 4a):** this is the agreed, intended behaviour — an in-scope duplicate for both the agent and the audit reconciliation (§8) — not a bug and not an exclusion.

### RB-03 — Empty folder
*Proves:* graceful handling of the empty-input boundary.
```powershell
New-Item -ItemType Directory -Force -Path ".\empty_dir"
```
*Expected:* no crash; nothing proposed for `empty_dir`; loop terminates naturally.

### RB-04 — Unicode and long filenames
*Proves:* filename edge handling (within `pathlib`'s native support — see out-of-scope note).
```powershell
Set-Content -Path ".\café_notés_ünïcode.txt" -Value "unicode name test" -NoNewline
$long = ".\" + ("a" * 120) + ".txt"
Set-Content -Path $long -Value "long name test" -NoNewline
```
*Expected:* scanned and handled without error; no crash on the names themselves.

### RB-05 — Read-only file
*Proves:* a read-only attribute is surfaced/handled, not silently mishandled.
```powershell
Copy-Item ".\report.txt" ".\locked_readonly.txt"
Set-ItemProperty -Path ".\locked_readonly.txt" -Name IsReadOnly -Value $true
```
*Expected:* if proposed for deletion and approved, the delete either succeeds (read-only alone doesn't always block delete) or fails **gracefully** via the `PermissionError` path with an alert — loop continues.

### RB-06 — Permission-denied on delete (true ACL deny)
*Proves:* the `PermissionError` handling path in `approval_gate._execute_delete` under a real denied Access Control List (ACL).
```powershell
Copy-Item ".\report.txt" ".\denied.txt"
icacls ".\denied.txt" /deny "$($env:USERNAME):(DE)"   # deny DElete to current user
# teardown later:  icacls ".\denied.txt" /remove:d "$env:USERNAME"
```
*Expected:* on approved delete, the agent catches `PermissionError`, logs/alerts an actionable message, **skips** the file, and **continues** with other approved actions — no crash.

### RB-07 — Reject-then-continue (behavioural, at run time)
*Proves:* the approval gate skips a rejected action and still executes the rest.
- No file setup — exercised during the run: when prompted, **reject** one proposed deletion and **approve** another.
*Expected:* rejected item skipped, approved item executed, run completes cleanly.

### RB-08 — OneDrive recycle-bin recovery *(secondary bed, under OneDrive)*
*Proves:* the RAID R6 recovery mechanism specifically.
```powershell
# Build a tiny secondary bed inside OneDrive:
$od = "$HOME\OneDrive\OneDrive-Agent_TestBed_OD"
New-Item -ItemType Directory -Force -Path $od
Set-Content -Path "$od\r.txt" -Value "recoverable" -NoNewline
Copy-Item "$od\r.txt" "$od\r_copy.txt"
```
Point `starting_folder` at `$od`, run, approve the delete of `r_copy.txt`, then confirm it appears in **OneDrive's** Recycle Bin and can be restored.
*Expected:* deleted file recoverable from OneDrive recycle bin / version history.

### RB-09 — Snapshot precondition ("no snapshot, no actions")
*Proves:* execution is blocked if the pre-run snapshot cannot be written.
- Simulate by making the snapshot target unwritable (e.g. temporarily create a **directory** named `pre_run_snapshot.json`, or deny write on it), then run.
*Expected:* the agent refuses to execute any action and reports the blocked snapshot — the hard governance precondition holds.

### RB-10 — Online-only / placeholder file *(secondary bed, under OneDrive)* — EXPLORATORY
*Proves / investigates:* behaviour on a OneDrive placeholder (gap G3 — currently unhandled). A placeholder ("online-only") file shows in File Explorer but its content lives only in the cloud — on disk it is effectively a 0-byte stub, so an unguarded content-hash could (1) hash "nothing" and falsely group unrelated placeholders as duplicates, (2) trigger a hydration download, or (3) error. The purpose of this case is to **observe which happens** and then make a conscious handle-vs-accept decision.
```powershell
# In the OneDrive secondary bed, make a file online-only:
attrib +U -P "$od\r.txt"   # or: right-click -> "Free up space"
```
*Expected:* **observe** — does scan read 0 bytes, trigger a download, or hash oddly? Record the outcome and make a conscious **handle-vs-accept** decision (log in RAID/BACKLOG). Not pass/fail.
**Environment note (2026-07-09):** the live Documents tree is now fully hydrated, so placeholders no longer occur naturally on this machine — this case must be *deliberately created* with the command above. **Confirmed in scope 2026-07-09**: it probes the one genuinely unhandled risk in the real deployment target, and "false duplicates from unread placeholders" is exactly the silent, destructive failure class the governance layer exists to prevent. Pilot sign-off must not claim placeholder coverage beyond this single exploratory case.

---

## 6. Additional scenarios folded in (computed)

Beyond the core set, these strengthen the bed and are recommended for a thorough pilot:

| ID | Scenario | Proves | Setup |
|---|---|---|---|
| **RB-11** | Locked file (open by another process) | Graceful handling when a file is exclusively locked | In a 2nd PowerShell: `$f=[IO.File]::Open("C:\OneDrive-Agent_TestBed\report.txt",'Open','Read','None')` — run the agent, then `$f.Close()` |
| **RB-12** | Zero-byte file | No divide-by-zero / hash edge on empty content | `New-Item -ItemType File -Path ".\empty.txt"` |
| **RB-13** | Interrupted run → resume safety | The crown-jewel: resume must land in `AWAITING_HUMAN_APPROVAL`, never auto-execute | Start a run; when it reaches the approval prompt, kill the process (close the window); restart — confirm it resumes **awaiting approval**, not executing |
| **GB-06** | Mixed realistic folder | End-to-end on a representative mix | Combine GB-01…GB-05 in one run |

**RB-13 is the single most important behavioural test** — it directly exercises the `AWAITING_HUMAN_APPROVAL` safety guarantee (`test_unit_check_for_resume_awaiting_human_approval_safety` proves it in code; RB-13 proves it live).

---

## 7. Answer key (expected results for the main bed)

After building the green-line cases (GB-01…GB-05) plus RB-01, RB-02, RB-04, RB-05, RB-06 in `C:\OneDrive-Agent_TestBed\`:

| Item(s) | In a duplicate group? | Proposed action |
|---|---|---|
| **Group A (6 files)** — `report.txt`, `report_COPY.txt`, `report_v2.txt`, `archive\report_archived.txt`, `locked_readonly.txt`, `denied.txt` | Yes — one **6-file** group. All are byte-identical copies of `report.txt` (RB-05/RB-06 copy it too), so content-hash dedup merges them into a single group. | Keep 1, propose **delete 5**. Two of those five exercise execution edges: `locked_readonly.txt` (RB-05, read-only) and `denied.txt` (RB-06, ACL-denied) — the *proposal* is normal; the *execution outcome* is what RB-05/RB-06 test. |
| **Group B (2 files)** — `data.txt`, `data.log` | Yes — one 2-file group (same content, different extension — RB-02, ratified intended behaviour) | Keep 1, delete 1 |
| `old_photo.bmp` | No | Convert (stub — logs only) |
| `unique_memo.txt` | No | None |
| `notes.txt`, `notes_v2.txt` | **No** (near-miss — RB-01) | None |
| `café_notés_ünïcode.txt`, long-name file | No | None |

**Note:** this key reflects the **synthetic** build commands (§4/§5). If you populate a case via its *Source (real)* option instead, the filenames differ but the grouping behaviour is identical. If you want RB-05/RB-06 to be *standalone* deletes rather than members of Group A, give `locked_readonly.txt`/`denied.txt` unique content and pair each with its own single duplicate.

Any deviation from this key is a defect → log in `RAID_LOG.md` / `BACKLOG.md`.

---

## 8. Pilot audit-control regime — independent verification checkpoints (CP1 / CP2 / CP3) *(NEW in v2.0)*

Adopted 2026-07-09 (designed 2026-07-08/09; reconciliation rule signed off by Nadeem — see handoff v8.0). This section is the **canonical text** of the regime; the handoff document summarises and points here.

### 8.1 Why: independence, and where it actually lives

The agent under test is Claude-driven (Anthropic Application Programming Interface (API), `claude-sonnet-5`). Claude Cowork is *also* Claude — so a Cowork audit report is **correlated** with the system under test: a shared-model quirk could appear in both and produce *false agreement*. The genuinely independent leg is a **deterministic, non-AI tool** — and for duplicate detection (a hash-comparison fact, not a judgement) deterministic evidence is the *stronger* proof.

**Roles (kept strictly apart):**

| Role | Actor | Gating? |
|---|---|---|
| System under test | The agent (`agent_loop.py` dry-run; `test_phase5_live.py` live) | — |
| Independent deterministic auditor | PowerShell `Get-FileHash -Algorithm MD5` manifest (same algorithm as the agent → exact hash-to-hash reconciliation) | **Yes — primary gate** |
| Narrative auditor | Claude Cowork report (folder schema, rename/organisation commentary) | **No** — advisory only; correlated with the system under test |
| Governance / decision layer | The Claude Project chat: reconciliation, go/no-go, sign-off, RAID and handoff updates | — |

`dupeGuru` was **considered and rejected** (2026-07-09): a second deterministic tool duplicating the same hash comparison — install/config overhead for marginal, cosmetic assurance. `Get-FileHash` is the sole independent gate.

### 8.2 The three assertions (checkpoints)

| CP | When | Assertion proven | Pass condition |
|---|---|---|---|
| **CP1 — Baseline** | Bed built, before any agent scan | What exists, and which groups are byte-identical | Agent-detected duplicate groups (dry-run) **agree** with the `Get-FileHash` manifest per §8.4 |
| **CP2 — Read-only proof** | After all scans (agent dry-run + optional Cowork narrative scan), before any approval/action | *Detecting* duplicates changed nothing | CP2 manifest **identical** to CP1 manifest (in-scope set) |
| **CP3 — Change control** | After approved actions execute | Only the approved changes happened | CP3 manifest = CP1 manifest **minus exactly the approved-deletion set** — nothing else moved, renamed, or vanished |

This makes the existing Phase 5 `pre_run_snapshot.json` control *independently verifiable* rather than self-attested.

### 8.3 Producing a manifest

Manifests are stored **outside the bed** (so audit artefacts never contaminate the scan target and never appear in a later manifest as "unexplained new files"):

```powershell
New-Item -ItemType Directory -Force -Path "C:\OneDrive-Agent_Audit"
Get-ChildItem -Path "C:\OneDrive-Agent_TestBed" -Recurse -File |
  Get-FileHash -Algorithm MD5 |
  Select-Object Hash, Path |
  Sort-Object Path |
  Export-Csv -Path "C:\OneDrive-Agent_Audit\CP1_manifest.csv" -NoTypeInformation
```

Repeat with `CP2_manifest.csv` / `CP3_manifest.csv` at the later checkpoints. Comparing two manifests:

```powershell
Compare-Object (Import-Csv "C:\OneDrive-Agent_Audit\CP1_manifest.csv") `
               (Import-Csv "C:\OneDrive-Agent_Audit\CP2_manifest.csv") `
               -Property Hash, Path
# No output = identical (CP2 pass). Any output rows = differences to classify per §8.4.
```

### 8.4 Reconciliation & Materiality Rule (v1.0 — signed off 2026-07-08/09)

**Applies to** every checkpoint comparison (CP1 cross-tool baseline; CP2 read-only proof; CP3 change control).

**Comparison key.** A *duplicate group* = a set of ≥2 files with identical MD5 hashes. Two reports **agree** when they yield the identical set of duplicate groups, a group's identity being its MD5 value **plus** the set of full file paths in it. Comparison is order-independent.

**In-scope target set.** Regular, readable files under the pilot bed root, minus the excluded classes below. Defined once **before CP1** and frozen for the run.

**Gating discrepancies — must be ZERO to proceed:**
- A file in one tool's manifest but absent from the other's, within the in-scope set.
- A duplicate group found by one tool but not the other (different membership or MD5).
- Any hash mismatch on a file both tools scanned.
- *(CP2)* **Any** change between CP1 and CP2 in-scope — detection must be read-only.
- *(CP3)* **Any** post-action difference from the CP1 baseline other than the exact approved-deletion set.

**Non-gating differences — logged, not blocking (expected/immaterial):**
- Excluded file classes: hidden/system files, `.git/` internals, OneDrive online-only stubs, Operating System (OS) artefacts (`desktop.ini`, `Thumbs.db`), zero-byte files (recorded separately — **Decision 4b, ratified 2026-07-09:** logged, not gating, never silently dropped; all empty files share one hash, so "duplicate" groupings among them are coincidence of emptiness, not meaningful duplication).
- Advisory/narrative content only one tool emits — Cowork's rename/schema/organisation suggestions or any human-readable commentary (not duplicate-identity claims; outside the comparison entirely).
- Presentation-only differences: ordering, hash-string casing, path-separator style, summary sections.
- Metadata/timestamp-only differences where content hash is identical.

**Ratified edge treatments (2026-07-09):**
- **Same content, different extension (RB-02) = in-scope duplicate** (Decision 4a). Both the agent and `Get-FileHash` will group them; agreement expected.
- **Zero-byte files = logged, non-gating** (Decision 4b), as above.

**Gate outcome.** A folder proceeds to UAT action (CP3) only if CP1 shows zero gating discrepancies **and** CP2 shows zero change from CP1. Any gating discrepancy **halts** the pilot → logged to RAID → root-caused → resolved → re-run from CP1.

### 8.5 Environment notes & exclusions (surfaced 2026-07-08, screenshots on file)

| Observation | Classification | Treatment |
|---|---|---|
| `My Music`, `My Pictures`, `My Videos` show OneDrive sync errors ("No access permissions to the item") | OneDrive *account-level* issue — out of this project's lane; not an agent defect | **Excluded from all beds.** Fix separately. The access-denied *class* is already covered synthetically by RB-06, so pilot coverage is not lost. |
| `Abbys` folder carries a shared-folder marker | Shared folders have different permission/sync semantics | **Excluded from all beds.** Shared/multi-owner behaviour logged as a future consideration, not a pilot case. |
| Live Documents tree fully hydrated (no natural placeholders) | Coverage nuance | RB-10 creates a placeholder deliberately; sign-off wording must not overclaim placeholder coverage. |
| Two-bed design (main un-synced + small OneDrive secondary) | Reviewed against the environment change | **Reaffirmed unchanged** — isolation for the bulk of cases, real-sync validation only where OneDrive behaviour is the thing under test (RB-08, RB-10). |

---

## 9. Running the agent against the bed *(updated in v2.0 — checkpoints woven in)*

1. **Build the bed** (§3–§6) and freeze the in-scope set (§8.4).
2. **CP1 manifest:** export `CP1_manifest.csv` per §8.3.
3. **Dry-run preview (zero risk):** point `starting_folder` at the bed in `agent_loop.py` and run it — it *proposes only, never executes*:
   ```powershell
   Set-Location "C:\Dev\onedrive-agent"
   # edit starting_folder = r"C:\OneDrive-Agent_TestBed" in agent_loop.py
   python agent_loop.py
   ```
   Check proposals against the §7 answer key, **and reconcile the agent's duplicate groups against the CP1 manifest** (§8.4). Zero gating discrepancies required to proceed.
4. **Optional narrative audit:** run the Claude Cowork report against the bed (advisory only — §8.1).
5. **CP2 manifest:** export `CP2_manifest.csv`; compare to CP1. Must be identical in-scope (read-only proof). Any difference = halt, RAID, root-cause, rebuild, restart from CP1.
6. **Live run with approval gate:** update `starting_folder` in `test_phase5_live.py` to the same path, then:
   ```powershell
   python test_phase5_live.py
   ```
   Review the printed pre-run snapshot and proposal list, then approve/reject per the UAT cases (§5.4 of `TEST_STRATEGY.md`), including the deliberate RB-07 rejection.
7. **CP3 manifest:** export `CP3_manifest.csv`; confirm it equals CP1 minus exactly the approved deletions (§8.4). Pass = pilot evidence complete for this bed.
8. **Rebuild between runs:** destructive runs consume the bed. Re-run Sections 3–6 to rebuild it (and restart the checkpoint sequence from CP1). Consider scripting Sections 3–6 into a `build_testbed.ps1` for one-command setup (recommended future task).

---

## 10. Handover checklist *(updated in v2.0)*

A reviewer with only the repo can prove the concept by:
- [ ] Cloning the repo; confirming the full automated suite green (`test_phase2.py`, `test_phase3_4_45.py`, `test_phase8_pre_pilot.py`).
- [ ] Following §3–§6 to build `C:\OneDrive-Agent_TestBed\`.
- [ ] Exporting the CP1 manifest (§8.3).
- [ ] Running §9 step 3 (dry-run) and checking output against the §7 answer key **and** the CP1 manifest (§8.4).
- [ ] Exporting/verifying CP2 (read-only proof).
- [ ] Running §9 step 6 (live) and walking the UAT cases, including RB-13 (resume safety).
- [ ] Exporting/verifying CP3 (change control).
- [ ] Confirming the pre-run snapshot precondition (RB-09) and recovery (RB-08).

---

## 11. Business analysis & PM contributions (Nadeem) *(extended in v2.0)*

Recorded for portfolio visibility — the analytical direction on this artifact came from Nadeem in his BA/PM capacity. Specifics, so the contribution is verifiable rather than generic:

| # | Contribution | BA/PM discipline demonstrated |
|---|---|---|
| 1 | Enforced the standing rule to re-check `BACKLOG.md` and `RAID_LOG.md` against the live repo *before* starting Phase 8, rather than trusting a prior-session summary — which surfaced the forgotten open item #1. | Governance / configuration control; challenging unverified "done" claims. |
| 2 | Identified that certain remediated issues recur, and asked whether a dedicated regression pack was needed — directly driving the **fixture-integrity guard** (RAID I5 class) and the split between code-catchable vs process-only recurrences. | Root-cause analysis; systemic (not point) controls; test strategy. |
| 3 | Specified the test-bed location (`C:\` root) and required a **handover-grade, reproducible** Test Bed & Test Cases artifact with explicit red- and green-line scenarios anyone could execute. | Requirements definition; reproducibility; UAT test design; knowledge transfer. |
| 4 | Required that BA/PM contributions be recorded and made visible across the handoff, README, and documents for an interviewer/manager to see. | Document control; stakeholder-facing traceability. |
| 5 | **(v2.0)** Specified an independent audit-control framework for the pilot — baseline scans before/after detection and after action, by more than one tool, with reports verified against each other before any UAT folder proceeds — which became the CP1/CP2/CP3 regime in §8. Also raised the execution-vs-governance separation (run scans elsewhere; bring artefact reports back for decisions). | Assurance design; segregation of duties; independent verification; audit-trail thinking. |
| 6 | **(v2.0)** Surfaced the changed OneDrive environment (fully-hydrated Documents; three sync-broken folders; one shared folder) *before* the pilot ran, and required a strategy review to avoid rework — leading to the §8.5 exclusions and the deliberate reaffirmation of the two-bed design. | Environment/configuration management; proactive risk surfacing; avoiding rework. |
| 7 | **(v2.0)** Ratified the reconciliation edge-treatments explicitly (RB-02 extension-differing duplicates in scope; zero-byte files logged-not-gating; RB-10 retained) rather than leaving them as silent defaults, and commissioned the canonical `GLOSSARY.md`. | Decision governance; explicit acceptance criteria; documentation standards. |

---

## 12. Document control

| Field | Value |
|---|---|
| Version | v2.0 |
| Companion | `TEST_STRATEGY.md` (bidirectional reference); `GLOSSARY.md` (acronym register) |
| Related | Backlog #6 / Phase 8; RAID R6, I5; gaps G1/G2/G3; handoff v8.0 (audit regime standing rule) |
| Author of build recipe | Claude (drafted), under Nadeem's BA/PM direction (see §11) |
| Next review | On Phase 8 completion, or if `tools.py` detection logic changes |

**Change history**

| Version | Date | Change |
|---|---|---|
| v1.0 | 2026-07-05 | Initial: two-bed design, GB-01…GB-06, RB-01…RB-13, answer key, handover checklist |
| v2.0 | 2026-07-09 05:16 | Added §8 pilot audit-control regime (CP1/CP2/CP3, tooling roles, signed-off Reconciliation & Materiality Rule v1.0, ratified edge treatments, environment exclusions); run sequence and handover checklist updated to include checkpoints; GB/RB prefixes defined; glossary pointer added; BA/PM contributions extended (rows 5–7). Test cases and answer key unchanged. |
