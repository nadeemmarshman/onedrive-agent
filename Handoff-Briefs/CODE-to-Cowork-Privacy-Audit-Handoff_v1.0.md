# Handoff Brief — Independent Privacy Audit (CODE → Cowork)

**From:** Claude Code session, `C:\Dev\onedrive-agent`
**To:** Claude Cowork, as an independent second check
**Date:** 2026-08-02
**Version:** v1.0

---

## Why you are being asked, and why this brief is deliberately thin

A privacy incident occurred in this repository. It was remediated by the
Claude Code session that caused it. That session then verified its own
remediation and declared it clean — **and was wrong.** A later sweep found
the verification had been structurally incapable of detecting part of what
it was checking for, and further personal data was still present.

That is the reason you are here. If this brief told you what was checked,
which terms were used, which files were inspected, or which methods were
applied, you would very likely re-run a variant of the same checks and
inherit the same blind spots. The whole value of this exercise is that you
approach it *without* that inheritance.

So this brief gives you **the problem and the objective, and deliberately
withholds the method.** Please design your own approach. If your instinct
differs from what you imagine was already done, follow your instinct — that
divergence is the point.

Please also treat every claim below as a claim, not as verified fact. The
prior session's assurances are exactly what is in question.

---

## Background: what happened

This repository is a personal portfolio project. It contains an agent that
finds and removes duplicate files. In its later phases it was pointed at
**real personal folders** rather than the synthetic test data it was built
against.

Artefacts produced by those runs — scan outputs, analysis reports, decision
maps, working scripts, project governance documents — were committed to
this repository **while it was public on GitHub**.

Those artefacts contained real personal information belonging to the repo
owner and, in places, to third parties. The categories involved include
financial records, identity and legal documents, medical scheme
information, employment history including a workplace dispute, licensing
records, and the names of family members and other individuals.

An important characteristic of this incident: **the file contents were
never committed.** The exposure came from file *paths*, folder names and
filenames alone, which were descriptive enough to disclose all of the
above. Whatever approach you take, be aware that the sensitive material in
this repo has generally not looked like a document — it has looked like a
path, a label, an identifier, a dict key, or an example in a sentence.

---

## What has reportedly been done since

Stated so you know what you are auditing. **None of it should be assumed
effective.**

- The repository was set to private.
- The affected artefacts were edited to remove or obscure the personal
  information, with placeholder text substituted in some places.
- Git history was rewritten and force-pushed — twice, because the first
  attempt was found to be incomplete.
- Some files that could not be sanitised were removed from version control
  and now exist only locally, outside the repository.
- An automated pre-commit control was added to block future occurrences.
- The incident was documented in the project's governance artefacts.

A recurring failure mode is worth flagging, because it may still be
present: on at least three occasions, the act of *writing about* the
incident reintroduced the sensitive data into the repository, because
describing what had been removed involved quoting it as an example.

---

## Your objective

**Establish, independently, whether any real personal information remains
anywhere in this repository or its history — and report what you find.**

"Anywhere" is meant broadly. Scope it as you see fit, but the question is
not limited to the obvious files. Consider what a repository actually
consists of, and where information can persist after it appears to have
been deleted.

Secondary questions, if you get that far:

1. **Is the remediation sound, or merely apparently sound?** Placeholders,
   truncation and removal each have failure modes. Are any of them
   reversible, inferable, or incomplete in ways that would still disclose
   something?
2. **Would the new pre-commit control actually have prevented the original
   incident**, and would it prevent a recurrence in a form slightly
   different from the original?
3. **Is anything else here sensitive that has not been considered at all?**
   The prior work concentrated on one category of problem. Something
   outside that framing may have been missed entirely.
4. **Is the repository safe to make public again?** Give a clear
   recommendation, with reasoning, and state your confidence.

---

## Practical context

- **Repository:** `C:\Dev\onedrive-agent` (git), remote
  `github.com/nadeemmarshman/onedrive-agent`, currently **private**.
- **Do not make it public.** That decision is {{owner}}'s and depends partly
  on your findings.
- **The live data itself** sits under the OneDrive folder the agent
  operated on. You do not need to inspect it to do this job, and you should
  not modify it.
- **Some files in the working directory are intentionally excluded from
  git and do contain real personal data.** They were kept deliberately, as
  local-only working copies. Whether that arrangement is appropriate, and
  whether the exclusion is actually watertight, is a fair thing for you to
  evaluate — but their mere existence is not automatically a finding.
- **Be careful in your own reporting.** If you find sensitive content,
  describe it by category and location rather than quoting it, and do not
  write it into any file inside the repository. That is the exact mistake
  that has already recurred three times here.

---

## What to hand back

A written report covering:

- **What you did** — enough that someone else could repeat it, since this
  is a control, not a one-off.
- **What you found** — by category and location, not quoted verbatim.
- **What you could not determine**, and why. Gaps stated plainly are more
  useful than a clean bill of health that does not hold.
- **Your recommendation** on re-publication, with confidence level.
- **Anything about the approach itself** that struck you as weak,
  including anything in this brief.

If you find nothing, say so plainly — but please make it clear *what your
method was capable of detecting*, so the value of a null result can be
judged. A previous "clean" result here was technically true and
substantively wrong, because the check could not see what it was looking
for.
