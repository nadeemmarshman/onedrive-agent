# Handoff Brief — GitHub purge verified, I27 ready to close (Cowork → CODE)

**From:** Claude Cowork session
**To:** Claude Code session, `C:\Dev\onedrive-agent`
**Date:** 2026-08-04
**Subject:** Server-side purge confirmed by GitHub Support and independently verified by {{owner}}. RAID I27's purge item can close.
**Governance record:** `GITHUB_SUPPORT_PURGE_REQUEST.md` (request as sent), RAID I27, Backlog #18, RTM REQ-23.

---

## 1. What happened

GitHub Support replied on **2026-08-03, 12:34 UTC** (agent: Eremie), confirming
the scope-based purge requested on 2026-08-02:

> "I've cleared out unreferenced commits, and all the links should now return a
> 404 error."

{{owner}} then verified this himself on **2026-08-04, between 10:10 and 10:30 SAST**.

## 2. Why the reply alone was not accepted as evidence

The repository is **private**. An unauthenticated request returns 404 for every
URL under it, purged or not — so an anonymous check cannot distinguish
"object destroyed" from "caller not authorised", and would have produced a
false pass. Support's wording ("should now return a 404") is a statement of
expected outcome, not an observation of this repository's state.

The verification was therefore designed with a **positive control**: confirm
first that a currently-reachable commit *does* render while authenticated, which
establishes that a subsequent 404 means the object is gone rather than the caller
being unrecognised. Without that control the test proves nothing.

Same principle as I24/I25/I26 and I28/I29: a tool's — or a vendor's — report of
its own state is not evidence.

## 3. Verification performed

**Method:** signed in to github.com as `nadeemmarshman`, normal browser window
(not incognito, which would be unauthenticated and invalidate the test), each
commit URL opened directly.

**Control (must render):**

| SHA | Expected | Observed |
|---|---|---|
| `67b990f974a0d58777b92394e6060b3f54586489` (HEAD at time of test) | renders | **rendered** — "Log Unsorted folder triage; RAID I31 corrects v2's duplicate count" |

Control passed, so the results below are meaningful.

**Group A — pushed while the repository was PUBLIC (priority):**

| SHA | Expected | Observed |
|---|---|---|
| `ff98dcdad7fb0486c76154fb4110984234ce567a` | 404 | **404** |
| `967f00f4c03ebd1642d2d234cf2dad868897aee1` | 404 | **404** |
| `4321830a1c10f5ac7bc0c17a81fb094808e6e72a` | 404 | **404** |

**Group B — pushed after the repository was already private; last two carry the
ID-formatted fixture:**

| SHA | Expected | Observed |
|---|---|---|
| `05c0e869d5ed8ea2c2c5a05047f504e14f004858` | 404 | **404** |
| `21ffa3e4af49ce5730a05fdb7fcb3d7ccd43a222` | 404 | **404** |
| `e2141c3ed65c239e9615119f1c978d3fb357982a` | 404 | **404** |

**Result: 6 of 6 superseded commits return 404 while authenticated, with the
control rendering in the same session.**

**Local clone:** independently confirmed by Cowork that all three Group A SHAs
are absent locally (`git cat-file -e` fails for each), consistent with the
earlier `reflog expire` + `gc --prune=now`. Local and server sides now agree.

## 4. On Support's credentials advice

The reply carried GitHub's standard line about changing leaked credentials.
**It does not apply here** and no rotation is required. Checked before advising:

- no `.env`, `*.key`, `*.pem`, token, secret or credential file appears anywhere
  in the repository's history, across all branches
  (`git log --all --diff-filter=A --name-only`)
- no hardcoded key patterns (`sk-…`, `ghp_…`, `AKIA…`) in the current tree

The exposure was **file paths and filenames**, plus one ID-formatted test
fixture — never credentials, and never file contents. Recommend recording this
explicitly so a future reader of I27 does not re-open the question.

## 5. Requested actions for CODE

1. Record the ticket reference in `GITHUB_SUPPORT_PURGE_REQUEST.md` — line 9 is
   still `**Ticket reference:** _(not yet recorded)_`. {{owner}} holds the ticket
   number; the reply is dated 2026-08-03 12:34 UTC, agent Eremie.
2. Update **RAID I27**: mark the GitHub Support purge item **closed**, citing
   the verification in §3 — including the control, since that is what makes it a
   verification rather than a restatement of Support's claim. Suggested wording:
   *"Purge confirmed by GitHub Support 2026-08-03; independently verified by
   {{owner}} 2026-08-04 while authenticated, with a reachable-commit control
   establishing that the 404s indicate absence rather than lack of access. 6/6
   superseded SHAs 404; control rendered."*
3. Close the corresponding item in **Backlog #18**, cross-reference **RTM
   REQ-23**.
4. Add the credentials finding from §4 to I27 so it is not revisited.
5. **Leave the re-publication decision open.** It is a separate call from the
   purge and is {{owner}}'s to make. What makes re-publication safe is the
   pre-commit guard, `sanitize_repo_artifacts.py` and the extended `.gitignore`
   — not the purge. Recommend it be tracked as its own item rather than closed
   alongside this one.

## 6. Residual risk, stated plainly

The purge removes objects from GitHub's servers. It cannot retract anything
already retrieved by a third party during the ~2-day public window. At detection
the repository had **0 forks, 0 stars, 0 watchers**, which is the best available
evidence that nothing was copied — but it is evidence of absence of *signals*,
not proof of absence of *access*. I27 should retain that caveat rather than
close as though the exposure never occurred.

## 7. Lesson worth carrying into `LESSONS_LEARNED.md`

A vendor's confirmation is a claim about what they did, not an observation of
your system's state. Where the two can be distinguished by a test, run the test —
and design it so a false pass is impossible. Here that meant a positive control,
because the failure mode ("private repo 404s for everyone") produces exactly the
result a success would.

This generalises the same lesson already recorded from I24, I28 and I29, now
extended to third parties and not just to our own tooling.
