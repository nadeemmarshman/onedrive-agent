"""
Phase 1: Plain Python tool functions (no AI/LLM involved yet).

These are the building blocks the agent will later call. Each function
has a clear, single responsibility and a well-defined input/output
contract -- this matters because in Phase 2 we wrap each one in a
JSON-schema "tool contract" that an LLM can read and decide to invoke.

Design decisions locked in (see handoff doc Decision log):
- scan_folder() recurses by default, but it's a toggle (recursive=True)
- Duplicate detection uses content hashing (MD5), not filename matching
- Built and tested against a disposable sample folder, not real OneDrive,
  until the human-approval gate (Phase 5) exists
"""

import os
import hashlib
from pathlib import Path


# Extensions we consider "old/bloated" and worth flagging for conversion.
# Kept as a simple mapping: old extension -> suggested modern replacement.
CONVERTIBLE_FORMATS = {
    ".bmp": ".png",
    ".doc": ".docx",
    ".xls": ".xlsx",
    ".ppt": ".pptx",
    ".tif": ".png",
    ".tiff": ".png",
}


def scan_folder(path: str, recursive: bool = True) -> list[dict]:
    """
    Walk a folder and return metadata for every file found.

    Args:
        path: folder to scan
        recursive: if True, descend into subfolders; if False, top-level only

    Returns:
        A list of dicts, one per file, each with:
            path: full file path (str)
            name: filename only (str)
            size_bytes: file size in bytes (int)
            extension: lowercase file extension, including the dot (str)
    """
    root = Path(path)
    if not root.exists():
        raise FileNotFoundError(f"Folder not found: {path}")

    results = []

    if recursive:
        walker = root.rglob("*")
    else:
        walker = root.glob("*")

    for entry in walker:
        if entry.is_file():
            results.append({
                "path": str(entry),
                "name": entry.name,
                "size_bytes": entry.stat().st_size,
                "extension": entry.suffix.lower(),
            })

    return results


def _hash_file(path: str, chunk_size: int = 8192) -> str:
    """
    Compute an MD5 hash of a file's content, reading in chunks so large
    files don't need to be loaded fully into memory.

    Not a security use case -- this is purely for duplicate detection,
    so MD5's speed is the right trade-off over a slower, cryptographically
    stronger hash.
    """
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def find_duplicates(files: list[dict]) -> list[list[dict]]:
    """
    Group files by content hash to find true duplicates -- catches
    renamed copies, and avoids false-flagging different files that
    happen to share a name.

    Args:
        files: output of scan_folder()

    Returns:
        A list of duplicate groups. Each group is a list of file dicts
        (from the input) that share identical content. Only groups with
        2+ files are included (unique files are omitted).
    """
    hash_map: dict[str, list[dict]] = {}

    for file_info in files:
        try:
            file_hash = _hash_file(file_info["path"])
        except (OSError, PermissionError):
            # Skip files we can't read (e.g. locked, or an
            # OneDrive "online-only" placeholder not yet downloaded)
            continue

        hash_map.setdefault(file_hash, []).append(file_info)

    duplicate_groups = [group for group in hash_map.values() if len(group) > 1]
    return duplicate_groups


def find_convertible_files(files: list[dict]) -> list[dict]:
    """
    Flag files whose extension matches a known "old/bloated format"
    that has a more modern, efficient equivalent.

    Args:
        files: output of scan_folder()

    Returns:
        A list of dicts, one per convertible file found, each with:
            path, name, current_extension, suggested_extension
    """
    candidates = []

    for file_info in files:
        ext = file_info["extension"]
        if ext in CONVERTIBLE_FORMATS:
            candidates.append({
                "path": file_info["path"],
                "name": file_info["name"],
                "current_extension": ext,
                "suggested_extension": CONVERTIBLE_FORMATS[ext],
            })

    return candidates


def propose_action(duplicate_groups: list[list[dict]], convertible_files: list[dict]) -> list[dict]:
    """
    Turn raw findings into structured, human-readable proposed actions.
    This is deliberately the hand-off point to the future human-approval
    gate (Phase 5) -- nothing in Phase 1-4 should delete or convert a
    file directly; everything routes through a proposal first.

    Args:
        duplicate_groups: output of find_duplicates()
        convertible_files: output of find_convertible_files()

    Returns:
        A list of proposed-action dicts, each with:
            action_type: "delete_duplicate" or "convert_format"
            target_path: the file the action would apply to
            reason: human-readable explanation
            details: supporting info (e.g. which file it duplicates)
    """
    proposals = []

    for group in duplicate_groups:
        # Keep the first file as the "original", propose deleting the rest
        keeper = group[0]
        for duplicate in group[1:]:
            proposals.append({
                "action_type": "delete_duplicate",
                "target_path": duplicate["path"],
                "reason": f"Identical content to '{keeper['path']}'",
                "details": {
                    "keeper_path": keeper["path"],
                    "duplicate_path": duplicate["path"],
                    "size_bytes": duplicate["size_bytes"],
                },
            })

    for candidate in convertible_files:
        proposals.append({
            "action_type": "convert_format",
            "target_path": candidate["path"],
            "reason": (
                f"'{candidate['current_extension']}' is an older/bloated format; "
                f"suggest converting to '{candidate['suggested_extension']}'"
            ),
            "details": {
                "current_extension": candidate["current_extension"],
                "suggested_extension": candidate["suggested_extension"],
            },
        })

    return proposals


if __name__ == "__main__":
    # Quick manual smoke test against the sample folder
    SAMPLE_FOLDER = "sample_data"

    files = scan_folder(SAMPLE_FOLDER, recursive=True)
    print(f"Scanned {len(files)} files:")
    for f in files:
        print(f"  {f['path']} ({f['size_bytes']} bytes)")

    dup_groups = find_duplicates(files)
    print(f"\nFound {len(dup_groups)} duplicate group(s):")
    for group in dup_groups:
        print("  Group:", [f["path"] for f in group])

    convertible = find_convertible_files(files)
    print(f"\nFound {len(convertible)} convertible file(s):")
    for c in convertible:
        print(f"  {c['path']}: {c['current_extension']} -> {c['suggested_extension']}")

    proposals = propose_action(dup_groups, convertible)
    print(f"\nProposed {len(proposals)} action(s):")
    for p in proposals:
        print(f"  [{p['action_type']}] {p['target_path']} -- {p['reason']}")
