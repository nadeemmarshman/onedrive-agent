r"""
Pre-commit guard: block any commit whose ADDED lines contain real personal
data from the scanned OneDrive folders.

Why this exists
---------------
RAID I27 was a privacy breach: real personal file paths were committed to
this then-public repo. The remediation worked, but during it the *same
mistake recurred three times* -- each time while writing about the breach:

  1. The first draft of RAID I27 quoted real filenames as examples of why
     exact-phrase redaction had failed.
  2. The sanitiser's own docstring did the same.
  3. The first draft of Backlog #18 quoted the real folder names the audit
     had just found.

Each was caught only because a scan happened to be run by hand before
committing. Three recurrences of one pattern is not a discipline problem
to try harder at -- it is a missing control. Writing about sensitive data
is exactly when you quote it, so the check has to be automatic and has to
sit at the commit boundary.

What it checks
--------------
Two independent layers, deliberately not both derived from the same source
(the original I27 verification failed precisely because it checked the repo
against the same token list used to redact it, so anything unmapped was
invisible):

  Layer 1 -- known tokens, from the local `sanitize_mapping.json`. Catches
            the specific real names for this dataset. Absent on a fresh
            clone, in which case this layer is skipped with a warning.

  Layer 2 -- structural patterns, derived from shape rather than from any
            list: Windows absolute paths under a user profile, deep
            backslash path chains ending in a document extension, and
            long digit runs that look like an identity or reference
            number. This layer catches terms nobody thought to map.

Known limitations -- read these before trusting it
--------------------------------------------------
An independent audit (Cowork, 2026-08-02) confirmed the design is sound
but identified real gaps. They are listed here rather than in a ticket,
because a control whose limits are undocumented invites misplaced
confidence:

1. **It only sees staged additions.** It cannot find anything already
   committed. It is a gate on new content, not an audit of existing
   content. Two live findings in this repo were invisible to it for
   exactly this reason.

2. **Blocking a commit does not undo `git add`.** By the time this runs,
   the staged content already exists as a blob in `.git/objects`. Every
   leak this guard "caught" still left a recoverable blob behind --
   confirmed: three such blobs, including a valid-format ID number and a
   real employment-dispute path, survived two history rewrites and were
   only found via `git fsck --unreachable --dangling`. If this guard
   blocks a commit, also run:
       git reflog expire --expire=now --expire-unreachable=now --all
       git gc --prune=now --aggressive
   Never test this guard by staging real sensitive data -- use an
   obviously-synthetic value, or a scratch repository.

3. **`core.hooksPath` is per-clone and manual.** Git does not carry hooks
   in the repository, so a fresh clone is unprotected until someone runs
   `git config core.hooksPath .githooks`. See `TODO.md`.

4. **The token layer needs the gitignored mapping to be present.** On a
   clone without it, only the structural layer runs -- weaker, though
   still the layer that catches unmapped terms.

5. **Structural detection has no signature for everything.** A bare name
   in ordinary prose, with no path or number attached, has no shape to
   match and will not be caught by either layer.

Usage
-----
    python check_staged_for_personal_data.py

Exit codes: 0 = clean, 1 = findings (commit blocked), 2 = usage error.

Install as a hook (once, per clone):
    git config core.hooksPath .githooks

Deliberate override, when a match is genuinely a false positive:
    ALLOW_PERSONAL_DATA=1 git commit ...
This is logged loudly rather than silent, so an override is a visible
decision rather than a habit.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

MAPPING_FILE = Path("sanitize_mapping.json")

# Layer 2: shape-based, independent of any curated list.
STRUCTURAL = [
    (re.compile(r"[A-Za-z]:\\Users\\[A-Za-z0-9._-]+\\", re.IGNORECASE),
     "absolute path under a user profile"),
    # Segments must allow spaces -- real folder names have them ("00-My
    # Folders"). An earlier version of this pattern excluded whitespace and
    # therefore silently missed exactly the case this layer exists to catch:
    # an unmapped, space-containing path. Found by the guard's own test.
    (re.compile(r"(?:[A-Za-z0-9][A-Za-z0-9 ._&'()+-]{1,40}\\){2,}"
                r"[A-Za-z0-9][A-Za-z0-9 ._&'()+-]{1,40}"
                r"\.(?:pdf|docx?|xlsx?|pptx?|jpe?g|png|heic|mp4|m4a|wav|zip|eml|collection)\b",
                re.IGNORECASE),
     "deep path chain ending in a document filename"),
    (re.compile(r"(?<!\d)\d{11,13}(?!\d)"),
     "long digit run (possible identity/reference number)"),
]

# Lines that are legitimately allowed to contain path-shaped text: the
# placeholders the sanitiser produces, and this file's own patterns.
# Underscores matter: the sanitiser emits both kebab-case placeholders
# (<identity-documents>) and SCREAMING_SNAKE roots (<DOCS_ROOT>,
# <ONEDRIVE_ROOT>, <DR_BACKUP_ROOT>). Omitting `_` made the latter look
# like real content and would have produced false positives on correctly
# sanitised files -- found by test_matches_generated_placeholders.
PLACEHOLDER = re.compile(r"<[a-z0-9_-]+>", re.IGNORECASE)
# Files exempt from the structural layer because their job is to *contain*
# path-shaped strings: the guard itself, the sanitiser, and the guard's
# tests (whose fixtures are deliberately synthetic -- "SomeUser",
# "Some Unmapped Folder", an invented 13-digit number).
#
# An exemption list is a hole, so it is kept to three files and every entry
# is reviewable by eye. Layer 1 (known real tokens) still applies to all of
# them, so a real name pasted into any of these is still caught.
SELF = {
    "check_staged_for_personal_data.py",
    "sanitize_repo_artifacts.py",
    "test_personal_data_guard.py",
}


def staged_additions() -> list[tuple[str, int, str]]:
    """Return (file, line_no, text) for every added line in the index."""
    diff = subprocess.run(
        ["git", "diff", "--cached", "--unified=0", "--no-color"],
        capture_output=True, text=True, errors="replace",
    ).stdout
    out: list[tuple[str, int, str]] = []
    current = ""
    lineno = 0
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:]
        elif line.startswith("@@"):
            m = re.search(r"\+(\d+)", line)
            lineno = int(m.group(1)) if m else 0
        elif line.startswith("+") and not line.startswith("+++"):
            out.append((current, lineno, line[1:]))
            lineno += 1
    return out


def load_tokens() -> list[str]:
    if not MAPPING_FILE.exists():
        return []
    raw = json.loads(MAPPING_FILE.read_text(encoding="utf-8"))
    toks: list[str] = []
    for section, items in raw.items():
        if section.startswith("_"):
            continue
        toks.extend(items.keys())
    # Longest first so the most specific match is reported.
    return sorted(toks, key=len, reverse=True)


def main() -> int:
    additions = staged_additions()
    if not additions:
        return 0

    tokens = load_tokens()
    findings: list[str] = []

    for path, lineno, text in additions:
        base = Path(path).name
        # Layer 1
        for tok in tokens:
            if tok.lower() in text.lower():
                findings.append(f"  {path}:{lineno}  known token: {tok!r}")
                break
        # Layer 2
        if base not in SELF:
            for pattern, why in STRUCTURAL:
                m = pattern.search(text)
                if m and not PLACEHOLDER.search(m.group(0)):
                    findings.append(f"  {path}:{lineno}  {why}: {m.group(0)[:70]!r}")
                    break

    if not findings:
        return 0

    if os.environ.get("ALLOW_PERSONAL_DATA") == "1":
        print("=" * 72, file=sys.stderr)
        print("OVERRIDE: personal-data check bypassed via ALLOW_PERSONAL_DATA=1",
              file=sys.stderr)
        print(f"{len(findings)} finding(s) were suppressed:", file=sys.stderr)
        for f in findings[:20]:
            print(f, file=sys.stderr)
        print("=" * 72, file=sys.stderr)
        return 0

    print("=" * 72, file=sys.stderr)
    print("COMMIT BLOCKED -- possible personal data in staged changes (RAID I27)",
          file=sys.stderr)
    print("=" * 72, file=sys.stderr)
    for f in findings[:40]:
        print(f, file=sys.stderr)
    if len(findings) > 40:
        print(f"  ... and {len(findings) - 40} more", file=sys.stderr)
    print("", file=sys.stderr)
    print("This most often fires when writing *about* the data -- a report, a", file=sys.stderr)
    print("RAID entry, a commit message, a docstring. Describe the category", file=sys.stderr)
    print("instead of quoting the real name.", file=sys.stderr)
    print("", file=sys.stderr)
    if not tokens:
        print("NOTE: sanitize_mapping.json not found, so only structural checks ran.",
              file=sys.stderr)
    print("If a finding is genuinely a false positive:", file=sys.stderr)
    print("    ALLOW_PERSONAL_DATA=1 git commit ...", file=sys.stderr)
    print("=" * 72, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
