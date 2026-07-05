"""
test_phase8_pre_pilot.py
========================

Pre-Phase-8 (UAT/Pilot) Definition-of-Ready gate.

Adds the tests identified by the on-paper test-design pass in
TEST_STRATEGY.md. All of these must be committed and green before any
Phase 8 run against real OneDrive data.

  Gap G1 -- Loop termination (agent_loop.run_agent_loop)
      run_agent_loop has real termination logic: a natural stop when the
      model stops calling tools, and a MAX_ITERATIONS safety cap. Until
      now both were proven only by the one-time Phase 4 live run -- no
      committed test exercised either path.

  RAID I5 class -- Fixture integrity
      Issue I5 was a recurring, self-inflicted bug: a Phase 5 test deleted
      the real sample_data/ fixtures on every run. It was fixed once and
      verified manually. This guard makes that verification permanent and
      automatic -- it runs the full Phase 3/4/4.5/5 suite in an isolated
      subprocess and asserts sample_data/ is byte-for-byte unchanged after.
      Any future test that mutates the real fixtures will fail this guard.

Style mirrors test_phase2.py / test_phase3_4_45.py: plain functions using
assert, a two-layer runner (unit first; integration only if unit passes),
no pytest dependency. The Anthropic client is always mocked -- no API key
or network call is ever made.

Run:  python test_phase8_pre_pilot.py
"""

import hashlib
import subprocess
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parent
SAMPLE_DATA = REPO_ROOT / "sample_data"

# Import agent_loop. anthropic is installed on the real machine; on a bare
# machine we register a minimal stub first so this file still runs (its
# error classes are only referenced by except-branches we never trigger,
# because the mocked client RETURNS a response rather than raising).
try:
    import anthropic  # noqa: F401
except ModuleNotFoundError:
    _stub = types.ModuleType("anthropic")
    for _name in ("AuthenticationError", "RateLimitError", "APIConnectionError"):
        setattr(_stub, _name, type(_name, (Exception,), {}))
    _stub.APIStatusError = type("APIStatusError", (Exception,), {})
    _stub.Anthropic = type("Anthropic", (), {"__init__": lambda self, *a, **k: None})
    sys.modules["anthropic"] = _stub

import agent_loop  # noqa: E402
from agent_loop import MAX_ITERATIONS  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _text_turn(text="Summary: nothing further to propose."):
    """A model turn with only a text block -> should trigger the natural stop."""
    return types.SimpleNamespace(
        content=[types.SimpleNamespace(type="text", text=text)]
    )


def _tool_turn(name="find_duplicates", tool_input=None, call_id="tu_1"):
    """A model turn that always requests a tool -> never stops on its own."""
    return types.SimpleNamespace(
        content=[types.SimpleNamespace(
            type="tool_use", name=name,
            input={"files": []} if tool_input is None else tool_input,
            id=call_id,
        )]
    )


def _hash_tree(root):
    """Return {relative_path: md5_hex} for every file under root."""
    manifest = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            manifest[str(path.relative_to(root))] = hashlib.md5(path.read_bytes()).hexdigest()
    return manifest


def _diff(before, after):
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    changed = sorted(k for k in before.keys() & after.keys() if before[k] != after[k])
    return f"added={added}, removed={removed}, changed={changed}"


# ===========================================================================
# LAYER 1: UNIT TESTS  (loop termination -- Gap G1)
# ===========================================================================
def test_unit_loop_natural_stop_on_zero_tool_calls():
    """[G1 POSITIVE] No tool calls in a turn => loop stops after exactly one API call."""
    client = MagicMock()
    client.messages.create.return_value = _text_turn()
    with patch("agent_loop.get_client", return_value=client), \
         patch("agent_loop.scan_folder", return_value=[]):
        agent_loop.run_agent_loop(goal="natural-stop test", starting_folder="unused")
    calls = client.messages.create.call_count
    assert calls == 1, f"natural stop should call the model exactly once, got {calls}"
    print("PASS: loop stops naturally on a zero-tool-call turn (1 API call, no safety cap)")


def test_unit_loop_stops_at_max_iterations_safety_cap():
    """[G1 NEGATIVE] Model never stops requesting tools => loop stops at exactly MAX_ITERATIONS."""
    client = MagicMock()
    client.messages.create.return_value = _tool_turn()
    with patch("agent_loop.get_client", return_value=client), \
         patch("agent_loop.scan_folder", return_value=[]), \
         patch("agent_loop.execute_tool_call", return_value={"result": []}):
        agent_loop.run_agent_loop(goal="safety-cap test", starting_folder="unused")
    calls = client.messages.create.call_count
    assert calls == MAX_ITERATIONS, (
        f"safety cap should stop at exactly MAX_ITERATIONS ({MAX_ITERATIONS}) API calls, got {calls}"
    )
    print(f"PASS: loop halts at the MAX_ITERATIONS safety cap ({MAX_ITERATIONS} calls) when tools never stop")


def test_unit_loop_no_tool_execution_after_natural_stop():
    """[G1 ORDERING] On a zero-tool-call turn, no tool may be executed before returning."""
    client = MagicMock()
    client.messages.create.return_value = _text_turn()
    with patch("agent_loop.get_client", return_value=client), \
         patch("agent_loop.scan_folder", return_value=[]), \
         patch("agent_loop.execute_tool_call") as mock_exec:
        agent_loop.run_agent_loop(goal="ordering test", starting_folder="unused")
    assert mock_exec.call_count == 0, (
        f"no tool should execute on a natural-stop turn, got {mock_exec.call_count}"
    )
    print("PASS: no tool executes on a natural-stop turn (correct ordering)")


# ===========================================================================
# LAYER 2: INTEGRATION TEST  (fixture integrity -- RAID I5 class)
# ===========================================================================
def test_integration_fixture_integrity_after_full_suite():
    """
    [RAID I5 class] Run the full Phase 3/4/4.5/5 suite in an isolated
    subprocess and assert sample_data/ is byte-for-byte identical after.
    Fails if any test mutates the real fixtures.
    """
    assert SAMPLE_DATA.is_dir(), f"sample_data/ not found at {SAMPLE_DATA}"
    before = _hash_tree(SAMPLE_DATA)
    assert before, "sample_data/ appears empty -- nothing to protect"

    proc = subprocess.run(
        [sys.executable, "test_phase3_4_45.py"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    after = _hash_tree(SAMPLE_DATA)
    assert before == after, (
        "sample_data/ fixtures changed while running the full suite -- a test is "
        "mutating the real fixtures (RAID I5 class). "
        f"{_diff(before, after)}\n--- suite stdout tail ---\n{proc.stdout[-600:]}"
    )
    print(f"PASS: all {len(after)} fixture files byte-identical before/after the full suite")


# ===========================================================================
# RUNNER (two-layer: unit first, integration only if unit passes)
# ===========================================================================
UNIT_TESTS = [
    test_unit_loop_natural_stop_on_zero_tool_calls,
    test_unit_loop_stops_at_max_iterations_safety_cap,
    test_unit_loop_no_tool_execution_after_natural_stop,
]
INTEGRATION_TESTS = [
    test_integration_fixture_integrity_after_full_suite,
]


def _run_layer(label, tests):
    print(f"\n{'=' * 60}\n{label}\n{'=' * 60}")
    failures = []
    for test in tests:
        try:
            test()
        except AssertionError as e:
            failures.append((test.__name__, str(e)))
            print(f"FAIL: {test.__name__}: {e}")
        except Exception as e:
            failures.append((test.__name__, f"{type(e).__name__}: {e}"))
            print(f"ERROR: {test.__name__}: {type(e).__name__}: {e}")
    return failures


def run_all_tests():
    print("#" * 60)
    print("# PHASE 8 PRE-PILOT DEFINITION-OF-READY GATE")
    print(f"# {len(UNIT_TESTS)} unit + {len(INTEGRATION_TESTS)} integration")
    print("#" * 60)
    unit_failures = _run_layer(f"LAYER 1: UNIT TESTS ({len(UNIT_TESTS)} tests)", UNIT_TESTS)
    if unit_failures:
        print(f"\n{'#' * 60}\nUNIT TESTS FAILED ({len(unit_failures)}) -- skipping integration")
        for name, msg in unit_failures:
            print(f"  - {name}: {msg}")
        print("#" * 60)
        sys.exit(1)
    integration_failures = _run_layer(
        f"LAYER 2: INTEGRATION TESTS ({len(INTEGRATION_TESTS)} tests)", INTEGRATION_TESTS
    )
    total = len(UNIT_TESTS) + len(INTEGRATION_TESTS)
    print(f"\n{'#' * 60}")
    if integration_failures:
        print(f"RESULT: {len(integration_failures)}/{total} test(s) failed")
        for name, msg in integration_failures:
            print(f"  - {name}: {msg}")
        print("#" * 60)
        sys.exit(1)
    print(f"RESULT: all {total} tests passed ({len(UNIT_TESTS)} unit + {len(INTEGRATION_TESTS)} integration)")
    print("#" * 60)


if __name__ == "__main__":
    run_all_tests()
