# TODO — sequenced follow-ups

Short, ordered list of things that are **waiting on a trigger** rather than
waiting on capacity. Longer-lived scope lives in `BACKLOG.md`; this file is
just "what happens next, and after what."

---

## 1. Finish the duplication work — done, 2026-08-04

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
- [x] **RAID I28/I29 — final permanent delete of `_Duplicates_PendingDeletion\
      Internal_Duplicates_20260803\`, done 2026-08-03.** 315 files, ~578.3 MB,
      deleted by {{owner}} via OneDrive web. Plus several further same-day
      quarantine-then-delete rounds: `Trash` (fixed-term-contract email +
      PDF, PDF relocated to its correct folder first), `ArchiveToDelete`'s
      old resume drafts, an already-empty `Bank Statements(Esther` shell,
      and the already-caught `edX_files` cache duplicate. Re-ran
      `verify_dedup_invariants.py` after all deletes: **0 orphaned groups**,
      confirmed. Both RAID I28 and I29 closed.
- [ ] **Two stale-duplicate pairs, deliberately left unresolved.** The 6
      `(from DocFolderBackup)` reload-notes pairs and 21 restored
      `5 Certificates` documents both still have a stale duplicate sitting
      alongside the canonical copy — not auto-picked a second time. Worth a
      look whenever convenient, not blocking anything.
- [x] **`Unsorted\` (31 files) triaged, 2026-08-04.** Every file identified
      (content read where needed, not just filename) and checked by hash
      against the rest of the live tree. Found 3 duplicate relationships,
      not the 2 Cowork's v2 report stated (RAID I31) — all 3 quarantined to
      `_Duplicates_PendingDeletion\Unsorted_Triage_20260803\`, keepers
      confirmed intact. A further 13 non-duplicate files were reviewed and
      quarantined at {{owner}}'s direction: reconciled financial records,
      already-superseded utility statements, a hobby-association membership
      record, two unrelated leisure-booking confirmations, and 2 files with
      no ongoing value. 16 files quarantined in total, pending {{owner}}'s
      final delete.
- [x] **Remaining 15 files resolved, 2026-08-04. `Unsorted\` is now empty
      (31 → 0).** By {{owner}}'s direction: correspondence relating to a
      closed, unrelated prior personal matter (3 files) moved to its
      existing, already-organised folder under Career Documents; 5
      insurance/medical-scheme documents moved to their existing organised
      folder under Bank & Insurance; 5 older resume-related files moved to
      a new sibling folder next to the maintained current-resume folder
      (`2 Career Documents\2 Archived Resumes\`, created for this); 1 work
      email and 1 file that could not be opened for review (protected)
      quarantined to `_Duplicates_PendingDeletion\Unsorted_Triage_20260803\`
      for {{owner}}'s own review/decision rather than filed automatically.
      Quarantine folder total now 18 files, pending final delete.
- [x] **Quarantine batch actioned by {{owner}}, 2026-08-04.** All 18 files in
      `_Duplicates_PendingDeletion\Unsorted_Triage_20260803\` deleted or
      moved to where {{owner}} wanted them — folder confirmed empty on disk.
      `Unsorted\` triage is fully closed end to end.

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
- [x] **Support confirmed 2026-08-03 (Ticket 4624306), independently
      verified by {{owner}} 2026-08-04** with a positive-control test (a
      reachable commit rendered while authenticated; 6/6 superseded commit
      SHAs returned 404 in the same session — see RAID I27). Ticket
      reference recorded, RAID I27 and Backlog #18's purge item both
      closed.

## 3. Then: decide on re-publication  ← current

**Trigger met 2026-08-04 — Support has confirmed the purge.** This is now
the live open item.

- [x] **Independent stranger-read review done, 2026-08-04 (RAID I32).**
      Found the placeholder delimiter itself was silently stripped by
      GitHub's own renderer repo-wide, and prompted a real reconsideration
      of the owner's-name-unredacted decision. Both fixed: delimiter
      switched to `{{...}}` (verified against GitHub's actual rendering
      API), name redacted in 36 operational-log files, kept on 9
      identity/portfolio-facing documents. See RAID I32 and
      `LESSONS_LEARNED.md` §2 lesson 12 for full detail.
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
- [x] **Git history rewritten and force-pushed, 2026-08-04 (RAID I32).**
      Name redacted across all history in the 35 operational-log files
      (kept in the 9 identity/portfolio-facing ones); two stray,
      already-deleted files carrying a phone number and out-of-scope
      content purged from history entirely. Verified before and after —
      see RAID I32 for the full method.
- [ ] **Second GitHub Support purge request drafted, 2026-08-04 — awaiting
      {{owner}} to send.** `GITHUB_SUPPORT_PURGE_REQUEST_20260804.md`,
      companion to the resolved Ticket 4624306. Covers the ~114 commits
      superseded by today's history rewrite. Lower urgency than the
      original — the repo stayed private throughout, this content was
      never reachable while public — but drafted so it's ready to send
      rather than left to only routine GC.
