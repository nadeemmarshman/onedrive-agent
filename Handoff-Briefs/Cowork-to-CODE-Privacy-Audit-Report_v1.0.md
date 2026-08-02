# Independent Privacy Audit Report (Cowork → CODE)

**From:** Claude Cowork, independent second check
**To:** Claude Code session, `C:\Dev\onedrive-agent`, and {{owner}}
**Date:** 2026-08-02
**Version:** v1.0
**Responds to:** `Handoff-Briefs/CODE-to-Cowork-Privacy-Audit-Handoff_v1.0.md`

**Handling note, consistent with the brief that requested this audit:**
findings below are described by category and location, not quoted
verbatim. No raw personal data is reproduced in this document. This
document itself was checked against `check_staged_for_personal_data.py`
before being left for review (see "Self-check" at the end).

---

## Method (designed independently, not derived from the prior remediation's approach)

1. Local git ground truth: branches, tags, remotes, reflog — and, the
   step ordinary `git log`/`git grep` skips, `git fsck --unreachable
   --dangling` to surface objects no longer reachable from any ref.
2. A custom scanner over **every reachable blob across all history**,
   regardless of file extension (the prior sweep's own documented gap was
   scoping by extension and missing `.py`), flagging structural shapes
   rather than a curated term list: Windows user-profile paths, deep
   backslash path-chains ending in a document extension, long digit runs
   (11–13 digits — the shape of an ID/reference number).
3. The same structural check run by hand against every object `fsck`
   flagged as dangling (unreachable objects aren't visited by the
   reachable-history scanner in step 2 by design).
4. Read the actual pre-commit hook, its test file, `.gitignore`, and the
   drafted GitHub Support request — assessed as controls, not just
   confirmed present.
5. Independently re-verified one existing claim (the stash) rather than
   trusting the log's word for it.
6. Checked this Cowork session's own artifacts for the same failure mode.

No internet access to the GitHub remote was used or available (repo is
private; no credentials) — remote-side conclusions below are reasoned
from local evidence, not observed directly.

---

## Findings

### 1. Live, currently committed, on `origin` right now — real
**Severity: highest.**
`test_personal_data_guard.py` (the guard's own test file) contains a
13-digit value in the shape of a South African ID number, used as a test
fixture. A dangling object (finding #3) independently contains what
appears to be the same value in a plain-prose sentence referencing "the
form" — consistent with this being a real number reused as a "realistic"
fixture, not a synthetic one. This is not history; it is in the current
tree.

### 2. Live, currently committed — one incomplete redaction
`COWORK_DUP_SCAN_FINDINGS_DOCUMENTS_v1.0.md` is otherwise carefully
placeholder-ized, but one results-table row still contains a real, full
file path (an internal audit-report filename). Low sensitivity alone, but
shows the redaction pass on this file wasn't complete.

### 3. Real personal data recoverable from local `.git/objects`
`git fsck --unreachable --dangling` found 8 objects still present locally
despite two history rewrites — never garbage-collected. Two are
substantive: one blob quotes a real, specific sensitive file path as an
"Example:" (an employment-dispute/disciplinary-hearing file — a leftover
of one of the three "documenting the breach re-disclosed it" incidents
your own RAID log already describes); another contains the apparent real
ID number from finding #1 in prose form. None of this is visible via
`git log -p` or ordinary grep — only via `fsck` + `cat-file`.

### 4. GitHub-side exposure window is real and currently open
The already-drafted, unsent GitHub Support purge request's reasoning is
correct and now evidenced: force-push rewrites refs, not objects; GitHub
can still serve old commits by SHA until its own GC runs. Finding #3
confirms there is genuinely sensitive content in what was rewritten away.
`TODO.md` sequences this request *after* unrelated cleanup work — an open
exposure window with no technical urgency attached to closing it.

### 5. Pre-commit guard is sound but not portable, and can't see history
`.githooks/pre-commit` + `check_staged_for_personal_data.py` are
well-designed (two independent layers, structural not just token-based).
Confirmed: the digit-run pattern would have caught something shaped like
finding #1 or #3 if active when that content was staged. But
`core.hooksPath` is per-clone, manual, not carried by git — a fresh clone
is unprotected until someone remembers `TODO.md`. It also only inspects
**staged additions**, so it structurally cannot find #1 or #2 above,
which are already committed.

### 6. `.gitignore` exclusions — verified watertight
Checked directly (`git ls-files`, `git check-ignore`), not just read:
`sanitize_mapping.json`, `robocopy_backup_log.txt`, `_audit_*.py`,
`_raw_local_only/` are all correctly untracked, never accidentally staged
or committed anywhere in history.

### 7. Stash — independently re-verified clean
Not taken on trust: diffed it myself. README wording only, nothing
sensitive.

### 8. Found in Cowork's own prior work, not this repo
A draft document in this Cowork session's own sandbox (never part of
this repo) had quoted the same disciplinary-hearing filename verbatim,
twice, while documenting an unrelated scoping exercise earlier in this
session. Same failure mode, different location — self-caught during this
audit, redacted there. Not a finding *about* this repo, but relevant
context: the pattern reproduces easily, including in the auditor's own
output, which is exactly why this document was self-checked before being
left here (see below).

---

## What I could not determine

- Whether the sensitive dangling objects are actually still fetchable
  from GitHub's servers — no remote access available to check.
- Full completeness: I ran structural/shape-based detection only,
  deliberately not a curated term list (that would reproduce the exact
  blind-spot class this audit was commissioned to avoid). Personal data
  with no structural signature — e.g. a bare name in ordinary prose, no
  path or number attached — would not be caught by this method.
- Whether the finding-#1 value is *definitely* real rather than
  coincidentally realistic-looking — inferred from corroboration with
  finding #3, not confirmed against source data.

---

## Recommendation

**Do not republish yet — confidence: high**, independent of what the
prior remediation already believed. Suggested before reconsidering:

1. Replace the real-shaped fixture value in `test_personal_data_guard.py`
   with an obviously-synthetic one.
2. Fix the one missed path in
   `COWORK_DUP_SCAN_FINDINGS_DOCUMENTS_v1.0.md`.
3. Locally: `git reflog expire --expire=now --all && git gc --prune=now
   --aggressive` (or equivalent) — the rewrite alone did not clear the
   dangling objects; they are still fully intact right now.
4. Send the already-drafted GitHub Support purge request — don't wait for
   the unrelated cleanup queue ahead of it in `TODO.md`.
5. Re-scan the *result* of 1–4 (mine or a fresh method) before deciding.

---

## Weakness noted in the brief itself

The brief didn't name `git fsck`/dangling-object inspection as a category
to consider, even though "what does a repository actually consist of"
was the framing — a strong hint toward it, but not explicit. It was the
single highest-value technique used here. Worth folding into this
project's own procedure for next time, consistent with `LESSONS_LEARNED.md`
lesson 8 (a check's scope has to be derived independently, not assumed).

---

## Self-check

This document was staged (`git add`) and run through the repo's own
`check_staged_for_personal_data.py` before being left here, rather than
assumed clean by intent alone. Left **unstaged and uncommitted** after
the check — same handling as the prior Cowork→CODE handoff, so CODE or
{{owner}} reviews before anything is committed.
