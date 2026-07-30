"""
Live run: byte-for-byte duplicate detection against a real OneDrive folder.

Uses the existing Phase 1 tools (scan_folder, find_duplicates) unmodified --
this exercise validates the original build against real, messy data rather
than the disposable sample_data/ fixture. Read-only: no files are moved,
renamed, or deleted. Per the project's approval-gate design, any deletion
would require a separate, explicitly-approved action.

Output paths are trimmed to filenames only in the printed report to avoid
committing a full local directory listing to a public repo.
"""

import sys
from datetime import datetime, timezone

from tools import scan_folder, find_duplicates

TARGET_FOLDER = r"C:\Users\Nadeem\OneDrive\Pictures\Camera Roll"


def run(folder: str = TARGET_FOLDER) -> str:
    files = scan_folder(folder, recursive=True)
    duplicate_groups = find_duplicates(files)

    total_dupe_files = sum(len(g) - 1 for g in duplicate_groups)
    total_dupe_bytes = sum(
        sum(f["size_bytes"] for f in g[1:]) for g in duplicate_groups
    )

    lines = [
        f"# Live run report -- {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "",
        "Target: OneDrive\\Pictures\\Camera Roll (path redacted to filename level below)",
        f"Files scanned: {len(files)}",
        f"Duplicate groups (identical content, MD5): {len(duplicate_groups)}",
        f"Redundant files: {total_dupe_files}",
        f"Reclaimable space: {total_dupe_bytes / 1024 / 1024:.1f} MB",
        "",
        "## Groups",
    ]
    for group in duplicate_groups:
        names = [f["name"] for f in group]
        lines.append(f"- {names}")

    report = "\n".join(lines) + "\n"
    return report


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else TARGET_FOLDER
    print(run(folder))
