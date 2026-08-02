r"""
De-identify the live-run scan artefacts before they sit in a public repo.

Background
----------
This repo is a public portfolio piece. The live-run phases scanned real
personal folders, and several committed artefacts carried the full path
of every file scanned -- disclosing, by folder and filename alone, an
employment dispute, firearm licence records, identity and estate
documents, medical scheme membership, an employee number, and
third-party names. File *contents* were never committed; the paths alone
were enough.

Design notes (both learned the hard way, first attempt)
-------------------------------------------------------
1. **Token regexes, not exact phrases.** A first version enumerated exact
   full strings such as "<employer>_Termination". Real data does not
   cooperate: the same entity appeared in at least four shapes -- joined
   to other words, abbreviated, camel-cased, and prefixed with a payroll
   number -- so enumeration silently missed most instances. Matching on
   the *token* catches every variant regardless of what surrounds it.
   (Deliberately not illustrated with the real filenames here: quoting
   them would re-disclose exactly what this script exists to remove --
   a mistake actually made in the first draft of this docstring and of
   RAID I27, and caught by the pre-commit scan.)

2. **Structure-agnostic JSON stripping.** The first version stripped keys
   named `groups`/`members`. One artefact was a top-level *list* whose
   groups used `keeper`/`dups`, so nothing was stripped and the file
   actually grew. This version drops any list of dicts that looks like
   file records, and additionally redacts any leftover path-shaped
   string, so an unfamiliar schema fails safe rather than silently
   leaking.

Two treatments, because artefacts differ in value
-------------------------------------------------
- Raw JSON scan dumps: value is the aggregate ("3,084 files scanned, 948
  duplicate groups"). Per-file lists carry all disclosure and no story --
  dropped, replaced by counts.
- Narrative markdown: the specifics *are* the value (keeper-selection
  defect, self-nested folder, collision handling). Deleting text would gut
  the analysis, so sensitive tokens are replaced by stable placeholders.

The mapping is deliberately NOT in this file: a committed real-name ->
placeholder map would re-disclose exactly what was removed. It lives in
`sanitize_mapping.json`, which is gitignored. Method is committed; data
is not.

Idempotent -- placeholders contain no mapped tokens.
"""

import json
import re
from pathlib import Path

MAPPING_FILE = Path("sanitize_mapping.json")

# A string that looks like a filesystem path or a document filename.
PATH_SHAPED = re.compile(
    r"(?:[A-Za-z]:\\)|(?:\\\\)|(?:/[A-Za-z0-9_ .-]+/)"
    r"|(?:\.(?:pdf|docx?|xlsx?|pptx?|jpe?g|png|heic|mp4|m4a|wav|zip|eml|collection|digital-link)\b)",
    re.IGNORECASE,
)

# Markdown that is really a data dump rather than narrative: keep the
# aggregate section, drop everything from the detail heading onward.
# DOCUMENTS_WORKSTREAM_DEDUP_REPORT.md is 730 lines of which every "###"
# heading is a full path-pair -- scrubbing it inline would leave mangled
# prose and still risk leaking an unmapped token, so it is truncated.
SECTION_TRUNCATE = {
    "DOCUMENTS_WORKSTREAM_DEDUP_REPORT.md": "## Full path-pair detail",
    "DOCFOLDERBACKUP_UNIQUE_FILES_REVIEW.md": "## System noise",
}

TRUNCATION_NOTE = (
    "\n---\n\n"
    "> **Detail removed before publication.** Everything below this point was a\n"
    "> per-file listing of real personal paths (employment dispute, licence,\n"
    "> identity, medical and third-party records). The aggregate findings above\n"
    "> carry the analytical content; the detail carried only disclosure. The\n"
    "> unredacted version is retained locally and is not in this repository.\n"
    "> See `sanitize_repo_artifacts.py` for the rationale and method.\n"
)

MARKDOWN_TARGETS = [
    "DOCUMENTS_WORKSTREAM_DEDUP_REPORT.md",
    "DOCFOLDERBACKUP_UNIQUE_FILES_REVIEW.md",
    "LIVE_RUN_INTERNAL_DUPLICATES.md",
    "LIVE_RUN_DOCFOLDERBACKUP_TRIAGE.md",
    "LIVE_RUN_DOCFOLDERBACKUP_QUARANTINE.md",
    "LIVE_RUN_DOCUMENTS.md",
    "LIVE_RUN_PCBACKUP.md",
    "COWORK_DUP_SCAN_FINDINGS_DOCUMENTS_v1.0.md",
    "Handoff-Briefs/Live-Run-Handoff-Documents_v1.0.md",
    "RAID_LOG.md",
]

JSON_TARGETS = [
    "DOCUMENTS_DEDUP_PROPOSAL.json",
    "DOCFOLDERBACKUP_DELTA.json",
    "COWORK_DUP_SCAN_GROUPS_v1.0.json",
    "PCBACKUP_DELTA.json",
]

# Source files are targets too. This was missed on the first remediation
# pass -- the verification sweep scoped itself to *.json and *.md, so
# triage_docfolderbackup_unique_files.py sat in the public repo with 30
# lines of real paths in its DECISIONS dict, untouched and unnoticed.
# A scan that defines its own scope by file extension misses whatever it
# did not think of. See RAID I27.
#
# Scrubbing DECISIONS turns those keys into placeholders, so that script
# is no longer re-runnable. Intended: it already executed, the files it
# referenced have since moved or been deleted, and its remaining value is
# as a record of how the triage was decided, not as a thing to re-run.
PYTHON_TARGETS = [
    "triage_docfolderbackup_unique_files.py",
    "analyze_pcbackup_delta.py",
    "relocate_docfolderbackup_unique_files.py",
    "quarantine_docfolderbackup_wholesale.py",
    "quarantine_pcbackup_wholesale.py",
    "scan_documents_dedup.py",
    "analyze_docfolderbackup_delta.py",
    "generate_workstream_dedup_report.py",
    "verify_documents_backup.py",
]

FILE_RECORD_HINTS = {"path", "members", "keeper", "dups", "size_bytes", "size", "matches_live"}


def load_token_patterns() -> list[tuple[re.Pattern, str]]:
    """Build longest-first token regexes from the gitignored mapping."""
    raw = json.loads(MAPPING_FILE.read_text(encoding="utf-8"))
    pairs: list[tuple[str, str]] = []
    for section, items in raw.items():
        if section.startswith("_"):
            continue
        pairs.extend(items.items())
    pairs.sort(key=lambda kv: len(kv[0]), reverse=True)

    compiled = []
    for token, placeholder in pairs:
        # Tokens are matched case-insensitively and not required to sit on
        # word boundaries, because real filenames run them together
        # (e.g. token joined to other words, or prefixed by a payroll number).
        compiled.append((re.compile(re.escape(token), re.IGNORECASE), placeholder))
    return compiled


def scrub(text: str, patterns: list[tuple[re.Pattern, str]]) -> tuple[str, int]:
    total = 0
    for pattern, placeholder in patterns:
        text, n = pattern.subn(placeholder, text)
        total += n
    return text, total


def looks_like_file_record(item) -> bool:
    return isinstance(item, dict) and bool(FILE_RECORD_HINTS & set(item.keys()))


def strip_lists(obj):
    """Drop any list of file-record dicts, leaving a count behind.

    Structure-agnostic: keys are not hard-coded, so an unfamiliar schema
    still gets stripped rather than silently passed through.
    """
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if isinstance(v, list) and v and all(looks_like_file_record(i) for i in v):
                out[f"{k}_count"] = len(v)
            elif isinstance(v, list) and v and all(isinstance(i, str) for i in v) and any(
                PATH_SHAPED.search(i) for i in v
            ):
                out[f"{k}_count"] = len(v)
            else:
                out[k] = strip_lists(v)
        return out
    if isinstance(obj, list):
        if obj and all(looks_like_file_record(i) for i in obj):
            return {"entries_removed": len(obj),
                    "note": "per-file entries removed before publication"}
        return [strip_lists(v) for v in obj]
    if isinstance(obj, str) and PATH_SHAPED.search(obj):
        return "<redacted-path>"
    return obj


def main() -> None:
    if not MAPPING_FILE.exists():
        raise SystemExit(f"{MAPPING_FILE} not found (gitignored by design).")
    patterns = load_token_patterns()
    print(f"Loaded {len(patterns)} token patterns.\n")

    print("JSON dumps -- aggregates kept, per-file lists dropped:")
    for name in JSON_TARGETS:
        p = Path(name)
        if not p.exists():
            print(f"  SKIP (absent): {name}")
            continue
        before = len(p.read_text(encoding="utf-8"))
        data = strip_lists(json.loads(p.read_text(encoding="utf-8")))
        text, n = scrub(json.dumps(data, indent=2), patterns)
        p.write_text(text, encoding="utf-8")
        print(f"  {name}: {before:,} -> {len(text):,} bytes ({n} tokens scrubbed)")

    print("\nMarkdown -- token substitution (+ truncation where it is a data dump):")
    for name in MARKDOWN_TARGETS:
        p = Path(name)
        if not p.exists():
            print(f"  SKIP (absent): {name}")
            continue
        text = p.read_text(encoding="utf-8")
        before_lines = text.count("\n")

        marker = SECTION_TRUNCATE.get(name)
        truncated = False
        if marker and marker in text:
            text = text.split(marker, 1)[0].rstrip() + "\n" + TRUNCATION_NOTE
            truncated = True

        text, n = scrub(text, patterns)
        p.write_text(text, encoding="utf-8")
        suffix = (f", truncated {before_lines}->{text.count(chr(10))} lines"
                  if truncated else "")
        print(f"  {name}: {n} tokens scrubbed{suffix}")

    print("\nPython sources -- token substitution:")
    for name in PYTHON_TARGETS:
        p = Path(name)
        if not p.exists():
            print(f"  SKIP (absent): {name}")
            continue
        text, n = scrub(p.read_text(encoding="utf-8"), patterns)
        if n:
            p.write_text(text, encoding="utf-8")
        print(f"  {name}: {n} tokens scrubbed")


if __name__ == "__main__":
    main()
