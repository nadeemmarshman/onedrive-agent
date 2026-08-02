# TODO — sequenced follow-ups

Short, ordered list of things that are **waiting on a trigger** rather than
waiting on capacity. Longer-lived scope lives in `BACKLOG.md`; this file is
just "what happens next, and after what."

---

## 1. Finish the duplication work  ← current

Remaining in flight:

- [ ] **Final delete of the PC Backup quarantine** —
      `_Duplicates_PendingDeletion\PC Backup\` (1,070 files, 2.77 GB).
      Delete via **OneDrive web**, not File Explorer (RAID I26: Explorer's
      OneDrive "Home" view serves a stale listing for script-created folders).
- [ ] **Reconcile the 6 suffixed `(from DocFolderBackup)` files** in the
      reload-notes folder — same name, genuinely different content, so both
      copies were kept. Decide which is current and drop the other.
- [ ] **Reconcile the 2 same-named CV versions** consolidated into one folder.
- [ ] **Decide on the remaining survey findings** — the 19.58 GB incomplete
      Google Takeout export (parts 001/005/009 missing) and the 41.18 GB
      Videos folder (no duplication found; an archival decision, not a dedup one).

## 2. Then: send the GitHub Support purge request

**Trigger: only once item 1 is complete.** Deliberately sequenced after the
duplication work so the request is sent once, against a final history,
rather than needing a follow-up if further commits are made.

> **The independent audit (2026-08-02) disagrees with this sequencing** and
> recommends sending it now rather than queueing it behind unrelated
> cleanup, on the grounds that the GitHub-side exposure window is open and
> has no technical reason to stay open.
>
> {{owner}}'s call, so the sequencing above stands unless he changes it. Two
> points to decide on, stated accurately:
>
> - **The exposure is real.** Commits containing real personal paths were
>   pushed while the repo was public. A force-push rewrites refs, not
>   objects, so GitHub can still serve those commits by SHA until its own
>   GC runs. That is the whole reason the request exists.
> - **One nuance in the audit's reasoning.** It cites the recovered
>   dangling objects as confirmation that sensitive content sits in what
>   was rewritten away. Those particular objects were **local-only** —
>   never in a commit, never reachable from a ref, therefore never pushed.
>   They do not bear on GitHub-side exposure. The conclusion still holds,
>   but on the original evidence (the pushed commits), not on that.
>
> Cost of sending now: if further commits follow, the SHA list in the
> request is incomplete and may need a follow-up message. Cost of waiting:
> the window stays open for however long item 1 takes.

- [x] **SENT 2026-08-02.** Submitted by {{owner}} via the GitHub Support web
      form. Sequencing changed from "after the duplication work" to "now",
      agreeing with the independent audit that an open exposure window had
      no technical reason to stay open.
- [x] Backup bundles moved out of the temp directory by {{owner}}, into
      `PurgeGItHPrivateData\`. **Note:** that folder sits inside the repo and
      is now gitignored — the bundles hold the complete pre-purge history,
      and the pre-commit guard cannot detect them (compressed, so text
      scanning sees nothing). Moving them outside the repo would be safer.
- [ ] After sending: record the ticket reference against RAID I27 and mark
      Backlog #18's outstanding item closed when Support confirms.

## 3. Then: decide on re-publication

**Trigger: Support confirms the purge.**

- [ ] Review the sanitised artefacts as a reader would — particularly the
      two reports now truncated to their summary sections, and the reports
      where real names became placeholders. That readability trade-off is
      worth seeing before the repo is public again.
- [ ] Decide whether to re-publish at all, and whether the résumé links
      still point where you want them to.

---

## Standing, not sequenced

- [ ] **Drop the stale `refs/stash`** (`01e3f38`) if you don't want it — a
      README WIP from 2026-07-09, verified clean and pre-dating the
      Documents phase. Left in place because discarding stashed work is
      your call, not something to clean up automatically.
- [ ] **Enable the pre-commit guard on any other clone** of this repo:
      `git config core.hooksPath .githooks` (it is per-clone, not carried
      by the repository itself).
