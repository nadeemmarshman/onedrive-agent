# GitHub Support — request to purge unreachable objects

**Status:** drafted 2026-08-02, not yet sent. Only {{owner}} can send this
(it must come from the account owner).

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

Please **permanently remove the unreachable objects and any cached views**
of the affected commits for this repository, so that they can no longer be
retrieved by direct commit SHA or via any cached diff/blob URL.

I understand that a force-push makes commits unreachable but does not
immediately delete the underlying objects, and that they can remain
accessible by their SHA until garbage collection runs on your side. Given
the nature of the data, I would like this done explicitly rather than
waiting for routine GC.

**Commit SHAs that contained the sensitive data**

These were rewritten and are no longer reachable. Two rounds of history
rewriting were performed (the first remediation was found to be incomplete
during a follow-up audit), so both sets are listed:

*Original commits that introduced the data:*
- `ff98dcd6ad7fb0486c76154fb4110984234ce567`
- `967f00f` (short SHA)
- `4321830a1c10f5ac7bc0c17a81fb094808e6e72a`

*Also now unreachable — intermediate rewrites and other commits from the
same period, all of which contained some of the same data:*
- `e9cb670`, `45d97d9`, `af73027`, `70a2729`, `a63c89a`
- `5ea447a`, `05c0e869d5ed8ea2c2c5a05047f504e14f004858`
- `8c56950`, `73cd096`, `4004ce1`, `d67a005`

**Current, intended state of `main`**

- `c6e9b72` — `PC Backup phase + privacy breach remediation`

Everything reachable from `c6e9b72` has been verified clean.

Please confirm once the objects have been purged, and let me know if you
need any further detail or verification from me.

Thank you,
{{owner}}

---

## Notes for {{owner}} before sending

- **Replace the short SHAs with full 40-character ones if Support asks.**
  They are listed short here because the local objects have already been
  garbage-collected, so the full values are no longer recoverable from the
  working clone. If needed, they can be read from the pre-purge backup
  bundle: `git bundle list-heads <bundle>` then `git log --format=%H` after
  cloning it. The bundle is at
  `C:\Users\{{owner}}\AppData\Local\Temp\claude\onedrive-agent-prepurge-20260802-200740.bundle`
  — **note this is in a temp directory and may be cleared; copy it somewhere
  durable before relying on it.**
- **Do not attach the sensitive files** to the ticket. The paths themselves
  are the sensitive content — describing the categories, as above, is enough.
- **Keep the repository private** until Support confirms, and until you have
  decided separately whether to re-publish at all.
- If you would rather not enumerate the categories in as much detail, the
  request is still actionable with just: *"the commits contained full file
  paths disclosing personal financial, identity, medical and employment
  records."* The detail above is included because it helps Support judge
  urgency, but it is your call.
