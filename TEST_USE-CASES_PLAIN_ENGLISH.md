# Test Use Cases — Plain English

**Companion to:** `TEST_BED_AND_CASES.md` (the technical build/execution recipe) and `TEST_STRATEGY.md` (the overall test plan). This document exists purely to make every test case readable by a non-technical reviewer — a recruiter, hiring manager, or interviewer — without needing to understand PowerShell commands or file hashes.

**Acronyms:** expanded on first use per document and per major section; full register in [`GLOSSARY.md`](./GLOSSARY.md).

**A note on the word "Agent":** throughout this project, "the OneDrive AI Agent" refers specifically to the Python-based, Claude-driven tool built for this project — not a call-centre agent, a logistics agent, or any other kind of "agent." This document always spells it out in full for that reason.

**Case-ID prefixes:**
- **GB = Green-line Baseline** — happy-path cases the OneDrive AI Agent *should* detect and handle correctly.
- **RB = Red-line Baseline** — negative, edge, and adversarial cases the OneDrive AI Agent must handle *safely* (decline correctly, or fail gracefully without crashing or bypassing a safety control).

Each entry follows the same shape: a one-line user story, what's actually being checked, what should and shouldn't happen, and why it matters for the portfolio story.

---

## Green-line cases (happy path)

### GB-01 — True duplicate (identical content, different name)

**As a user, I want the OneDrive AI Agent to correctly spot two files that are actually the same, even if I gave them different names** — so it can find real duplicate clutter, not just files that happen to be named similarly.

What GB-01 is checking:
- Two files exist with different names but the exact same content inside (like `report.txt` and `report_COPY.txt`).
- The OneDrive AI Agent looks at the actual content of each file (using something called a hash — a fingerprint of the file's content), not just the filename.
- What should happen: the OneDrive AI Agent recognizes they're identical, groups them together, and proposes keeping one and deleting the other.
- What should not happen: the OneDrive AI Agent misses them because the names are different, or wrongly flags files as duplicates just because the names look similar.

Why this matters: this is the core promise of the tool — finding real duplicates by content, not guessing from names. Get this wrong and the whole product is untrustworthy.

---

### GB-02 — Duplicate group of three

**As a user, I want the OneDrive AI Agent to handle it correctly when there are three (or more) identical copies, not just two** — keeping exactly one and proposing to delete the rest, not leaving extras behind or deleting everything.

What GB-02 is checking:
- Three files exist with identical content.
- The OneDrive AI Agent groups all three together as one duplicate group, not as separate pairs.
- What should happen: the OneDrive AI Agent proposes keeping 1 and deleting the other 2.
- What should not happen: it deletes all three (leaving nothing), or fails to notice the third file belongs to the group.

Why this matters: this proves the "keep one, delete the rest" rule scales beyond the simplest two-copy case — which is what actually happens in real, cluttered folders where the same file gets copied multiple times over the years.

---

### GB-03 — Convertible file (.bmp)

**As a user, I want the OneDrive AI Agent to notice old, bulky file formats (like old-style .bmp images) and suggest converting them to something smaller** — even though, right now, it only suggests this and doesn't actually perform the conversion yet.

What GB-03 is checking:
- A `.bmp` image file exists in the test folder.
- The OneDrive AI Agent recognizes it as a "convertible" file type.
- What should happen: a proposal to convert appears; if approved, the tool logs the intent, but the file itself is left unchanged (this is deliberate — the actual conversion feature isn't built yet).
- What should not happen: the OneDrive AI Agent silently damages or replaces the file, or pretends the conversion happened when it didn't.

Why this matters: this shows honest design — a feature that isn't finished is clearly labelled as not finished, rather than quietly faked. That's a good governance signal, not a bug.

---

### GB-04 — Cross-folder duplicate (recursion)

**As a user, I want the OneDrive AI Agent to find duplicate files even when they're sitting in completely different folders, not just next to each other** — because that's how real duplicate clutter actually happens (I copy a file into a new folder and forget the old one is still there).

What GB-04 is checking:
- The same file content exists in two places: the main folder and a subfolder inside it.
- The OneDrive AI Agent is told to search folders and their subfolders, not just the top level.
- What should happen: the copy sitting in the subfolder is correctly grouped with the original as a duplicate.
- What should not happen: the OneDrive AI Agent only looks at the top-level folder and misses the copy buried in a subfolder.

Why this matters: real OneDrive folders build up duplicate mess across many nested folders over years — if the tool only checked one folder at a time, it would miss most of the real clutter.

---

### GB-05 — Unique file (true negative)

**As a user, I want the OneDrive AI Agent to leave files alone when they're genuinely one-of-a-kind** — I don't want it flagging or touching something just because it feels like it should "do something."

What GB-05 is checking:
- A file exists whose content doesn't match anything else in the folder.
- What should happen: the OneDrive AI Agent doesn't group it with anything and proposes no action for it at all.
- What should not happen: the OneDrive AI Agent invents a false match or proposes an action on a file that has nothing wrong with it.

Why this matters: a tool that finds "problems" even when there aren't any would be untrustworthy. This proves it can correctly do nothing when nothing needs doing.

---

### GB-06 — Mixed realistic folder

**As a user, I want to see the OneDrive AI Agent handle a realistic, messy folder correctly all at once** — duplicates, near-misses, convertible files, and unique files all mixed together, the way my actual OneDrive looks, not one tidy example at a time.

What GB-06 is checking:
- All the green-line cases (GB-01 to GB-05) are combined into a single folder, and the OneDrive AI Agent is run once over all of it together.
- What should happen: every case is handled correctly at the same time — duplicates grouped and proposed for deletion, the convertible file flagged, the unique file left alone — with nothing interfering with anything else.
- What should not happen: something that works fine on its own breaks or gets confused when mixed in with everything else.

Why this matters: individual tests proving each piece works is good, but this is the test that proves it all holds together as one realistic solution — the closest thing to what actually happens on pilot day.

---

## Red-line cases (edge cases and failure handling)

### RB-01 — Near-miss (similar but NOT identical)

**As a user, I don't want the OneDrive AI Agent deleting a file just because it looks almost the same as another one** — near-enough is not good enough when the action is permanent.

What RB-01 is checking:
- Two files exist that are almost identical — same general content, but with one small difference (like a missing punctuation mark).
- The OneDrive AI Agent checks the actual content fingerprint, which will be different even for a tiny change.
- What should happen: the OneDrive AI Agent correctly sees they are NOT identical and proposes no deletion for either.
- What should not happen: the OneDrive AI Agent gets fooled by how similar the files look and proposes a deletion anyway.

Why this matters: this is the flip side of GB-01 — it proves the OneDrive AI Agent isn't just deleting anything vaguely similar. A tool that's too aggressive here could destroy genuinely different files, like two drafts of a document that are 99% the same but not identical.

---

### RB-02 — Same content, different extension

**As a user, I want to know exactly what the OneDrive AI Agent will do when two files have identical content but different file types (like a `.txt` and a `.log` that happen to contain the same text)** — and I want that behaviour to be a deliberate decision, not an accident.

What RB-02 is checking:
- Two files exist with identical content but different file-type extensions.
- What should happen: the OneDrive AI Agent treats them as duplicates anyway, because it judges by content, not file type — a decision that was discussed and deliberately agreed on, not a coincidence of the code.
- What should not happen: nothing here is "wrong" behaviour — this test is checking that the documented decision actually matches what the code does.

Why this matters: this shows the difference between an assumption and a decision. Anyone reviewing this project can see the behaviour was thought through and agreed on, not accidental.

---

### RB-03 — Empty folder

**As a user, I want the OneDrive AI Agent to handle an empty folder calmly** — not crash, not get confused, just correctly report there's nothing to do.

What RB-03 is checking:
- A completely empty subfolder exists in the test bed.
- What should happen: no crash; the OneDrive AI Agent proposes nothing for that folder and finishes normally.
- What should not happen: the OneDrive AI Agent errors out or hangs on a folder with zero files in it.

Why this matters: real folders are sometimes empty — leftovers from a previous cleanup, or just unused. The tool needs to shrug this off, not break.

---

### RB-04 — Unicode and long filenames

**As a user, I want the OneDrive AI Agent to cope with filenames that have accented letters, non-English characters, or names that are unusually long** — because real files, especially from different languages or older systems, often look like this.

What RB-04 is checking:
- A file with accented or special characters in its name exists (for example, `café_notés_ünïcode.txt`).
- A file with a very long filename exists.
- What should happen: both are scanned and handled without any error — the OneDrive AI Agent just does its job on them like any other file.
- What should not happen: the OneDrive AI Agent crashes, garbles the filename, or silently skips these files.

Why this matters: a tool that only works on plain English filenames would fail on a lot of real-world OneDrive content. This proves basic robustness on realistic filenames.

---

### RB-05 — Read-only file

**As a user, if a file is marked "read-only" and the OneDrive AI Agent tries to delete it after I've approved that, I want to know clearly whether it succeeded or failed** — not have it fail silently or pretend it worked.

What RB-05 is checking:
- A file is copied and then marked read-only (a Windows setting that restricts changes).
- If it's proposed for deletion and I approve it, the OneDrive AI Agent attempts the delete.
- What should happen: either the delete succeeds (read-only alone doesn't always block deletion on Windows), or it fails cleanly with a clear error and an alert email — and the run continues with the rest of the approved actions either way.
- What should not happen: the OneDrive AI Agent crashes the whole run, or claims success when the file is actually still there.

Why this matters: read-only files show up in real folders — backups, templates, downloaded files. The tool needs to handle this specific, common Windows quirk predictably.

---

### RB-06 — Permission-denied on delete (true ACL deny)

**As a user, I want the OneDrive AI Agent to handle a file it's not allowed to delete gracefully and safely — not crash, not silently skip it, not pretend it succeeded** — so that I can trust it when it runs on my real files.

What RB-06 is checking:
- There's a test file (`denied.txt`) that's deliberately locked down with a permission rule saying "this account may not delete this file" (an ACL deny — ACL means Access Control List, the Windows permission system).
- The OneDrive AI Agent is told to delete it anyway (this is the human-approved action).
- What should happen: the OneDrive AI Agent tries, Windows blocks it, the OneDrive AI Agent catches that failure properly, sends an alert email saying "this failed," and the file is still there afterward, completely untouched.
- What should not happen: the OneDrive AI Agent crashes with an ugly error, thinks the delete worked when it didn't, or silently does nothing without telling you.

**Note:** because which file gets kept vs. proposed for deletion is partly the OneDrive AI Agent's own decision at run time, `denied.txt` doesn't always end up in the delete list on a given run. When that happens, this case is exercised separately, as its own small standalone check, rather than skipped.

Why this matters: proof that the OneDrive AI Agent fails safely and visibly when something goes wrong. That's a real governance/reliability signal, not just "it deletes files."

---

### RB-07 — Reject-then-continue

**As a user, I want to be able to say "no" to one specific deletion the OneDrive AI Agent proposes, while still saying "yes" to others in the same run** — and have it respect that exactly, not treat my "no" as a reason to stop everything or quietly ignore it.

What RB-07 is checking:
- During a live run, when the OneDrive AI Agent presents its list of proposed actions, I reject one and approve another.
- What should happen: the rejected file is left completely untouched; the approved file is still deleted; the run finishes cleanly.
- What should not happen: the OneDrive AI Agent stops the whole run because of the rejection, or deletes the rejected file anyway by mistake.

Why this matters: this is the everyday, real behaviour of the human-approval gate — proving item-by-item control actually works, not just an all-or-nothing "approve everything" button.

---

### RB-08 — OneDrive recycle-bin recovery

**As a user, if the OneDrive AI Agent deletes a file inside my actual OneDrive folder, I want to know I can still get that file back through OneDrive's own recycle bin** — the same safety net I'd have if I'd deleted it myself by mistake.

What RB-08 is checking:
- A small test folder is built inside a real, OneDrive-synced location (unlike most other cases, which use a separate, isolated test folder outside OneDrive).
- A duplicate file is created and, in a run, approved for deletion.
- What should happen: after deletion, the file appears in OneDrive's own Recycle Bin (not just the regular Windows one) and can be restored from there.
- What should not happen: the file is gone with no way to recover it through OneDrive's normal safety net.

Why this matters: this proves the tool's real-world safety net actually works the way it's supposed to — recoverability is checked directly, not just assumed.

---

### RB-09 — Snapshot precondition ("no snapshot, no actions")

**As a user, I want the OneDrive AI Agent to refuse to delete or change anything if it can't first write down a record of what existed beforehand** — no exceptions, even if everything else about the run looks fine.

What RB-09 is checking:
- The location where the OneDrive AI Agent would normally save its "before" record is deliberately blocked, so it can't be written.
- The OneDrive AI Agent is then run.
- What should happen: the OneDrive AI Agent detects it can't write the safety record, refuses to execute any actions at all, and reports the problem clearly.
- What should not happen: the OneDrive AI Agent goes ahead and deletes files anyway without having saved a "before" record first.

Why this matters: this is a hard governance rule, not a nice-to-have. It proves the "safety net before action" promise can't be silently skipped, even by an unexpected technical glitch.

---

### RB-10 — Online-only / placeholder file (exploratory)

**As a user, I want to understand what the OneDrive AI Agent does when it meets a file that looks normal in File Explorer but hasn't actually been downloaded to my computer yet** — because getting this wrong could mean wrongly grouping unrelated files as "duplicates," or triggering a slow download I didn't ask for.

What RB-10 is checking:
- A file in the OneDrive secondary test folder is deliberately marked "online-only" — its content lives only in the cloud, not on this PC.
- The OneDrive AI Agent scans it.
- What should happen: this one is exploratory, not pass/fail — we're watching what actually happens (does it read the file as empty? trigger a download? error out?) and then making a deliberate, documented decision about whether it needs fixing.
- What should not happen: anything crashing or being mishandled silently, without anyone noticing.

Why this matters: this is the one real-world condition the tool hasn't been specifically built to handle yet. Testing it openly — rather than ignoring it — is the honest, responsible thing to do, and it's logged explicitly so the pilot sign-off doesn't overclaim what's actually been proven.

---

### RB-11 — Locked file (open by another process)

**As a user, if I happen to have a file open in another program (like Word) at the exact moment the OneDrive AI Agent is checking or trying to delete it, I want it to handle that sensibly** — not crash the whole run over one locked file.

What RB-11 is checking:
- A file is deliberately kept open/locked by a separate process while the OneDrive AI Agent runs against it.
- What should happen: the OneDrive AI Agent either handles the lock gracefully — skipping it with a clear message, or failing cleanly on just that one file — without crashing the rest of the run.
- What should not happen: the whole run crashes or hangs because one file happened to be open elsewhere.

Why this matters: this is an everyday real-world situation. Proving the tool copes with it, rather than falling over, matters for actual day-to-day usability, not just theoretical correctness.

---

### RB-12 — Zero-byte file

**As a user, I want the OneDrive AI Agent to handle a completely empty file sensibly** — not error out, and not wrongly treat every empty file as a "duplicate" of every other empty file just because they're both empty.

What RB-12 is checking:
- A file with zero bytes of content (completely empty) exists.
- What should happen: the OneDrive AI Agent processes it without crashing; if it groups it with other empty files as a "duplicate," that's logged as a known, understood quirk (all empty files technically look identical), not treated as a meaningful duplicate worth deleting.
- What should not happen: the OneDrive AI Agent crashes on the empty file, or treats "both files are empty" as a real, actionable duplicate.

Why this matters: edge cases like this are exactly where poorly-built tools tend to break. Proving it doesn't is a basic robustness signal.

---

### RB-13 — Interrupted run → resume safety (the "crown jewel")

**As a user, I want to know that if my computer crashes or loses power halfway through a run, the OneDrive AI Agent won't wake back up and finish deleting things without asking me again** — because a half-finished deletion I never approved is the single worst thing this tool could do.

What RB-13 is checking:
- A run is started, and the OneDrive AI Agent reaches the point where it's showing proposed deletions and waiting for my "yes" or "no."
- Right at that moment — before I've answered — the process is killed (simulating a crash, power cut, or closed window).
- The OneDrive AI Agent is then restarted.
- What should happen: the OneDrive AI Agent picks up exactly where it left off — still waiting for my approval, having done nothing on its own. It does not assume "yes," and it does not start over and re-decide on its own.
- What should not happen: the OneDrive AI Agent resumes by silently continuing straight into deleting files, treating the interruption as if I'd already said yes.

Why this matters: this is the single most important safety test in the whole project. It's the difference between "a tool that asks permission" and "a tool that asks permission, unless something goes wrong, in which case it just does it anyway." Passing this is what makes the human-approval gate a real safety guarantee, not just a feature that works when nothing goes wrong.

---

## Document control

| Field | Value |
|---|---|
| Version | v1.0 |
| Companion | `TEST_BED_AND_CASES.md` (technical build/execution recipe), `TEST_STRATEGY.md` (overall test plan) |
| Purpose | Plain-English readability for non-technical reviewers (recruiters, hiring managers, interviewers) |
| Terminology note | "OneDrive AI Agent" used throughout, in full, to avoid ambiguity with contact-centre or logistics "agent" roles |
| Covers | All 19 test cases: GB-01 to GB-06 (6), RB-01 to RB-13 (13) |
