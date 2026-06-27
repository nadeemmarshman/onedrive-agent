"""
Phase 2: JSON-schema tool contracts for the Phase 1 functions.

These contracts don't contain any logic themselves -- they describe,
in the standard format used by the Anthropic API (and MCP), what each
tool in tools.py is called, what it does, and what arguments it expects.

In Phase 3, these get handed to Claude alongside a goal. Claude reads
these descriptions and decides which tool to call and with what
arguments -- it never sees the actual Python code, only this contract.

No API calls happen in this phase -- this is pure schema/design work.
"""

TOOL_CONTRACTS = [
    {
        "name": "scan_folder",
        "description": (
            "Scans a folder and returns metadata (path, name, size, extension) "
            "for every file found. Can optionally recurse into subfolders. "
            "This is typically the first tool called, since its output feeds "
            "into find_duplicates and find_convertible_files."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The folder path to scan, e.g. 'sample_data'."
                },
                "recursive": {
                    "type": "boolean",
                    "description": (
                        "If true, scan subfolders too. If false, only scan the "
                        "top-level folder. Defaults to true."
                    )
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "find_duplicates",
        "description": (
            "Given a list of files (as returned by scan_folder), finds groups "
            "of files that have identical content, regardless of filename. "
            "Uses content hashing, not filename matching, so it correctly "
            "catches renamed duplicates and avoids falsely flagging different "
            "files that happen to share a name."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "description": "A list of file metadata dicts, as returned by scan_folder.",
                    "items": {"type": "object"}
                }
            },
            "required": ["files"]
        }
    },
    {
        "name": "find_convertible_files",
        "description": (
            "Given a list of files (as returned by scan_folder), flags files "
            "whose format is old or bloated and has a more modern, efficient "
            "equivalent (e.g. .bmp -> .png, .doc -> .docx)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "description": "A list of file metadata dicts, as returned by scan_folder.",
                    "items": {"type": "object"}
                }
            },
            "required": ["files"]
        }
    },
    {
        "name": "propose_action",
        "description": (
            "Given duplicate file groups and convertible file candidates, "
            "produces a structured list of proposed clean-up actions "
            "(delete_duplicate, convert_format). This tool never deletes or "
            "modifies any file itself -- it only proposes actions, which "
            "require separate human approval before being carried out "
            "(approval gate is built in Phase 5)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "duplicate_groups": {
                    "type": "array",
                    "description": "Groups of duplicate files, as returned by find_duplicates.",
                    "items": {
                        "type": "array",
                        "items": {"type": "object"}
                    }
                },
                "convertible_files": {
                    "type": "array",
                    "description": "Convertible file candidates, as returned by find_convertible_files.",
                    "items": {"type": "object"}
                }
            },
            "required": ["duplicate_groups", "convertible_files"]
        }
    }
]


if __name__ == "__main__":
    import json
    # Quick sanity check: print the contracts as they'd be sent to the API
    print(json.dumps(TOOL_CONTRACTS, indent=2))
