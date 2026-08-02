r"""
Triage execution for the 58 files staged in
_DocFolderBackup_Unique_Files_ToReview\ (see DOCFOLDERBACKUP_UNIQUE_FILES_REVIEW.md
for the category-level analysis this refines into per-file decisions).

Three outcomes per file:
- KEEP: relocated into an existing, matching folder in the live
  "00-My Folders" tree. Only used where a real matching folder already
  exists -- no new folders invented to force a "confident" placement.
- DISCARD: relocated into a new review-only folder
  (_DocFolderBackup_Discard_ToReview\), not deleted -- final delete is
  Nadeem's call, same pattern as every other live-run phase. Reasons:
  system noise (desktop.ini), broken OneDrive-item pointer stubs
  (.collection files, confirmed by reading their content -- they
  reference an item ID, not an embedded image), someone else's CV,
  a downloaded resume template, a software installer, and a copy-pasted
  PowerShell troubleshooting log (new 2.txt -- confirmed by reading it).
- LEAVE: left in the original staging folder untouched. Two files
  (brochure.pdf, a <care-facility> voice note) have unclear/personal content
  that genuinely needs Nadeem's own judgment, not a guessed placement.

Relative paths (dict keys) are exactly as they appear in
DOCFOLDERBACKUP_DELTA.json's unique_file_list, relative to
_DocFolderBackup_Unique_Files_ToReview\.
"""

import json
import shutil
from pathlib import Path

STAGING_ROOT = Path(r"<DOCS_ROOT>\_DocFolderBackup_Unique_Files_ToReview")
LIVE_ROOT = Path(r"<DOCS_ROOT>\00-My Folders")
DISCARD_ROOT = Path(r"<DOCS_ROOT>\_DocFolderBackup_Discard_ToReview")
DELTA_JSON = r"C:\Dev\onedrive-agent\DOCFOLDERBACKUP_DELTA.json"
BACKUP_DOCS_PREFIX = r"<DOCS_ROOT>\DocFolderBackup\Documents\\"

# relative_path (from staging root) -> ("KEEP", dest folder under 00-My Folders)
#                                    -> ("DISCARD", reason)
#                                    -> ("LEAVE", reason)
# The real decision map is NOT published. It was a per-file dict of 58
# real paths -> (action, destination) covering identity documents,
# employment-dispute records, licence records, <<payslip-record>-records> and third-party
# names. Token-scrubbing cannot de-identify it: the per-file structure
# IS the disclosure, so only removal works. The unredacted map is
# retained locally, outside version control (see .gitignore).
#
# Illustrative shape only, so the method stays legible:
#
#   DECISIONS = {
#       r"<area>\<subfolder>\desktop.ini": ("DISCARD", "folder-view marker, no content"),
#       r"<area>\<subfolder>\<file>.collection": ("DISCARD", "verified: OneDrive item-ID pointer stub"),
#       r"<area>\<identity-docs>\<file>.jpg": ("KEEP", r"<identity-docs>"),
#       r"<area>\<career>\<file>.docx": ("KEEP", r"<career>\<subfolder>"),
#       r"<area>\<file>.pdf": ("LEAVE", "unclear content -- needs a human decision"),
#   }
#
# Actual outcome across the real 58: 41 KEEP, 15 DISCARD, 2 LEAVE
# (later revised to 40/15/2 plus 1 reclassified KEEP).



def _load_local_decisions() -> dict[str, tuple[str, str]]:
    """Load the per-file decision map from a local, unpublished file.

    Kept out of the repository deliberately (RAID I27): the map is 58 real
    personal paths, and its per-file structure cannot be de-identified
    without destroying it. This script therefore no longer runs from a
    clean checkout -- intended, since the triage already executed and the
    files it referenced have since been moved or deleted. Its remaining
    value is as a record of method, not as something to re-run.
    """
    import json
    local = Path("_raw_local_only/docfolderbackup_decisions.json")
    if not local.exists():
        raise SystemExit(
            "Decision map not available: it is deliberately unpublished (RAID I27). "
            f"Expected local copy at {local}."
        )
    raw = json.loads(local.read_text(encoding="utf-8"))
    return {k: tuple(v) for k, v in raw.items()}


DECISIONS: dict[str, tuple[str, str]] = _load_local_decisions()


def _verify_complete() -> None:
    data = json.load(open(DELTA_JSON, encoding="utf-8"))
    backup_docs_root = Path(r"<DOCS_ROOT>\DocFolderBackup\Documents")
    expected = set()
    for entry in data["unique_file_list"]:
        rel = Path(entry["path"]).relative_to(backup_docs_root)
        expected.add(str(rel))
    actual = set(DECISIONS.keys())
    missing = expected - actual
    extra = actual - expected
    if missing or extra:
        raise AssertionError(f"Decision map incomplete. Missing: {missing}. Extra: {extra}")
    assert len(actual) == 58, f"expected 58 decisions, got {len(actual)}"


def run() -> None:
    _verify_complete()
    DISCARD_ROOT.mkdir(exist_ok=True)

    results = {"KEEP": [], "DISCARD": [], "LEAVE": [], "SKIPPED_ALREADY_DONE": []}
    for rel_path, (action, detail) in DECISIONS.items():
        src = STAGING_ROOT / rel_path
        if action == "LEAVE":
            results["LEAVE"].append((rel_path, detail))
            continue
        if not src.exists():
            # Resumable: a prior run already moved this file.
            results["SKIPPED_ALREADY_DONE"].append(rel_path)
            continue
        if action == "KEEP":
            dest_dir = LIVE_ROOT / detail
        else:
            dest_dir = DISCARD_ROOT / Path(rel_path).parent
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name
        collision = dest.exists()
        if collision:
            # A same-named, different-content file already lives at the
            # destination (confirmed different by DOCFOLDERBACKUP_DELTA.json's
            # own uniqueness check) -- never overwrite; suffix instead and
            # flag for Nadeem to reconcile which version is current.
            dest = dest_dir / f"{src.stem} (from DocFolderBackup){src.suffix}"
            assert not dest.exists(), f"suffixed destination also collides: {dest}"
        shutil.move(str(src), str(dest))
        results[action].append((rel_path, str(dest), collision))

    print(f"Skipped (already moved in a prior run): {len(results['SKIPPED_ALREADY_DONE'])}")
    print(f"KEEP: {len(results['KEEP'])} files relocated into 00-My Folders")
    collisions = [r for r in results["KEEP"] if r[2]]
    print(f"  of which {len(collisions)} had a same-named different-content file "
          f"already there -- suffixed '(from DocFolderBackup)', not overwritten:")
    for rel_path, dest, _ in collisions:
        print(f"    {rel_path} -> {dest}")
    print(f"DISCARD: {len(results['DISCARD'])} files moved to {DISCARD_ROOT}")
    print(f"LEAVE: {len(results['LEAVE'])} files left in staging, still need your input")
    for rel_path, detail in results["LEAVE"]:
        print(f"  LEAVE: {rel_path} -- {detail}")


if __name__ == "__main__":
    run()
