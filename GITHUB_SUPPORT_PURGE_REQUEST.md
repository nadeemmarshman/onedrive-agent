# GitHub Support — request to purge unreachable objects

**Status:** v2.0, ready to send (2026-08-02). Must be submitted by {{owner}} —
it has to come from the account owner.

**This is a web form, not an email address.**

**Sequencing decision:** originally queued behind the remaining duplication
work. Changed 2026-08-02 — {{owner}} elected to send now, agreeing with the
independent audit that an open exposure window has no technical reason to
stay open.

**SHAs verified 2026-08-02:** every 40-character SHA below was checked
against the backup bundles and confirmed to be a real commit. An earlier
draft carried one mistyped SHA (`ff98dcd6…567` for `ff98dcda…567a`), which
would have sent Support looking for an object that never existed.

**Where to send:** https://support.github.com/contact — choose
*Account or profile* → *Something else*, or reply to any existing ticket.
Do **not** raise it as a public issue or discussion.

**Before sending, confirm:**
- the repository is still **private** (it is, as of 2026-08-02)
- the force-pushes are complete and `origin/main` is at the intended commit
- you are logged in as `nadeemmarshman`

---

## Subject

Request to purge unreachable objects after force-push removing sensitive data — nadeemmarshman/onedrive-agent

---

## Message body

Hello,

I need to request server-side removal of unreachable Git objects from one
of my repositories, following a force-push that removed sensitive personal
data from its history.

**Repository:** https://github.com/nadeemmarshman/onedrive-agent
(currently set to **private**)

**What happened**

This repository is a portfolio project that de-duplicates files in my
personal OneDrive. Between 31 July and 2 August 2026, several commits
inadvertently included raw scan output containing the **full file paths**
of my personal documents. The file *contents* were never committed — only
the paths and filenames — but those alone disclose sensitive personal
information, including:

- employment dispute records (a termination, suspension, disciplinary
  hearing and CCMA referral)
- firearm licence records, including specific firearm models and a
  competency certificate
- identity, marriage and estate documents
- medical scheme and insurer membership
- tax, payslip and loan records, including an employee number
- the names of family members and other third parties

The repository was **public** during this period. I discovered the issue
on 2 August 2026 and set it to private the same day. The exposure window
was approximately two days, and at the point of discovery the repository
had **0 forks, 0 stars and 0 watchers**.

Separately, and found during a later review: one commit contained a
13-digit number in the format of a South African ID number. It was created
as a software test fixture and was intended to be fictitious, but it
satisfies the Luhn checksum and encodes a valid date of birth, so I cannot
rule out that it corresponds to a real person. That commit was pushed after
the repository was already private, so it was never publicly exposed — but
I would like it purged on the same basis as the rest.

**What I have already done**

1. Set the repository to private (verified — the unauthenticated API now
   returns 404 for it).
2. Removed the sensitive content from all affected files.
3. Rewrote the affected history locally and force-pushed to `main`. The
   commits that contained the sensitive data are no longer reachable from
   any branch or tag.
4. Expired my local reflog and ran garbage collection, so the old objects
   no longer exist in my local clone.

**What I am requesting**

Please **permanently remove all unreachable objects for this repository**,
so that no commit that is not reachable from a current branch or tag can be
retrieved by SHA or via any cached diff/blob URL.

I am deliberately phrasing this as "all unreachable objects" rather than a
list of specific commits. The repository has undergone **multiple history
rewrites** during remediation, and more than one working session has pushed
to it, so I cannot guarantee an enumerated list is exhaustive. A
scope-based purge avoids that problem entirely. The SHAs below are offered
as supporting detail, not as the definition of the request.

I understand that a force-push makes commits unreachable but does not
immediately delete the underlying objects, and that they can remain
accessible by their SHA until garbage collection runs on your side. Given
the nature of the data, I would like this done explicitly rather than
waiting for routine GC.

**Superseded (unreachable) commit SHAs, as far as I can identify them**

These were rewritten and are no longer reachable. Three rounds of history
rewriting occurred in total (the first remediation was found incomplete by a
follow-up audit; a later session then squashed two commits), so all sets are
listed:

**Group A — pushed while the repository was PUBLIC.** These carried the
personal file paths and are the priority:

```
ff98dcdad7fb0486c76154fb4110984234ce567a
967f00f4c03ebd1642d2d234cf2dad868897aee1
e9cb670d307cb09a2ff03c5081c1af9d64f1c236
45d97d96f65a58c2b97ac42b75e5e8d2b8ada5e3
af730278e32364d5ee9f1dbfca39b4295f427d33
70a272955b976313f7e4f80b0c1e67caef75793c
a63c89a2b3bc2132cd06090cfa63babf50e72406
4321830a1c10f5ac7bc0c17a81fb094808e6e72a
```

**Group B — pushed after the repository was already private.** Lower
urgency, same class of data; the last two also contain the ID-formatted
number described above:

```
05c0e869d5ed8ea2c2c5a05047f504e14f004858
e2141c3ed65c239e9615119f1c978d3fb357982a
21ffa3e4af49ce5730a05fdb7fcb3d7ccd43a222
```

Further intermediate commits from the same rewrites (`5ea447a`, `8c56950`,
`73cd096`, `4004ce1`, `d67a005`) are also unreachable. I hold only their
abbreviated SHAs, which is precisely why the request above is scoped to
*all* unreachable objects rather than to this list.

**Current, intended state of `main`**

Whatever `main` currently points to on your side is correct — the branch is
still being committed to, so I have deliberately not pinned a SHA here that
would be stale by the time you read this. Everything **reachable** from
`main` is intended to be retained.

Everything reachable has been verified clean: I scanned every blob in the
full current history and found no occurrence of the sensitive data, and
`git fsck` reports no unreachable objects in my local clone.

To be unambiguous: **the request is to purge only what is _unreachable_.**
Nothing reachable from `main` or from any tag should be removed.

Please confirm once the objects have been purged, and let me know if you
need any further detail or verification from me.

Thank you,
{{owner}}

---

## Notes for {{owner}} before sending

- **Copy the backup bundles somewhere durable before sending.** They are now
  the only remaining source of the old objects — everything has been
  garbage-collected locally. Both sit in a temp directory that may be
  cleared without warning:
  - `%LOCALAPPDATA%\Temp\claude\onedrive-agent-prepurge-20260802-200740.bundle`
  - `%LOCALAPPDATA%\Temp\claude\onedrive-agent-preIDpurge-20260802-213212.bundle`

  If Support asks for the remaining abbreviated SHAs in full, clone a bundle
  and read them:
  `git clone <bundle> tmp && git -C tmp log --format=%H`
- **Do not attach the sensitive files** to the ticket. The paths themselves
  are the sensitive content — describing the categories, as above, is enough.
- **Keep the repository private** until Support confirms, and until you have
  decided separately whether to re-publish at all.
- If you would rather not enumerate the categories in as much detail, the
  request is still actionable with just: *"the commits contained full file
  paths disclosing personal financial, identity, medical and employment
  records."* The detail above is included because it helps Support judge
  urgency, but it is your call.
