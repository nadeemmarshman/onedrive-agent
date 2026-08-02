# DocFolderBackup — 58 unique files, review queue

Source: `DOCFOLDERBACKUP_DELTA.json`. These 58 files exist **only** inside
`DocFolderBackup` — no byte-identical copy anywhere else in `1. Documents`.
Everything else in that folder (1,118 files, 2.5 GB) is a confirmed
duplicate of something in the live tree and is a safe wholesale-discard
candidate. These 58 (496.5 MB) are not -- deleting `DocFolderBackup`
outright would lose them permanently.

Nothing has been moved or deleted. For each row, decide: **Keep**
(relocate into the live tree, tell me where) or **Discard** (confirm and
I'll quarantine it, same reversible move-not-delete pattern as the other
live-run phases).

Paths below are relative to `DocFolderBackup\Documents\` unless noted.

---

> **Detail removed before publication.** Everything below this point was a
> per-file listing of real personal paths (employment dispute, licence,
> identity, medical and third-party records). The aggregate findings above
> carry the analytical content; the detail carried only disclosure. The
> unredacted version is retained locally and is not in this repository.
> See `sanitize_repo_artifacts.py` for the rationale and method.
