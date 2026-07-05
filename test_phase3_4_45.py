"""
Pre-Phase-5 quality gate: negative/red-line test suite for Phases 3, 4, and 4.5.

This suite is a condition of the Definition of Done for Phase 4.5 --
it must pass before Phase 5 (the human-approval gate) is built.
Per GRC best practice, this is quality assurance on capabilities already
built (a quality control), not a new delivery phase.

TWO-LAYER STRUCTURE (standing rule):
  Layer 1 -- UNIT TESTS: each function tested in isolation, including
             realistic negative/red-line cases (the primary focus here,
             since happy-path unit tests already exist in test_phase2.py)
  Layer 2 -- INTEGRATION TESTS: functions tested chained together,
             with data flowing as it will in the real agent loop.

NEGATIVE/RED-LINE FOCUS:
  The existing test_phase2.py covers happy-path and edge cases for
  Phases 1-2. This suite explicitly targets failure boundaries --
  the scenarios where things go wrong -- to verify that every failure
  mode fails gracefully, loudly, and with the right message, rather
  than silently, cryptically, or catastrophically.

NO LIVE API CALLS: all tests in this suite are fully local. The
  anthropic package is stubbed where needed so tests run without
  an API key, without network access, and without API cost.
"""

import os
os.environ.pop("SENDGRID_API_KEY", None)  # test isolation: the suite must never send real alert emails (RAID I6)

import inspect
import json
import logging
import os
import sys
import tempfile
import types
from pathlib import Path
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# STUB SETUP: fake the anthropic package so tests run without it installed
# or without a live API key. Only the exception classes and type hints
# that our code references at import time need to be present.
# ---------------------------------------------------------------------------

def _build_anthropic_stub():
    fake = types.ModuleType("anthropic")

    class _FakeAPIStatusError(Exception):
        def __init__(self, message="", status_code=400):
            super().__init__(message)
            self.message = message
            self.status_code = status_code

    class _FakeAuthenticationError(Exception): pass
    class _FakeRateLimitError(Exception): pass
    class _FakeAPIConnectionError(Exception): pass

    fake.AuthenticationError   = _FakeAuthenticationError
    fake.RateLimitError        = _FakeRateLimitError
    fake.APIConnectionError    = _FakeAPIConnectionError
    fake.APIStatusError        = _FakeAPIStatusError
    fake.Anthropic             = object

    fake_types = types.ModuleType("anthropic.types")
    fake_types.Message = object
    fake.types = fake_types

    sys.modules["anthropic"]       = fake
    sys.modules["anthropic.types"] = fake_types
    return fake

_anthropic_stub = _build_anthropic_stub()


# Now import our modules -- anthropic is already stubbed in sys.modules
from decision_loop import get_client
from agent_loop import validate_arguments, execute_tool_call, FUNCTION_MAP
import resilience
from resilience import (
    AgentState, VALID_TRANSITIONS,
    transition_to, check_for_resume,
    _masked_user_id, _now_utc,
    alert_auth_failure, alert_rate_limit, alert_connection_failure,
    alert_api_status_error, alert_resume_approval_required,
    alert_corrupted_state_file, alert_sendgrid_failure,
    send_alert, alert_on_error,
    STATE_FILE,
)
import approval_gate
from approval_gate import (
    write_snapshot, present_proposals, execute_approved_actions,
    run_approval_gate, SNAPSHOT_FILE,
)


# ---------------------------------------------------------------------------
# TEST HELPERS
# ---------------------------------------------------------------------------

def _temp_state_file():
    """Return a temporary Path for state file tests -- always cleaned up."""
    return Path(tempfile.mktemp(suffix=".json"))


def _captured_alerts():
    """
    Context manager that intercepts send_alert() calls and captures
    the subject + body without actually sending emails or needing
    a real SENDGRID_API_KEY. Used to assert that alert CONTENT is
    correct for each error type.
    """
    captured = []

    original = resilience.send_alert

    def _capture(subject, body):
        captured.append({"subject": subject, "body": body})

    resilience.send_alert = _capture
    return captured, original


def _restore_send_alert(original):
    resilience.send_alert = original


# ---------------------------------------------------------------------------
# LAYER 1: UNIT TESTS
# ---------------------------------------------------------------------------

# ---- Phase 3: decision_loop.py ----

def test_unit_get_client_missing_key():
    """
    [NEGATIVE] get_client() must raise RuntimeError with an actionable
    message when ANTHROPIC_API_KEY is not set -- not a raw KeyError or
    AttributeError that would confuse the user.
    """
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("ANTHROPIC_API_KEY", None)
        try:
            get_client()
            assert False, "Expected RuntimeError when key is missing"
        except RuntimeError as e:
            assert "ANTHROPIC_API_KEY" in str(e), (
                f"Error message should mention ANTHROPIC_API_KEY, got: {e}"
            )
    print("PASS: get_client() raises RuntimeError with actionable message when key missing")


def test_unit_get_client_with_key():
    """
    [POSITIVE] get_client() must not raise when the key is set.
    We verify the env var is readable and get_client() doesn't raise
    a RuntimeError -- we can't test the returned client's API behaviour
    without a real key, so we catch the stub's TypeError and treat it
    as a pass (the RuntimeError guard passed, which is what matters).
    """
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test-fake-key"}):
        try:
            get_client()
            print("PASS: get_client() succeeds when ANTHROPIC_API_KEY is set")
        except RuntimeError:
            assert False, "get_client() should not raise RuntimeError when key is set"
        except TypeError:
            # The stub's Anthropic class doesn't accept constructor args --
            # this is expected in the test environment. The important thing
            # is that RuntimeError was NOT raised, meaning the key was found.
            print("PASS: get_client() found the key (stub TypeError is expected in test env)")


# ---- Phase 4: agent_loop.py ----

def test_unit_validate_arguments_missing_required():
    """
    [NEGATIVE] validate_arguments() must catch a missing required argument
    and return a descriptive error string, not raise an exception.
    """
    result = validate_arguments("scan_folder", {})
    assert result is not None, "Expected an error string for missing 'path'"
    assert "path" in result.lower(), f"Error should mention 'path', got: {result}"
    print(f"PASS: validate_arguments catches missing required arg: {result}")


def test_unit_validate_arguments_unexpected_arg():
    """
    [NEGATIVE] validate_arguments() must catch an argument that the real
    function doesn't accept -- preventing Claude from passing phantom args.
    """
    result = validate_arguments("find_duplicates", {"files": [], "bogus": True})
    assert result is not None
    assert "bogus" in result.lower(), f"Error should mention 'bogus', got: {result}"
    print(f"PASS: validate_arguments catches unexpected arg: {result}")


def test_unit_validate_arguments_valid_passes():
    """
    [POSITIVE] validate_arguments() must return None when arguments are valid.
    """
    result = validate_arguments("scan_folder", {"path": "sample_data", "recursive": True})
    assert result is None, f"Expected None for valid args, got: {result}"
    print("PASS: validate_arguments returns None for valid args")


def test_unit_validate_arguments_none_value():
    """
    [NEGATIVE] Claude could theoretically return None as an argument value.
    validate_arguments() validates argument NAMES/PRESENCE -- a None value
    for a required arg still satisfies presence, so this tests that the
    function doesn't crash on None values.
    """
    result = validate_arguments("scan_folder", {"path": None})
    assert result is None, (
        "None value for a present required arg should pass name validation "
        "(type checking is the function's own responsibility)"
    )
    print("PASS: validate_arguments handles None argument value without crashing")


def test_unit_execute_tool_call_unrecognised_tool():
    """
    [NEGATIVE] execute_tool_call() must return an error dict for an
    unrecognised tool name, never raise -- so Claude can receive the
    error as an observation and potentially recover.
    """
    result = execute_tool_call("delete_everything", {})
    assert "error" in result, "Expected error dict for unrecognised tool"
    assert "delete_everything" in result["error"]
    assert "result" not in result
    print(f"PASS: execute_tool_call returns error dict for unrecognised tool")


def test_unit_execute_tool_call_malformed_arguments():
    """
    [NEGATIVE] execute_tool_call() must catch validation failure and
    return an error dict, not raise a TypeError from the underlying function.
    """
    result = execute_tool_call("scan_folder", {})  # missing required 'path'
    assert "error" in result
    assert "result" not in result
    print(f"PASS: execute_tool_call returns error dict for malformed arguments")


def test_unit_execute_tool_call_runtime_error_in_tool():
    """
    [NEGATIVE] If the underlying function raises (e.g. folder not found),
    execute_tool_call() must catch it and return an error dict rather than
    letting the exception propagate and crash the agent loop.
    """
    result = execute_tool_call("scan_folder", {"path": "this_does_not_exist_xyz"})
    assert "error" in result
    assert "result" not in result
    print(f"PASS: execute_tool_call catches runtime error from underlying function")


def test_unit_execute_tool_call_valid_execution():
    """
    [POSITIVE] execute_tool_call() with valid args must return a result dict.
    """
    result = execute_tool_call("scan_folder", {"path": "sample_data", "recursive": True})
    assert "result" in result
    assert "error" not in result
    assert len(result["result"]) == 6
    print(f"PASS: execute_tool_call returns result dict for valid execution")


# ---- Phase 4.5: resilience.py -- state machine ----

def test_unit_state_machine_all_states_defined():
    """
    [POSITIVE] All five named states must exist in the AgentState enum.
    """
    expected = {
        "SCANNING", "AWAITING_DECISION", "EXECUTING_TOOL",
        "AWAITING_HUMAN_APPROVAL", "DONE"
    }
    actual = {s.value for s in AgentState}
    assert actual == expected, f"State mismatch: {actual} != {expected}"
    print(f"PASS: All 5 states defined: {sorted(actual)}")


def test_unit_valid_transitions_complete():
    """
    [POSITIVE] Every state must have an entry in VALID_TRANSITIONS.
    A missing state would cause a KeyError at runtime.
    """
    for state in AgentState:
        assert state in VALID_TRANSITIONS, f"State {state} missing from VALID_TRANSITIONS"
    print("PASS: VALID_TRANSITIONS covers all 5 states")


def test_unit_invalid_transition_raises():
    """
    [NEGATIVE] An invalid transition (SCANNING -> DONE) must raise
    ValueError explicitly, not silently corrupt the state.
    """
    tf = _temp_state_file()
    resilience.STATE_FILE = tf
    try:
        transition_to(AgentState.SCANNING, AgentState.DONE, {})
        assert False, "Expected ValueError for invalid transition"
    except ValueError as e:
        assert "SCANNING" in str(e)
        assert "DONE" in str(e)
    finally:
        if tf.exists(): tf.unlink()
    print("PASS: Invalid transition raises ValueError with clear message")


def test_unit_valid_transition_persists_state():
    """
    [POSITIVE] A valid transition must write the new state to disk
    so restart-and-resume can pick it up.
    """
    tf = _temp_state_file()
    resilience.STATE_FILE = tf
    try:
        transition_to(AgentState.SCANNING, AgentState.AWAITING_DECISION, {"files": 6})
        assert tf.exists(), "State file should have been created"
        saved = json.loads(tf.read_text())
        assert saved["state"] == "AWAITING_DECISION"
        assert saved["data"] == {"files": 6}
    finally:
        if tf.exists(): tf.unlink()
    print("PASS: Valid transition persists correct state to disk")


def test_unit_check_for_resume_fresh_run():
    """
    [POSITIVE] check_for_resume() must return (None, {}) when no state
    file exists -- correctly identifying a fresh run.
    """
    tf = _temp_state_file()
    resilience.STATE_FILE = tf
    assert not tf.exists()
    state, data = check_for_resume()
    assert state is None
    assert data == {}
    print("PASS: check_for_resume returns None for fresh run (no state file)")


def test_unit_check_for_resume_corrupted_json():
    """
    [NEGATIVE] check_for_resume() must handle a corrupted state file
    (invalid JSON) gracefully -- return (None, {}) and log the error,
    never raise or crash.
    """
    tf = _temp_state_file()
    resilience.STATE_FILE = tf
    tf.write_text("this is not valid json {{{")
    try:
        state, data = check_for_resume()
        assert state is None, "Corrupted file should result in fresh run"
        assert data == {}
    finally:
        if tf.exists(): tf.unlink()
    print("PASS: check_for_resume handles corrupted JSON gracefully")


def test_unit_check_for_resume_invalid_state_name():
    """
    [NEGATIVE] check_for_resume() must handle a state file containing an
    unrecognised state name -- return (None, {}) and log the error,
    never raise ValueError.
    """
    tf = _temp_state_file()
    resilience.STATE_FILE = tf
    tf.write_text(json.dumps({"state": "MADE_UP_STATE", "data": {}, "timestamp": "now"}))
    try:
        state, data = check_for_resume()
        assert state is None, "Unrecognised state name should result in fresh run"
        assert data == {}
    finally:
        if tf.exists(): tf.unlink()
    print("PASS: check_for_resume handles unrecognised state name gracefully")


def test_unit_check_for_resume_awaiting_human_approval_safety():
    """
    [NEGATIVE / SAFETY-CRITICAL] check_for_resume() must return
    AWAITING_HUMAN_APPROVAL when that state is saved -- never silently
    skip past it. This is the safety guarantee the whole state-machine
    design is built around.
    """
    tf = _temp_state_file()
    resilience.STATE_FILE = tf
    tf.write_text(json.dumps({
        "state": "AWAITING_HUMAN_APPROVAL",
        "data": {"proposals": 3},
        "timestamp": "2026-07-01T00:00:00Z"
    }))
    try:
        state, data = check_for_resume()
        assert state == AgentState.AWAITING_HUMAN_APPROVAL, (
            "AWAITING_HUMAN_APPROVAL must be returned, never skipped"
        )
        assert data == {"proposals": 3}
    finally:
        if tf.exists(): tf.unlink()
    print("PASS: AWAITING_HUMAN_APPROVAL safety guarantee confirmed -- state returned, not skipped")


def test_unit_save_state_disk_write_failure():
    """
    [NEGATIVE] _save_state() must handle a disk write failure gracefully --
    log the error but not raise, since crashing on a state-save failure
    would be worse than continuing without saved state.
    """
    tf = Path("/nonexistent_directory_xyz/agent_state.json")
    resilience.STATE_FILE = tf
    try:
        # Should not raise -- should log ERROR and return quietly
        resilience._save_state(AgentState.SCANNING, {})
        print("PASS: _save_state handles disk write failure without raising")
    except OSError:
        assert False, "_save_state should not raise on disk write failure"
    finally:
        resilience.STATE_FILE = STATE_FILE  # restore


# ---- Phase 4.5: resilience.py -- masked user ID ----

def test_unit_masked_user_id_format():
    """
    [POSITIVE] _masked_user_id() must return a string in the format
    XX****@YY**** -- partial masking applied to both username and hostname.
    """
    with patch.dict(os.environ, {"USERNAME": "Nadeem", "COMPUTERNAME": "DESKTOP-8VDSVKM"}):
        result = _masked_user_id()
        assert "@" in result, "Result should be username@hostname format"
        parts = result.split("@")
        assert len(parts) == 2
        assert parts[0].endswith("****"), f"Username part should end with ****: {parts[0]}"
        assert parts[1].endswith("****"), f"Hostname part should end with ****: {parts[1]}"
        assert parts[0].startswith("Na"), f"Username should show first 2 chars: {parts[0]}"
        assert parts[1].startswith("DE"), f"Hostname should show first 2 chars: {parts[1]}"
    print(f"PASS: _masked_user_id() correctly masks credentials: {result}")


def test_unit_masked_user_id_short_value():
    """
    [NEGATIVE] _masked_user_id() must fully mask values of 2 or fewer
    characters -- showing first 2 chars of a 1-char value would expose it.
    """
    with patch.dict(os.environ, {"USERNAME": "A", "COMPUTERNAME": "AB"}):
        result = _masked_user_id()
        assert "****@****" == result, f"Short values should be fully masked: {result}"
    print(f"PASS: _masked_user_id() fully masks short credential values")


def test_unit_masked_user_id_missing_env_vars():
    """
    [NEGATIVE] _masked_user_id() must handle missing USERNAME/COMPUTERNAME
    env vars without crashing -- falls back to 'unknown'.
    """
    env = os.environ.copy()
    env.pop("USERNAME", None)
    env.pop("COMPUTERNAME", None)
    with patch.dict(os.environ, env, clear=True):
        result = _masked_user_id()
        assert "****" in result, f"Missing env vars should still produce masked output: {result}"
    print(f"PASS: _masked_user_id() handles missing env vars gracefully: {result}")


# ---- Phase 4.5: resilience.py -- alert message content ----

def test_unit_alert_auth_failure_content():
    """
    [NEGATIVE] alert_auth_failure() must produce an alert with the correct
    5W structure and subject line. Asserts against exact field labels so
    the test fails if the message format drifts from the design spec.
    """
    captured, original = _captured_alerts()
    try:
        with patch.dict(os.environ, {"SENDGRID_API_KEY": "fake-key"}):
            alert_auth_failure()
        assert len(captured) == 1
        alert = captured[0]
        assert "Authentication failed" in alert["subject"]
        assert "WHAT:" in alert["body"]
        assert "WHEN:" in alert["body"]
        assert "WHERE:" in alert["body"]
        assert "TRIGGERED BY:" in alert["body"]
        assert "WHY:" in alert["body"]
        assert "STEPS:" in alert["body"]
        assert "ANTHROPIC_API_KEY" in alert["body"]
        assert "echo $env:ANTHROPIC_API_KEY" in alert["body"]
        assert "README" in alert["body"]
    finally:
        _restore_send_alert(original)
    print("PASS: alert_auth_failure() produces correct 5W structure and content")


def test_unit_alert_rate_limit_content():
    """[NEGATIVE] alert_rate_limit() must produce correct 5W content."""
    captured, original = _captured_alerts()
    try:
        with patch.dict(os.environ, {"SENDGRID_API_KEY": "fake-key"}):
            alert_rate_limit()
        assert len(captured) == 1
        alert = captured[0]
        assert "Rate limit" in alert["subject"]
        assert "WHAT:" in alert["body"]
        assert "WHEN:" in alert["body"]
        assert "60 seconds" in alert["body"]
        assert "TRIGGERED BY:" in alert["body"]
        assert "python agent_loop.py" in alert["body"]
        assert "README" in alert["body"]
    finally:
        _restore_send_alert(original)
    print("PASS: alert_rate_limit() produces correct 5W structure and content")


def test_unit_alert_connection_failure_content():
    """[NEGATIVE] alert_connection_failure() must produce correct 5W content."""
    captured, original = _captured_alerts()
    try:
        with patch.dict(os.environ, {"SENDGRID_API_KEY": "fake-key"}):
            alert_connection_failure()
        assert len(captured) == 1
        alert = captured[0]
        assert "Network connection failed" in alert["subject"]
        assert "WHAT:" in alert["body"]
        assert "load shedding" in alert["body"]
        assert "status.anthropic.com" in alert["body"]
        assert "TRIGGERED BY:" in alert["body"]
        assert "README" in alert["body"]
    finally:
        _restore_send_alert(original)
    print("PASS: alert_connection_failure() produces correct 5W structure and content")


def test_unit_alert_api_status_error_content():
    """[NEGATIVE] alert_api_status_error() must include the status code and message."""
    captured, original = _captured_alerts()
    try:
        with patch.dict(os.environ, {"SENDGRID_API_KEY": "fake-key"}):
            alert_api_status_error(429, "Too many requests")
        assert len(captured) == 1
        alert = captured[0]
        assert "429" in alert["subject"]
        assert "429" in alert["body"]
        assert "Too many requests" in alert["body"]
        assert "billing" in alert["body"]
        assert "TRIGGERED BY:" in alert["body"]
        assert "README" in alert["body"]
    finally:
        _restore_send_alert(original)
    print("PASS: alert_api_status_error() includes status code and message correctly")


def test_unit_alert_resume_approval_content():
    """[NEGATIVE / SAFETY] alert_resume_approval_required() must stress
    that no files were modified and approval is required."""
    captured, original = _captured_alerts()
    try:
        with patch.dict(os.environ, {"SENDGRID_API_KEY": "fake-key"}):
            alert_resume_approval_required("2026-07-01T00:00:00Z")
        assert len(captured) == 1
        alert = captured[0]
        assert "approval" in alert["subject"].lower()
        assert "NOT been executed" in alert["body"]
        assert "No files have been modified" in alert["body"]
        assert "agent_state.json" in alert["body"]
        assert "Get-Content agent_state.json" in alert["body"]
        assert "TRIGGERED BY:" in alert["body"]
        assert "README" in alert["body"]
    finally:
        _restore_send_alert(original)
    print("PASS: alert_resume_approval_required() correctly stresses safety guarantee")


def test_unit_alert_corrupted_state_content():
    """[NEGATIVE] alert_corrupted_state_file() must include error detail
    and safe recovery steps."""
    captured, original = _captured_alerts()
    try:
        with patch.dict(os.environ, {"SENDGRID_API_KEY": "fake-key"}):
            alert_corrupted_state_file("JSONDecodeError: line 1")
        assert len(captured) == 1
        alert = captured[0]
        assert "State file unreadable" in alert["subject"]
        assert "JSONDecodeError" in alert["body"]
        assert "Remove-Item agent_state.json" in alert["body"]
        # The OneDrive safety note spans two lines -- join before checking
        joined = " ".join(alert["body"].split())
        assert "no onedrive files are affected" in joined.lower()
        assert "TRIGGERED BY:" in alert["body"]
        assert "README" in alert["body"]
    finally:
        _restore_send_alert(original)
    print("PASS: alert_corrupted_state_file() includes error detail and safe recovery steps")


def test_unit_alert_sendgrid_failure_content():
    """[NEGATIVE] alert_sendgrid_failure() must include troubleshooting
    for the SendGrid key itself."""
    captured, original = _captured_alerts()
    try:
        with patch.dict(os.environ, {"SENDGRID_API_KEY": "fake-key"}):
            alert_sendgrid_failure("HTTP 401: Unauthorized")
        assert len(captured) == 1
        alert = captured[0]
        assert "Alert delivery failed" in alert["subject"]
        assert "HTTP 401" in alert["body"]
        assert "SENDGRID_API_KEY" in alert["body"]
        assert "echo $env:SENDGRID_API_KEY" in alert["body"]
        assert "sendgrid.com" in alert["body"]
        assert "TRIGGERED BY:" in alert["body"]
        assert "README" in alert["body"]
    finally:
        _restore_send_alert(original)
    print("PASS: alert_sendgrid_failure() includes SendGrid key troubleshooting")


def test_unit_all_alerts_contain_masked_user_id():
    """
    [SECURITY] Every named alert function must include the masked user ID
    in its TRIGGERED BY field -- verifying the security design decision
    is consistently applied across all 7 functions.
    """
    alert_fns_and_args = [
        (alert_auth_failure, []),
        (alert_rate_limit, []),
        (alert_connection_failure, []),
        (alert_api_status_error, [500, "Internal error"]),
        (alert_resume_approval_required, ["2026-07-01T00:00:00Z"]),
        (alert_corrupted_state_file, ["JSONDecodeError"]),
        (alert_sendgrid_failure, ["HTTP 401"]),
    ]
    with patch.dict(os.environ, {
        "SENDGRID_API_KEY": "fake-key",
        "USERNAME": "Nadeem",
        "COMPUTERNAME": "DESKTOP-TEST"
    }):
        for fn, args in alert_fns_and_args:
            captured, original = _captured_alerts()
            try:
                fn(*args)
                assert len(captured) == 1
                body = captured[0]["body"]
                assert "Na****" in body, (
                    f"{fn.__name__} body missing masked username. "
                    f"TRIGGERED BY field: {[l for l in body.split(chr(10)) if 'TRIGGERED' in l]}"
                )
                assert "DE****" in body, (
                    f"{fn.__name__} body missing masked hostname."
                )
            finally:
                _restore_send_alert(original)
    print("PASS: All 7 alert functions include masked user ID in TRIGGERED BY field")


def test_unit_send_alert_missing_sendgrid_key():
    """
    [NEGATIVE] send_alert() must fail gracefully when SENDGRID_API_KEY
    is not set -- log the error but never raise, so a missing key
    doesn't crash the already-failing agent loop.
    """
    env = os.environ.copy()
    env.pop("SENDGRID_API_KEY", None)
    with patch.dict(os.environ, env, clear=True):
        try:
            send_alert("Test subject", "Test body")
            print("PASS: send_alert() handles missing SENDGRID_API_KEY without raising")
        except Exception as e:
            assert False, f"send_alert() should not raise on missing key, got: {e}"


# ---------------------------------------------------------------------------
# LAYER 2: INTEGRATION TESTS
# ---------------------------------------------------------------------------

def test_integration_full_tool_chain_via_execute():
    """
    Integration: the full tool chain (scan -> find_duplicates +
    find_convertible_files -> propose_action) executed via
    execute_tool_call() -- the same path the real agent loop uses --
    confirms data flows correctly through all four tools.
    """
    scan_result    = execute_tool_call("scan_folder", {"path": "sample_data", "recursive": True})
    assert "result" in scan_result
    files = scan_result["result"]
    assert len(files) == 6

    dup_result  = execute_tool_call("find_duplicates", {"files": files})
    conv_result = execute_tool_call("find_convertible_files", {"files": files})
    assert "result" in dup_result
    assert "result" in conv_result
    assert len(dup_result["result"])  == 1  # one duplicate group
    assert len(conv_result["result"]) == 1  # one convertible file

    prop_result = execute_tool_call("propose_action", {
        "duplicate_groups":   dup_result["result"],
        "convertible_files":  conv_result["result"],
    })
    assert "result" in prop_result
    proposals = prop_result["result"]
    assert len(proposals) == 3  # 2 deletes + 1 convert
    action_types = [p["action_type"] for p in proposals]
    assert action_types.count("delete_duplicate")  == 2
    assert action_types.count("convert_format")    == 1

    print("PASS: Full tool chain via execute_tool_call() produces correct proposals")


def test_integration_state_machine_full_cycle():
    """
    Integration: a complete, valid state-machine cycle from SCANNING
    to DONE, with state written to disk at each step and verified
    by reading it back -- confirms the full restart-and-resume
    persistence chain works end to end.
    """
    tf = _temp_state_file()
    resilience.STATE_FILE = tf
    try:
        state = AgentState.SCANNING
        state = transition_to(state, AgentState.AWAITING_DECISION, {"files": 6})
        saved = json.loads(tf.read_text())
        assert saved["state"] == "AWAITING_DECISION"

        state = transition_to(state, AgentState.EXECUTING_TOOL, {"tool": "find_duplicates"})
        saved = json.loads(tf.read_text())
        assert saved["state"] == "EXECUTING_TOOL"

        state = transition_to(state, AgentState.AWAITING_DECISION, {"results": "done"})
        state = transition_to(state, AgentState.AWAITING_HUMAN_APPROVAL, {"proposals": 3})
        saved = json.loads(tf.read_text())
        assert saved["state"] == "AWAITING_HUMAN_APPROVAL"

        # Simulate resume -- must land back in AWAITING_HUMAN_APPROVAL
        resumed_state, resumed_data = check_for_resume()
        assert resumed_state == AgentState.AWAITING_HUMAN_APPROVAL
        assert resumed_data == {"proposals": 3}

        # Complete the cycle
        state = transition_to(resumed_state, AgentState.DONE, {})
        assert state == AgentState.DONE

    finally:
        if tf.exists(): tf.unlink()
        resilience.STATE_FILE = STATE_FILE

    print("PASS: Full state-machine cycle with resume confirmed end to end")


def test_integration_error_path_returns_error_dict_not_raises():
    """
    Integration: confirms that an error mid-chain (bad arguments to a
    real function) returns an error dict that can be fed back to Claude
    as an observation, rather than raising and crashing the loop.
    """
    # Good scan result
    scan_result = execute_tool_call("scan_folder", {"path": "sample_data"})
    assert "result" in scan_result

    # Bad call: pass scan result directly to propose_action, skipping
    # find_duplicates and find_convertible_files -- wrong argument names
    bad_result = execute_tool_call("propose_action", {
        "files": scan_result["result"]  # wrong arg -- should be duplicate_groups
    })
    assert "error" in bad_result, "Wrong args should produce error dict, not raise"
    assert "result" not in bad_result

    print("PASS: Error mid-chain returns error dict, not exception")


# ---------------------------------------------------------------------------
# LAYER 1: UNIT TESTS -- Phase 5: approval_gate.py
# ---------------------------------------------------------------------------

def test_unit_snapshot_writes_correctly():
    """
    [POSITIVE] write_snapshot() must create a valid JSON file containing
    path, size, md5, and timestamp for each affected file.
    """
    proposals = [
        {"action_type": "delete_duplicate",
         "target_path": "sample_data/original_notes.txt", "reason": "test"},
    ]
    tf = _temp_state_file()
    approval_gate.SNAPSHOT_FILE = tf
    try:
        result = write_snapshot(proposals)
        assert result is True
        saved = json.loads(tf.read_text())
        assert "snapshot_timestamp_utc" in saved
        assert saved["files_affected"] == 1
        assert len(saved["files"]) == 1
        entry = saved["files"][0]
        assert entry["exists"] is True
        assert "size_bytes" in entry
        assert "md5" in entry
        assert "modified_utc" in entry
    finally:
        if tf.exists(): tf.unlink()
        approval_gate.SNAPSHOT_FILE = SNAPSHOT_FILE
    print("PASS: write_snapshot() creates correct JSON with file metadata")


def test_unit_snapshot_blocked_on_write_failure():
    """
    [NEGATIVE / RISK 1] write_snapshot() must return False when the
    snapshot file cannot be written -- the 'no snapshot, no actions'
    precondition.
    """
    proposals = [{"action_type": "delete_duplicate",
                  "target_path": "sample_data/original_notes.txt", "reason": "test"}]
    approval_gate.SNAPSHOT_FILE = Path("/nonexistent_dir_xyz/snapshot.json")
    try:
        result = write_snapshot(proposals)
        assert result is False, "Should return False when write fails"
    finally:
        approval_gate.SNAPSHOT_FILE = SNAPSHOT_FILE
    print("PASS: write_snapshot() returns False when file cannot be written")


def test_unit_run_approval_gate_blocked_when_snapshot_fails():
    """
    [NEGATIVE / RISK 1] run_approval_gate() must return status='blocked'
    and execute zero actions when the snapshot write fails.
    """
    proposals = [{"action_type": "delete_duplicate",
                  "target_path": "sample_data/original_notes.txt",
                  "reason": "test", "details": {}}]
    approval_gate.SNAPSHOT_FILE = Path("/nonexistent_dir_xyz/snapshot.json")
    try:
        result = run_approval_gate(proposals)
        assert result["status"] == "blocked"
        assert result["succeeded"] == 0
        assert result["failed"] == 0
    finally:
        approval_gate.SNAPSHOT_FILE = SNAPSHOT_FILE
    print("PASS: run_approval_gate() blocks execution when snapshot fails")


def test_unit_prompt_approval_invalid_input_reprompts():
    """
    [NEGATIVE / RISK 2] _prompt_approval() must re-prompt on invalid
    input without crashing. Tests that arbitrary strings, empty input,
    and non-y/n values are all rejected.
    """
    from approval_gate import _prompt_approval
    proposal = {"action_type": "delete_duplicate",
                "target_path": "some/file.txt", "reason": "test"}
    inputs = iter(["maybe", "", "x", "DELETE", "y"])
    with patch("builtins.input", side_effect=inputs):
        result = _prompt_approval(proposal, 1, 1)
    assert result is True
    print("PASS: _prompt_approval() re-prompts on invalid input, accepts y")


def test_unit_prompt_approval_accepts_no():
    """
    [POSITIVE] _prompt_approval() must return False when user enters n.
    """
    from approval_gate import _prompt_approval
    proposal = {"action_type": "delete_duplicate",
                "target_path": "some/file.txt", "reason": "test"}
    with patch("builtins.input", return_value="n"):
        result = _prompt_approval(proposal, 1, 1)
    assert result is False
    print("PASS: _prompt_approval() returns False for n")


def test_unit_execute_delete_missing_file():
    """
    [NEGATIVE / RISK 3] _execute_delete() must handle FileNotFoundError
    gracefully -- return False, not raise.
    """
    from approval_gate import _execute_delete
    result = _execute_delete("/nonexistent/file/xyz.txt")
    assert result is False
    print("PASS: _execute_delete() returns False for missing file without raising")


def test_unit_execute_approved_actions_continues_after_failure():
    """
    [NEGATIVE / RISK 3] execute_approved_actions() must continue with
    remaining actions after a single action failure -- a failure on one
    item must not abort the rest.
    """
    mixed = [
        {"action_type": "delete_duplicate",
         "target_path": "/nonexistent/gone.txt",
         "reason": "test", "details": {}},
        {"action_type": "convert_format",
         "target_path": "sample_data/old_photo.bmp",
         "reason": "test", "details": {"suggested_extension": ".png"}},
    ]
    summary = execute_approved_actions(mixed)
    assert summary["failed"] == 1, f"Expected 1 failed, got {summary['failed']}"
    assert summary["succeeded"] == 1, f"Expected 1 succeeded, got {summary['succeeded']}"
    print(f"PASS: execute_approved_actions() continues after failure: {summary}")


def test_unit_execute_approved_actions_unknown_action_type():
    """
    [NEGATIVE] An unrecognised action_type must be skipped with a
    warning, not crash the execution loop.
    """
    unknown = [
        {"action_type": "teleport_file",
         "target_path": "sample_data/original_notes.txt",
         "reason": "test", "details": {}},
    ]
    summary = execute_approved_actions(unknown)
    assert summary["skipped"] == 1
    assert summary["succeeded"] == 0
    assert summary["failed"] == 0
    print("PASS: execute_approved_actions() skips unknown action types without crashing")


def test_unit_run_approval_gate_empty_proposals():
    """
    [POSITIVE] run_approval_gate() must handle an empty proposal list
    gracefully -- no snapshot needed, no prompts, no actions.
    """
    result = run_approval_gate([])
    assert result["succeeded"] == 0
    print("PASS: run_approval_gate() handles empty proposals cleanly")


# ---------------------------------------------------------------------------
# LAYER 2: INTEGRATION TESTS -- Phase 5
# ---------------------------------------------------------------------------

def test_integration_full_phase5_approve_all():
    """
    Integration: full Phase 1 -> Phase 5 chain with all proposals
    approved. Verifies snapshot is written, all actions execute,
    and the summary is correct.

    ISOLATION FIX (2026-07-02, caught by Claude Cowork peer review):
    This test previously scanned and operated on the REAL sample_data/
    folder. Since _execute_delete() is not mocked, "approve all" genuinely
    deleted real fixture files on every test run, causing sample_data/ to
    drift out of sync with what test_phase2.py expects (a recurring,
    self-inflicted bug, not a one-time fluke). Fixed by building a
    temporary copy of sample_data/ and operating entirely within it --
    the real fixture folder is never touched by this test.
    """
    import shutil
    from tools import scan_folder, find_duplicates, find_convertible_files, propose_action

    # Build an isolated temp copy of sample_data -- never touch the real folder
    temp_dir = Path(tempfile.mkdtemp())
    temp_sample_data = temp_dir / "sample_data"
    shutil.copytree("sample_data", temp_sample_data)

    tf = _temp_state_file()
    approval_gate.SNAPSHOT_FILE = tf

    try:
        files      = scan_folder(str(temp_sample_data), recursive=True)
        dup_groups = find_duplicates(files)
        convertible = find_convertible_files(files)
        proposals  = propose_action(dup_groups, convertible)
        assert len(proposals) > 0, "Need proposals to test the gate"

        # Approve all
        with patch("builtins.input", return_value="y"):
            result = run_approval_gate(proposals)

        assert result["status"] == "complete"
        assert result["succeeded"] > 0
        assert tf.exists(), "Snapshot file should exist"
        snapshot = json.loads(tf.read_text())
        assert "snapshot_timestamp_utc" in snapshot
        assert snapshot["files_affected"] == len(proposals)
    finally:
        if tf.exists(): tf.unlink()
        approval_gate.SNAPSHOT_FILE = SNAPSHOT_FILE
        shutil.rmtree(temp_dir, ignore_errors=True)

    print(f"PASS: Full Phase 1->5 chain with all approved (isolated temp copy): {result}")


def test_integration_full_phase5_reject_all():
    """
    Integration: full chain with all proposals rejected.
    Verifies snapshot is still written (precondition is met),
    but zero actions execute.

    ISOLATION FIX (2026-07-02, caught by Claude Cowork peer review):
    Same fix as test_integration_full_phase5_approve_all -- operates on
    a temporary copy of sample_data/, never the real fixture folder.
    """
    import shutil
    from tools import scan_folder, find_duplicates, find_convertible_files, propose_action

    # Build an isolated temp copy of sample_data -- never touch the real folder
    temp_dir = Path(tempfile.mkdtemp())
    temp_sample_data = temp_dir / "sample_data"
    shutil.copytree("sample_data", temp_sample_data)

    tf = _temp_state_file()
    approval_gate.SNAPSHOT_FILE = tf

    try:
        files       = scan_folder(str(temp_sample_data), recursive=True)
        dup_groups  = find_duplicates(files)
        convertible = find_convertible_files(files)
        proposals   = propose_action(dup_groups, convertible)

        with patch("builtins.input", return_value="n"):
            result = run_approval_gate(proposals)

        assert result["status"] == "complete"
        assert result["succeeded"] == 0
        assert tf.exists(), "Snapshot should still be written even when all rejected"
    finally:
        if tf.exists(): tf.unlink()
        approval_gate.SNAPSHOT_FILE = SNAPSHOT_FILE
        shutil.rmtree(temp_dir, ignore_errors=True)

    print(f"PASS: Full Phase 1->5 chain with all rejected (isolated temp copy): {result}")


# ---------------------------------------------------------------------------
# TEST RUNNER
# ---------------------------------------------------------------------------

UNIT_TESTS = [
    # Phase 3
    test_unit_get_client_missing_key,
    test_unit_get_client_with_key,
    # Phase 4
    test_unit_validate_arguments_missing_required,
    test_unit_validate_arguments_unexpected_arg,
    test_unit_validate_arguments_valid_passes,
    test_unit_validate_arguments_none_value,
    test_unit_execute_tool_call_unrecognised_tool,
    test_unit_execute_tool_call_malformed_arguments,
    test_unit_execute_tool_call_runtime_error_in_tool,
    test_unit_execute_tool_call_valid_execution,
    # Phase 4.5 -- state machine
    test_unit_state_machine_all_states_defined,
    test_unit_valid_transitions_complete,
    test_unit_invalid_transition_raises,
    test_unit_valid_transition_persists_state,
    test_unit_check_for_resume_fresh_run,
    test_unit_check_for_resume_corrupted_json,
    test_unit_check_for_resume_invalid_state_name,
    test_unit_check_for_resume_awaiting_human_approval_safety,
    test_unit_save_state_disk_write_failure,
    # Phase 4.5 -- masked user ID
    test_unit_masked_user_id_format,
    test_unit_masked_user_id_short_value,
    test_unit_masked_user_id_missing_env_vars,
    # Phase 4.5 -- alert content (5W framework verification)
    test_unit_alert_auth_failure_content,
    test_unit_alert_rate_limit_content,
    test_unit_alert_connection_failure_content,
    test_unit_alert_api_status_error_content,
    test_unit_alert_resume_approval_content,
    test_unit_alert_corrupted_state_content,
    test_unit_alert_sendgrid_failure_content,
    test_unit_all_alerts_contain_masked_user_id,
    test_unit_send_alert_missing_sendgrid_key,
    # Phase 5 -- approval_gate.py
    test_unit_snapshot_writes_correctly,
    test_unit_snapshot_blocked_on_write_failure,
    test_unit_run_approval_gate_blocked_when_snapshot_fails,
    test_unit_prompt_approval_invalid_input_reprompts,
    test_unit_prompt_approval_accepts_no,
    test_unit_execute_delete_missing_file,
    test_unit_execute_approved_actions_continues_after_failure,
    test_unit_execute_approved_actions_unknown_action_type,
    test_unit_run_approval_gate_empty_proposals,
]

INTEGRATION_TESTS = [
    test_integration_full_tool_chain_via_execute,
    test_integration_state_machine_full_cycle,
    test_integration_error_path_returns_error_dict_not_raises,
    # Phase 5
    test_integration_full_phase5_approve_all,
    test_integration_full_phase5_reject_all,
]


def _run_layer(label, tests):
    print(f"\n{'=' * 60}")
    print(label)
    print("=" * 60)
    failures = []
    for test in tests:
        print(f"\n--- {test.__name__} ---")
        try:
            test()
        except AssertionError as e:
            failures.append((test.__name__, str(e)))
            print(f"FAIL: {e}")
        except Exception as e:
            failures.append((test.__name__, f"{type(e).__name__}: {e}"))
            print(f"ERROR: {type(e).__name__}: {e}")
    return failures


def run_all_tests():
    print("#" * 60)
    print("# PRE-PHASE-5 QUALITY GATE + PHASE 5 APPROVAL GATE TESTS")
    print("# test_phase3_4_45.py")
    print(f"# {len(UNIT_TESTS)} unit tests + {len(INTEGRATION_TESTS)} integration tests")
    print("#" * 60)

    unit_failures = _run_layer(
        f"LAYER 1: UNIT TESTS ({len(UNIT_TESTS)} tests)", UNIT_TESTS
    )

    if unit_failures:
        print(f"\n{'#' * 60}")
        print(f"UNIT TESTS FAILED ({len(unit_failures)}) -- skipping integration tests")
        print("Integration results would not be meaningful until unit tests pass.")
        for name, msg in unit_failures:
            print(f"  - {name}: {msg}")
        print("#" * 60)
        return

    integration_failures = _run_layer(
        f"LAYER 2: INTEGRATION TESTS ({len(INTEGRATION_TESTS)} tests)",
        INTEGRATION_TESTS,
    )

    total = len(UNIT_TESTS) + len(INTEGRATION_TESTS)
    total_failures = len(unit_failures) + len(integration_failures)
    print(f"\n{'#' * 60}")
    if total_failures:
        print(f"RESULT: {total_failures}/{total} test(s) failed")
        for name, msg in integration_failures:
            print(f"  - {name}: {msg}")
    else:
        print(
            f"RESULT: all {total} tests passed "
            f"({len(UNIT_TESTS)} unit + {len(INTEGRATION_TESTS)} integration)"
        )
    print("#" * 60)


if __name__ == "__main__":
    run_all_tests()
