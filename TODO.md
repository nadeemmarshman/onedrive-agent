# TODO — sequenced follow-ups

Short, ordered list of things that are **waiting on a trigger** rather than
waiting on capacity. Longer-lived scope lives in `BACKLOG.md`; this file is
just "what happens next, and after what."

---

## 1. Finish the duplication work  ← current

Remaining in flight:

- [x] **PC Backup quarantine deleted, 2026-08-03.** 1,070 files, 2.84 GB
      reclaimed via OneDrive web (RAID I26). Verified via the details
      panel's Path/Activity/Size before deleting, and on-disk absence after.
- [x] **6 suffixed `(from DocFolderBackup)` files reconciled, 2026-08-03.**
      Compared by actual content (text similarity + diff, sheet/string
      comparison), not just filename/date. All 6: backup dated 2025, live
      dated Feb 2026, and every divergence was live *adding* material, never
      contradicting the backup. Nothing to merge back — quarantined all 6 to
      `_Duplicates_PendingDeletion\Reload_Notes_Superseded\`.
- [x] **2 same-named CV versions reconciled, 2026-08-03.** Third-party
      document, so compared by structure only (timestamps, revision count,
      word count) — never actual text. Both shared an identical creation
      timestamp; the ex-ResumeResources copy was the later revision (later
      modified date, +1 save, +1 word). Kept as canonical, promoted to the
      plain filename; older ex-DocFolderBackup copy quarantined to
      `_Duplicates_PendingDeletion\CV_Superseded\`.
- [ ] **Decide on the remaining survey findings** — the 19.58 GB incomplete
      Google Takeout export (parts 001/005/009 missing) and the 41.18 GB
      Videos folder (no duplication found; an archival decision, not a dedup one).
- [ ] **RAID I28/I29 — final permanent delete of `_Duplicates_PendingDeletion\
      Internal_Duplicates_20260803\`** (315 files, ~578.3 MB, after the
      2026-08-03 orphan restore). **Gate passed**: `verify_dedup_invariants.py`
      confirms 0 orphaned groups. Not yet deleted — {{owner}}'s call, same as
      every other delete in this project. Two things worth deciding first,
      not blocking: the 6 `(from DocFolderBackup)` reload-notes pairs and
      21 restored `5 Certificates` documents both now have a stale duplicate
      sitting alongside the canonical copy, deliberately left unresolved
      rather than auto-picked a second time — worth a look before or after
      the delete, your call.

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
- [x] **Backup bundles relocated outside the repository, 2026-08-02.**
      Now at `D:\OneDrive-Agent-Backups\`. They were briefly inside the
      repo, which was a real hazard: they hold the complete pre-purge
      history, and the pre-commit guard cannot see into them (compressed,
      so text scanning returns CLEAN). `D:` is not cloud-synced, not
      scanned by the agent, and does not consume OneDrive quota. Verified
      before the originals were deleted: MD5-identical, `git bundle verify`
      reports a complete history, and a test clone recovered 94 commits
      including the purged ones.
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
