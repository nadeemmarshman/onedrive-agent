"""
Phase 4: The full agent loop -- decide, execute, observe, repeat.

This is where Phase 3's "decide once and print it" script becomes a real,
looping agent. Each iteration:
  1. Send Claude the goal + tool contracts + current observations
  2. Claude decides which tool(s) to call (zero, one, or several)
  3. We actually RUN those tools for real (Phase 3 never did this)
  4. The results are fed back to Claude as the next observation
  5. Repeat until Claude has no more tool calls to make, or a safety
     limit is hit

Per the project's proactive-design standing rule, this loop explicitly
handles five risks that reliably occur with an LLM-driven, tool-calling
agent -- each is called out below at the point it's handled, not left
as incidental behavior:

  [RISK 1] Claude returning zero, one, or multiple tool calls in a turn
  [RISK 2] Tool-call arguments that don't match what the function expects
  [RISK 3] A tool name Claude requests that isn't recognized
  [RISK 4] No explicit loop-termination condition
  [RISK 5] Real API/network failures during a call in the loop

LOGGING DESIGN:
  Built-in Python logging writes simultaneously to the console AND a
  timestamped file under logs/ -- one file per run, never overwritten.

  Log verbosity is deliberately tiered:
    INFO    -- abbreviated summaries of normal operation (tool name +
               argument shape + result count). Kept lean so logs are
               scannable without noise.
    WARNING -- unexpected but recoverable events. Full detail always
               preserved, since these need to be understood.
    ERROR   -- failures that stop or degrade the loop. Full detail
               always preserved, since these are what you diagnose.

  The INFO/WARNING/ERROR distinction matters for Phase 4.5: email
  alerts fire on ERROR-level events only, not routine INFO messages.

IMPORTANT: propose_action() is the only "action" tool in this agent --
per the project's design, NOTHING in Phases 1-4 deletes or modifies a
real file. find_duplicates/find_convertible_files only read and report;
propose_action only proposes. Actual destructive execution is gated
behind Phase 5's human-approval step, which does not exist yet.
"""

import inspect
import json
import logging
from datetime import datetime
from pathlib import Path

import anthropic

from tools import scan_folder, find_duplicates, find_convertible_files, propose_action
from tool_contracts import TOOL_CONTRACTS
from decision_loop import get_client


MAX_ITERATIONS = 6

FUNCTION_MAP = {
    "scan_folder": scan_folder,
    "find_duplicates": find_duplicates,
    "find_convertible_files": find_convertible_files,
    "propose_action": propose_action,
}


def _summarise_args(arguments: dict) -> str:
    """
    Produce a compact, human-readable summary of tool arguments for
    INFO-level log lines -- shows argument names and shapes (e.g. list
    length), not full values. Full values are never logged at INFO level
    since they can be very long (e.g. a list of 100 file dicts).

    Examples:
        {"path": "sample_data", "recursive": True}
        → path='sample_data', recursive=True

        {"files": [{...}, {...}, {...}]}
        → files=[3 items]

        {"duplicate_groups": [[...]], "convertible_files": [{...}]}
        → duplicate_groups=[1 group], convertible_files=[1 item]
    """
    parts = []
    for key, val in arguments.items():
        if isinstance(val, list):
            # Special case: duplicate_groups is a list of lists --
            # label it as "groups" to make the summary more meaningful.
            if key == "duplicate_groups":
                parts.append(f"{key}=[{len(val)} group(s)]")
            else:
                parts.append(f"{key}=[{len(val)} item(s)]")
        elif isinstance(val, str):
            parts.append(f"{key}='{val}'")
        else:
            parts.append(f"{key}={val}")
    return ", ".join(parts)


def _summarise_result(tool_name: str, result) -> str:
    """
    Produce a compact summary of a tool's return value for INFO-level
    log lines. Each tool's result shape is known, so we can give a
    meaningful count rather than a generic "result returned."
    """
    if tool_name == "scan_folder":
        return f"{len(result)} file(s) found"
    elif tool_name == "find_duplicates":
        return f"{len(result)} duplicate group(s) found"
    elif tool_name == "find_convertible_files":
        return f"{len(result)} convertible file(s) found"
    elif tool_name == "propose_action":
        return f"{len(result)} proposal(s) generated"
    else:
        # Fallback for any future tool not yet listed here
        if isinstance(result, list):
            return f"{len(result)} item(s) returned"
        return "completed"


def setup_logging() -> logging.Logger:
    """
    Configure built-in Python logging to write simultaneously to the
    console and a timestamped file under logs/.

    Console: INFO and above (lean summaries of normal operation).
    File: DEBUG and above (captures everything, including internal
          debug detail not shown on the console).
    """
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"agent_run_{timestamp}.txt"

    logger = logging.getLogger("agent_loop")
    logger.setLevel(logging.DEBUG)

    # Shorter timestamp format (HH:MM only) for INFO lines -- sufficient
    # for a single run's log, and keeps lines compact.
    # WARNING and ERROR use full timestamp since they need precise timing
    # for diagnosis. Both handlers share one formatter for simplicity;
    # the level distinction is in the message content, not the format.
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M",
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.info(f"Run started | log: {log_file}")
    return logger


logger = setup_logging()


def validate_arguments(tool_name: str, arguments: dict) -> str | None:
    """
    [RISK 2] Validate tool arguments against the real function signature
    before calling anything. Returns None if valid, error string if not.
    """
    func = FUNCTION_MAP[tool_name]
    sig = inspect.signature(func)
    valid_param_names = set(sig.parameters.keys())
    required_param_names = {
        name for name, param in sig.parameters.items()
        if param.default is inspect.Parameter.empty
    }
    supplied_names = set(arguments.keys())

    unexpected = supplied_names - valid_param_names
    if unexpected:
        return f"Unexpected argument(s) for {tool_name}: {sorted(unexpected)}"

    missing = required_param_names - supplied_names
    if missing:
        return f"Missing required argument(s) for {tool_name}: {sorted(missing)}"

    return None


def execute_tool_call(tool_name: str, arguments: dict) -> dict:
    """
    Run a tool Claude decided to call, with safety checks first.
    Always returns a dict with 'result' or 'error' -- never raises.
    """
    # [RISK 3] Unrecognized tool name -- full detail in WARNING
    if tool_name not in FUNCTION_MAP:
        msg = f"Unrecognized tool name: '{tool_name}'. Known tools: {list(FUNCTION_MAP.keys())}"
        logger.warning(msg)
        return {"error": msg}

    validation_error = validate_arguments(tool_name, arguments)
    if validation_error:
        # Full detail in WARNING -- validation failures need to be understood
        logger.warning(f"Argument validation failed | {tool_name} | {validation_error}")
        return {"error": validation_error}

    func = FUNCTION_MAP[tool_name]
    try:
        result = func(**arguments)
        # INFO: abbreviated summary only -- result counts, not full data
        logger.info(f"  Result: {_summarise_result(tool_name, result)}")
        return {"result": result}
    except Exception as e:
        # Full detail in ERROR -- unexpected failures need full context
        msg = f"{tool_name} raised an unexpected error: {type(e).__name__}: {e}"
        logger.error(msg)
        return {"error": msg}


def run_agent_loop(goal: str, starting_folder: str = "sample_data") -> None:
    logger.info(f"Goal: {goal}")
    logger.info(f"Scanning: {starting_folder}")

    client = get_client()
    initial_files = scan_folder(starting_folder, recursive=True)
    logger.info(f"Scan complete: {len(initial_files)} file(s) found")

    messages = [
        {
            "role": "user",
            "content": (
                f"Goal: {goal}\n\n"
                f"Current folder contents (already scanned):\n"
                f"{json.dumps(initial_files, indent=2)}\n\n"
                f"Decide which tool(s) to call next to make progress on the goal. "
                f"When you believe the goal is complete, stop calling tools and "
                f"summarize what you found and proposed."
            ),
        }
    ]

    for iteration in range(1, MAX_ITERATIONS + 1):
        logger.info(f"--- Iteration {iteration} ---")

        # [RISK 5] API/network failures -- full detail in ERROR
        try:
            response = client.messages.create(
                model="claude-sonnet-5",
                max_tokens=1500,
                tools=TOOL_CONTRACTS,
                messages=messages,
            )
        except anthropic.AuthenticationError:
            logger.error("Authentication failed. Check ANTHROPIC_API_KEY.")
            return
        except anthropic.RateLimitError:
            logger.error("Rate limit hit. Stopping loop -- try again shortly.")
            return
        except anthropic.APIConnectionError:
            logger.error("Connection failed. Check your internet connection.")
            return
        except anthropic.APIStatusError as e:
            logger.error(f"API error status {e.status_code}: {e.message}")
            return

        # [RISK 1] Zero, one, or multiple tool calls per turn
        tool_calls = [b for b in response.content if b.type == "tool_use"]
        text_blocks = [b for b in response.content if b.type == "text"]

        for block in text_blocks:
            # Claude's commentary: log first line only at INFO (lean),
            # full text goes to DEBUG for the file log
            first_line = block.text.split("\n")[0][:120]
            logger.info(f"  Claude: {first_line}{'...' if len(block.text) > 120 else ''}")
            logger.debug(f"  Claude (full): {block.text}")

        # Natural stop: Claude decided it's done
        if not tool_calls:
            logger.info(f"Loop complete — natural stop after {iteration} iteration(s)")
            return

        messages.append({"role": "assistant", "content": response.content})

        tool_results_content = []
        for call in tool_calls:
            # INFO: abbreviated -- tool name + argument shapes only
            logger.info(f"  Calling: {call.name}({_summarise_args(call.input)})")

            outcome = execute_tool_call(call.name, call.input)

            if "error" in outcome:
                # ERROR: already logged inside execute_tool_call with full detail
                pass

            tool_results_content.append({
                "type": "tool_result",
                "tool_use_id": call.id,
                "content": json.dumps(outcome, default=str),
            })

        messages.append({"role": "user", "content": tool_results_content})

    # [RISK 4] Safety cap reached -- WARNING since it's unexpected
    logger.warning(
        f"Safety cap reached: {MAX_ITERATIONS} iterations without natural stop. "
        f"Review the run log for unexpected behaviour."
    )


if __name__ == "__main__":
    run_agent_loop(
        goal="Clean up this folder: find anything that should be removed or converted to a better format, and propose the specific actions.",
        starting_folder="sample_data",
    )
