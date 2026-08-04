# GitHub Support — second purge request (history rewrite, 2026-08-04)

**Status: DRAFTED, not yet sent.** Companion to `GITHUB_SUPPORT_PURGE_REQUEST.md`
(the original request, resolved — Ticket 4624306, confirmed 2026-08-03,
independently verified 2026-08-04). This is a separate, second request for
a second, later history rewrite — same repository, unrelated set of
objects.

**This document was drafted by an AI assistant and must be sent by
{{owner}} himself.** The same limitation as the first request applies:
submitting GitHub Support's web form requires being signed in as the
account owner, which an assistant cannot do.

**Where to send:** https://support.github.com/contact — choose
*Account or profile* → *Something else*, or reply to the existing ticket
(4624306) referencing it as a related, follow-up request. Do **not** raise
it as a public issue or discussion.

**Before sending, confirm:**
- the repository is still **private**
- the force-pushes below are complete and `origin/main` is at the intended
  commit (`1ef05220cd3a155d006a6f218dbcf709155515e2` as of this draft)
- you are logged in as `nadeemmarshman`

---

## Subject

Follow-up purge request (second history rewrite) — nadeemmarshman/onedrive-agent, ref Ticket 4624306

---

## Message body

Hello,

This is a follow-up to Ticket 4624306, which you confirmed resolved on
2026-08-03. I need a second, separate purge for the same repository —
different objects, unrelated cause.

**Repository:** https://github.com/nadeemmarshman/onedrive-agent
(still **private**)

**What happened this time**

This repository has remained private throughout, so none of what follows
was ever publicly exposed — this is a precautionary purge, not a breach
response. While preparing the repository for a possible future
re-publication, an independent review found two separate things worth
fixing in the commit history itself, not just the current file content:

1. My own full name appeared, deliberately, throughout many operational
   log files (it is intentionally still present on a few identity-facing
   documents like the README, by design). On review, having it repeated so
   often alongside employment-dispute and hobby-related detail across many
   documents was worth reducing, so I had it redacted from those specific
   files going forward.
2. Two files that no longer exist in the repository (removed in the same
   commit session they were mistakenly added) were still fully readable in
   older commits — one was an old résumé draft that included my phone
   number.

**What I have already done**

1. Rewrote the affected history locally using `git-filter-repo`, scoped
   precisely so only the intended files' history changed.
2. Force-pushed the rewritten history to `main` and to all three existing
   tags (their SHAs changed too, as ancestors of the rewritten commits).
3. Verified afterward: the name no longer appears anywhere in history
   outside the files where it's meant to stay; the two removed files are
   unreachable from any commit; the current file content is unchanged from
   before the rewrite (only history changed); `git fsck` reports no
   unreachable objects in my local clone after garbage collection.

**What I am requesting**

As with the previous ticket, please **permanently remove all unreachable
objects for this repository** — a scope-based purge rather than an
enumerated list, since a rewrite like this touches many commits and I
would rather not risk an incomplete list. Everything reachable from
`main` or from any of the three tags is intended to be retained; nothing
else should be.

**For reference — the previous (now superseded) tip and tag commits:**

```
main (old tip):                      36293d9c758ba404cda9c7cc5ea6d420bd76a8be
v1.0-foundational-build (old):       0b9b0d5f0acf8b949d58b3997e61ef24113241a6
v2.0-live-run-camera-roll (old):     79c910fc0a128f4a5042f802a79516388108f78e
v2.1-live-run-camera-roll-complete (old): 1625b113fa927a801ee85c9cb69671bbd6530469
```

**Current, intended state — for contrast, not part of the request:**

```
main (new tip):                      1ef05220cd3a155d006a6f218dbcf709155515e2
v1.0-foundational-build (new):       81b52cf061c39515dda38c11edb8047cec6867dd
v2.0-live-run-camera-roll (new):     c29a67bf276fadb041c9ce84543a088c35fdfe82
v2.1-live-run-camera-roll-complete (new): 0bf0b3a8ad5b0d2284771d72f23052a3fbafb021
```

Everything reachable from the current tip and tags is correct and should
be retained. To be unambiguous: **the request is to purge only what is
now unreachable** — the four commits above and everything between them and
their former history, roughly 114 commits in total by my own count, none
of which I am enumerating individually since the request is scope-based.

Please confirm once done, and let me know if you need anything further.

Thank you,
{{owner}}

---

## Notes for {{owner}} before sending

- The backup bundle taken immediately before this rewrite is at:
  `D:\OneDrive-Agent-Backups\pre-history-rewrite-20260804-133654.bundle`
  — keep it until you're confident this is fully resolved.
- No need to attach or describe the résumé/phone-number file in detail —
  "an old résumé draft that included my phone number" is enough; don't
  paste the actual number into the ticket.
- This is lower urgency than the first request — the repo was never public
  with this content — so there's no particular rush, but the same "send it
  rather than let it linger" logic that applied last time still applies.
