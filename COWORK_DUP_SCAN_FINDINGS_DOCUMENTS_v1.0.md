# Cowork Duplicate Scan Findings — Documents Repo (v1.0)

**Produced by:** Cowork session (Claude), 8 July 2026
**Purpose:** Ground-truth record of the Cowork duplicate/artifact scan of the Documents repository, written to this repo so Claude Code can verify it against what is committed/documented here (e.g. `DOCUMENTS_DEDUP_PROPOSAL.json`).
**Companion file:** `COWORK_DUP_SCAN_GROUPS_v1.0.json` — full machine-readable duplicate groups (exact copy of the working list saved to the repo owner's OneDrive).

---

## 1. Scope

| Item | Value |
|---|---|
| Roots scanned | `<DOCS_ROOT>\1. My Folders` and `...\<family-member-1>` |
| Files | 1,689 (1,651 in My Folders, 38 in <family-member-1>) |
| Folders | 263 |
| Logical size | 3.34 GB |
| Scan date | 2026-07-08 |

Not scanned: anything outside those two roots (Pictures, Camera Roll, other `1. Documents` subfolders such as WindowsPowerShell).

## 2. Method

1. Full inventory (path, byte size, mtime) of all 1,689 files.
2. Size-grouping: 578 files shared a byte size with at least one other file.
3. 340 of these candidates were OneDrive cloud-only (~480 MB); they were hydrated (downloaded) with the owner's approval to allow content verification.
4. Partial hash (first 64 KB, MD5) to prune, then **full-file MD5** on all 552 surviving candidates (~900 MB read).
5. Duplicate = byte-identical full-file MD5. No name/size-only matches are reported as duplicates.

## 3. Headline results

| Metric | Value |
|---|---|
| Verified duplicate groups | **242** |
| Redundant copies (files deletable) | **308** |
| Reclaimable space | **581.7 MB** (~17% of repo) |

## 4. Largest findings (top 5 by waste)

1. **468.5 MB** — `<hearing-recording>.wav` (234.2 MB) exists **3×** under `2 Career Documents/4 Employment Companies/<employerA>/<employerA>_Termination/`, caused by a full nested self-copy: `<employerA>_Termination/<employerA>_Termination/` is a complete duplicate subtree of its parent (~500 MB total incl. ~40 duplicated documents).
2. **13.2 MB** — `Statement_{{owner}}.pdf` ×3 (incl. one `(2)` copy) in <employerA> Suspension folders.
3. **9.8 MB** — `D_<suspension-notice> 1stNov2019.pdf` ×4.
4. **8.8 MB** — `F_<union>Agreeement9thDec2019.pdf` ×4.
5. **6.5 MB** — `C_WarningAppeal 4thOct2019.pdf` ×4.

Full list of all 242 groups with suggested keeper vs delete paths: see companion JSON (fields: `size`, `waste`, `n`, `keeper`, `dups`; paths relative to `OneDrive\1. Documents`).

## 5. Duplication patterns identified

- Folder-pasted-into-itself (`<employerA>_Termination/<employerA>_Termination`) — single largest cause.
- Same document filed under two life areas (e.g. `knockout-target.pdf` in Shooting/Targets and <employerA>_Work_Files/Mine; Samsung warranty in <household-records> and <employerA>_Work_Files/Mine). The `<employerA>_Work_Files/Mine` folder is a shadow copy of personal filing.
- Browser re-download numbering: `BSTMA0<employee-ref> (1)..(7).PDF`, `Pgsql-with-Python (1)/(2).py`, etc.
- Copies beside originals: `... (2).pdf`, `<hobby-app>-Backup-2025-08-22 1.hobbyapp` (28 MB), `Ramadan Parcels_Copy.xlsx`.
- Duplicated scan folders: `<employerA> <suspension-documents>/2020-01-14_` vs `2020-01-14_170945` (same 4 JPGs).
- 101 files carry copy-pattern names (`(n)`, `_Copy`, `(x2)`).

## 6. Junk / artifacts found

- 2 saved-webpage `..._edX_files` folders (~50 web files incl. `.js.download`), one a duplicate of the other.
- 3 Windows `.lnk` shortcuts.
- Self-labelled junk folders: `Trash`, `ArchiveToDelete`, `Other Unsorted`, `Random Artifacts`.
- Cryptic unsearchable names: `9PJEVhUzhbHfThO.728KOw.PDF`, `MFSpougIL2iA5FoGSMeYQg.PDF`, `Book1 (Recovered).xlsx`, `Document.docx`, `scan17247666.jpg` (+3 siblings).
- Zero-byte files: none.

## 7. Deliverables produced by the Cowork session

| Artefact | Location |
|---|---|
| Full audit report (29+ pp, incl. proposed folder schema, naming conventions, Appendix A with all 242 groups) | `<ONEDRIVE_ROOT>\<DOCS>\<area>\<admin>\<audit-report>.docx` |
| Machine-readable duplicate groups | `<ONEDRIVE_ROOT>\<DOCS>\<area>\<admin>\<audit-groups>.json` (identical content to the companion JSON in this repo) |
| New folder created | `1. My Folders\00-Admin\` (approved via gate) |

## 8. Caveats for reconciliation

- Waste figure uses MB = 1,048,576 bytes; group "waste" = size × (copies − 1).
- Keeper selection is heuristic (shallowest path, then shortest); reconciliation should compare **group membership**, not keeper choice.
- Files created after 2026-07-08 are not reflected.
- Hydration means previously cloud-only candidates now occupy local disk; a "Free up space" pass was recommended to the owner.
- No files were deleted, moved or renamed by the scan itself; the only writes were the `00-Admin` artefacts above and this handoff.
