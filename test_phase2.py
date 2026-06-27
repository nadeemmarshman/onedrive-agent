"""
Phase 2 tests: unit tests, then integration tests.

Standing testing structure for this project (see handoff doc):
whenever new functions are added in a phase, they get tested in two
ordered layers:

  LAYER 1 -- UNIT TESTS
    Each function tested in isolation, including edge cases. Proves
    each piece works correctly on its own, independent of how it's
    wired together with anything else.

  LAYER 2 -- INTEGRATION TESTS
    Functions tested chained together, with data flowing from one
    into the next exactly as it will in the real agent loop (Phase 3
    onward). Proves the pieces work correctly TOGETHER, not just
    individually -- this is where contract-shape mismatches and
    "forgot to handle the previous step's output format" bugs surface.

Unit tests always run first and must all pass before integration
tests are considered meaningful -- if a unit test fails, an
integration failure built on top of it tells you nothing extra.

This suite will grow as each phase adds new functions: Phase 3's
decision loop, Phase 4's multi-step execution, and Phase 5's approval
gate will each add their own unit tests, then their own integration
tests layered on top of the prior phases' chain.

Still no API calls / no AI involved in this phase -- this is local
validation only.
"""

import inspect
import json
import os
import tempfile

from tools import scan_folder, find_duplicates, find_convertible_files, propose_action
from tool_contracts import TOOL_CONTRACTS


FUNCTION_MAP = {
    "scan_folder": scan_folder,
    "find_duplicates": find_duplicates,
    "find_convertible_files": find_convertible_files,
    "propose_action": propose_action,
}


# =============================================================================
# LAYER 1: UNIT TESTS -- each function tested in isolation, including edge cases
# =============================================================================

def test_unit_scan_folder_finds_all_files():
    """scan_folder should find every file in the sample folder, recursively."""
    files = scan_folder("sample_data", recursive=True)
    assert len(files) == 6, f"Expected 6 files, got {len(files)}"
    print(f"PASS: scan_folder found all {len(files)} files recursively")


def test_unit_scan_folder_non_recursive():
    """scan_folder with recursive=False should skip nested subfolders."""
    files = scan_folder("sample_data", recursive=False)
    nested_files = [f for f in files if "subfolder" in f["path"]]
    assert len(nested_files) == 0, "Non-recursive scan should not find files inside subfolder/"
    assert len(files) == 4, f"Expected 4 top-level files, got {len(files)}"
    print(f"PASS: scan_folder(recursive=False) correctly skipped nested files ({len(files)} top-level)")


def test_unit_scan_folder_missing_path_raises():
    """scan_folder should raise a clear error for a folder that doesn't exist (edge case)."""
    try:
        scan_folder("this_folder_does_not_exist", recursive=True)
        assert False, "Expected FileNotFoundError, but no error was raised"
    except FileNotFoundError:
        print("PASS: scan_folder raises FileNotFoundError for a missing folder")


def test_unit_scan_folder_empty_folder():
    """scan_folder on a genuinely empty folder should return an empty list, not error (edge case)."""
    with tempfile.TemporaryDirectory() as empty_dir:
        files = scan_folder(empty_dir, recursive=True)
        assert files == [], f"Expected empty list for an empty folder, got {files}"
        print("PASS: scan_folder returns an empty list for an empty folder")


def test_unit_find_duplicates_detects_true_duplicate():
    """find_duplicates should group files with identical content together."""
    files = scan_folder("sample_data", recursive=True)
    groups = find_duplicates(files)
    assert len(groups) == 1, f"Expected exactly 1 duplicate group, got {len(groups)}"
    assert len(groups[0]) == 3, f"Expected the group to contain 3 files, got {len(groups[0])}"
    print("PASS: find_duplicates correctly grouped the 3 identical files")


def test_unit_find_duplicates_ignores_near_miss():
    """
    Edge case: a file with a very similar name but DIFFERENT content
    (original_notes_v2.txt) must NOT be included in any duplicate group.
    This is the core proof that content-hash beats filename matching.
    """
    files = scan_folder("sample_data", recursive=True)
    groups = find_duplicates(files)
    all_grouped_paths = [f["path"] for group in groups for f in group]
    near_miss_path = "sample_data/original_notes_v2.txt"
    assert near_miss_path not in all_grouped_paths, (
        "Near-miss file with different content was incorrectly flagged as a duplicate"
    )
    print("PASS: find_duplicates correctly ignored the same-name/different-content near-miss")


def test_unit_find_duplicates_empty_input():
    """Edge case: find_duplicates on an empty file list should return an empty list, not error."""
    groups = find_duplicates([])
    assert groups == [], f"Expected empty list for empty input, got {groups}"
    print("PASS: find_duplicates handles empty input without error")


def test_unit_find_duplicates_no_duplicates_present():
    """Edge case: a set of all-unique files should produce zero duplicate groups."""
    files = scan_folder("sample_data", recursive=False)
    # Top-level only includes the unique files plus the original (no copies)
    unique_only = [f for f in files if f["name"] != "original_notes.txt"]
    groups = find_duplicates(unique_only)
    assert groups == [], f"Expected no duplicate groups among unique files, got {groups}"
    print("PASS: find_duplicates returns no groups when no duplicates exist")


def test_unit_find_convertible_files_flags_bmp():
    """find_convertible_files should flag the .bmp file and suggest .png."""
    files = scan_folder("sample_data", recursive=True)
    convertible = find_convertible_files(files)
    assert len(convertible) == 1, f"Expected 1 convertible file, got {len(convertible)}"
    assert convertible[0]["current_extension"] == ".bmp"
    assert convertible[0]["suggested_extension"] == ".png"
    print("PASS: find_convertible_files correctly flagged the .bmp file")


def test_unit_find_convertible_files_ignores_unlisted_extensions():
    """Edge case: .txt and .docx are not in CONVERTIBLE_FORMATS and must not be flagged."""
    files = scan_folder("sample_data", recursive=True)
    convertible = find_convertible_files(files)
    flagged_extensions = {c["current_extension"] for c in convertible}
    assert ".txt" not in flagged_extensions
    assert ".docx" not in flagged_extensions
    print("PASS: find_convertible_files correctly ignored non-convertible extensions")


def test_unit_find_convertible_files_empty_input():
    """Edge case: find_convertible_files on an empty list should return an empty list."""
    result = find_convertible_files([])
    assert result == [], f"Expected empty list for empty input, got {result}"
    print("PASS: find_convertible_files handles empty input without error")


def test_unit_propose_action_keeps_one_file_per_group():
    """
    For a duplicate group of N files, propose_action should propose
    deleting exactly N-1 of them (keeping one as the "original").
    """
    fake_group = [
        {"path": "a.txt", "size_bytes": 10},
        {"path": "b.txt", "size_bytes": 10},
        {"path": "c.txt", "size_bytes": 10},
    ]
    proposals = propose_action([fake_group], [])
    delete_proposals = [p for p in proposals if p["action_type"] == "delete_duplicate"]
    assert len(delete_proposals) == 2, f"Expected 2 delete proposals for a 3-file group, got {len(delete_proposals)}"
    deleted_paths = {p["target_path"] for p in delete_proposals}
    assert "a.txt" not in deleted_paths, "The first file in the group should be kept, not proposed for deletion"
    print("PASS: propose_action keeps one file per duplicate group and proposes deleting the rest")


def test_unit_propose_action_empty_inputs():
    """Edge case: no duplicates and no convertible files should yield zero proposals."""
    proposals = propose_action([], [])
    assert proposals == [], f"Expected no proposals for empty inputs, got {proposals}"
    print("PASS: propose_action returns no proposals when there is nothing to act on")


def test_unit_propose_action_never_modifies_filesystem():
    """
    Edge case / safety check: propose_action must be a pure function --
    it must not import or call any file-deletion or file-writing logic.
    This guards the Phase 5 approval-gate boundary.
    """
    source = inspect.getsource(propose_action)
    forbidden_calls = ["os.remove", "os.unlink", "shutil.move", "shutil.rmtree", ".write(", "open("]
    for forbidden in forbidden_calls:
        assert forbidden not in source, f"propose_action source unexpectedly contains '{forbidden}'"
    print("PASS: propose_action contains no filesystem-modifying calls (safe for the future approval gate)")


UNIT_TESTS = [
    test_unit_scan_folder_finds_all_files,
    test_unit_scan_folder_non_recursive,
    test_unit_scan_folder_missing_path_raises,
    test_unit_scan_folder_empty_folder,
    test_unit_find_duplicates_detects_true_duplicate,
    test_unit_find_duplicates_ignores_near_miss,
    test_unit_find_duplicates_empty_input,
    test_unit_find_duplicates_no_duplicates_present,
    test_unit_find_convertible_files_flags_bmp,
    test_unit_find_convertible_files_ignores_unlisted_extensions,
    test_unit_find_convertible_files_empty_input,
    test_unit_propose_action_keeps_one_file_per_group,
    test_unit_propose_action_empty_inputs,
    test_unit_propose_action_never_modifies_filesystem,
]


# =============================================================================
# LAYER 2: INTEGRATION TESTS -- contract validation + the full chained flow
# =============================================================================

def test_integration_schema_is_valid_json():
    """Every contract must be valid, serializable JSON (this is what gets sent to the API)."""
    json.dumps(TOOL_CONTRACTS)
    print("PASS: all contracts serialize to valid JSON")


def test_integration_contract_names_match_functions():
    """Every contract name must correspond to a real function, and vice versa."""
    contract_names = {c["name"] for c in TOOL_CONTRACTS}
    function_names = set(FUNCTION_MAP.keys())

    missing_functions = contract_names - function_names
    missing_contracts = function_names - contract_names

    assert not missing_functions, f"Contracts reference unknown functions: {missing_functions}"
    assert not missing_contracts, f"Functions have no contract: {missing_contracts}"
    print("PASS: all contract names match real functions (4/4)")


def test_integration_required_fields_match_function_signature():
    """
    For each contract, every parameter the real Python function requires
    (no default value) must be marked "required" in the schema -- and
    the schema shouldn't claim a parameter is required if the function
    actually has a default for it.
    """
    for contract in TOOL_CONTRACTS:
        name = contract["name"]
        func = FUNCTION_MAP[name]
        sig = inspect.signature(func)

        actual_required = {
            param.name
            for param in sig.parameters.values()
            if param.default is inspect.Parameter.empty
        }
        schema_required = set(contract["input_schema"].get("required", []))

        assert actual_required == schema_required, (
            f"{name}: function requires {actual_required}, "
            f"but schema marks {schema_required} as required"
        )
        print(f"PASS: {name} required fields match function signature {sorted(actual_required)}")


def test_integration_full_chain():
    """
    Simulate the real Phase 3 flow: Claude calls scan_folder, gets a
    result, calls find_duplicates and find_convertible_files with that
    result, then calls propose_action with both outputs.

    Arguments are passed as plain dicts/lists -- the same shape an API
    tool_use response would produce -- not as native Python objects
    constructed by hand, to prove the contract's input_schema shape
    actually lines up with what the function expects.
    """
    scan_args = {"path": "sample_data", "recursive": True}
    files = scan_folder(**scan_args)
    assert len(files) > 0, "Expected scan_folder to find sample files"
    print(f"PASS: scan_folder returned {len(files)} files")

    dup_args = {"files": files}
    duplicate_groups = find_duplicates(**dup_args)
    assert len(duplicate_groups) == 1, f"Expected 1 duplicate group, got {len(duplicate_groups)}"
    assert len(duplicate_groups[0]) == 3, "Expected the duplicate group to contain 3 files"
    print(f"PASS: find_duplicates found {len(duplicate_groups)} group(s) of duplicates")

    conv_args = {"files": files}
    convertible_files = find_convertible_files(**conv_args)
    assert len(convertible_files) == 1, f"Expected 1 convertible file, got {len(convertible_files)}"
    assert convertible_files[0]["current_extension"] == ".bmp"
    print(f"PASS: find_convertible_files found {len(convertible_files)} convertible file(s)")

    proposal_args = {
        "duplicate_groups": duplicate_groups,
        "convertible_files": convertible_files,
    }
    proposals = propose_action(**proposal_args)
    assert len(proposals) == 3, f"Expected 3 proposals (2 deletes + 1 convert), got {len(proposals)}"

    action_types = [p["action_type"] for p in proposals]
    assert action_types.count("delete_duplicate") == 2
    assert action_types.count("convert_format") == 1
    print(f"PASS: propose_action produced {len(proposals)} correct proposal(s)")

    print("Full chain confirmed: scan_folder -> find_duplicates + find_convertible_files -> propose_action")


INTEGRATION_TESTS = [
    test_integration_schema_is_valid_json,
    test_integration_contract_names_match_functions,
    test_integration_required_fields_match_function_signature,
    test_integration_full_chain,
]


# =============================================================================
# Test runner -- unit tests always run first; integration tests only run
# (and are only meaningful) if every unit test passed.
# =============================================================================

def _run_layer(layer_name, tests):
    print("\n" + "=" * 60)
    print(layer_name)
    print("=" * 60)

    failures = []
    for test in tests:
        print(f"\n--- {test.__name__} ---")
        try:
            test()
        except AssertionError as e:
            failures.append((test.__name__, str(e)))
            print(f"FAIL: {e}")
    return failures


def run_all_tests():
    print("#" * 60)
    print("# PHASE 2 TEST SUITE")
    print("# Layer 1: Unit tests -> Layer 2: Integration tests")
    print("#" * 60)

    unit_failures = _run_layer(f"LAYER 1: UNIT TESTS ({len(UNIT_TESTS)} tests)", UNIT_TESTS)

    if unit_failures:
        print("\n" + "#" * 60)
        print(f"UNIT TESTS FAILED ({len(unit_failures)}) -- skipping integration tests")
        print("Integration results would not be meaningful until unit tests pass.")
        for name, msg in unit_failures:
            print(f"  - {name}: {msg}")
        print("#" * 60)
        return

    integration_failures = _run_layer(
        f"LAYER 2: INTEGRATION TESTS ({len(INTEGRATION_TESTS)} tests)", INTEGRATION_TESTS
    )

    print("\n" + "#" * 60)
    total_tests = len(UNIT_TESTS) + len(INTEGRATION_TESTS)
    total_failures = len(unit_failures) + len(integration_failures)
    if total_failures:
        print(f"RESULT: {total_failures}/{total_tests} test(s) failed")
        for name, msg in integration_failures:
            print(f"  - {name}: {msg}")
    else:
        print(f"RESULT: all {total_tests} tests passed ({len(UNIT_TESTS)} unit + {len(INTEGRATION_TESTS)} integration)")
    print("#" * 60)


if __name__ == "__main__":
    run_all_tests()
