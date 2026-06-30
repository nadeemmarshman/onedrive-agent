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

IMPORTANT: propose_action() is the only "action" tool in this agent --
per the project's design, NOTHING in Phases 1-4 deletes or modifies a
real file. find_duplicates/find_convertible_files only read and report;
propose_action only proposes. Actual destructive execution is gated
behind Phase 5's human-approval step, which does not exist yet.
"""

import inspect
import json

import anthropic

from tools import scan_folder, find_duplicates, find_convertible_files, propose_action
from tool_contracts import TOOL_CONTRACTS
from decision_loop import get_client  # reuse Phase 3's proven API-key loading


MAX_ITERATIONS = 6  # [RISK 4] hard safety cap, separate from the "no more
                     # tool calls" natural stopping condition below -- this
                     # protects against an unexpected infinite back-and-forth
                     # (and runaway API cost) even if something behaves
                     # unexpectedly.

FUNCTION_MAP = {
    "scan_folder": scan_folder,
    "find_duplicates": find_duplicates,
    "find_convertible_files": find_convertible_files,
    "propose_action": propose_action,
}


def validate_arguments(tool_name: str, arguments: dict) -> str | None:
    """
    [RISK 2] Tool-call arguments that don't match what the function expects.

    Checks that every argument Claude supplied is one the real function
    actually accepts, and that every REQUIRED parameter (no default
    value) is present. This runs BEFORE we ever call the real function
    with **arguments, so a malformed call fails with a clear message
    instead of a confusing Python TypeError deep inside tools.py.

    Returns None if the arguments look valid, or an error message
    string describing what's wrong if not.
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
    Actually run a tool Claude decided to call, with the proactive-design
    safety checks applied before anything real happens.

    Always returns a dict with either a "result" or an "error" key --
    never raises -- so the caller can always feed *something* coherent
    back to Claude as the next observation, rather than the whole loop
    crashing because one tool call went wrong.
    """
    # [RISK 3] A tool name Claude requests that isn't recognized.
    # This matters more here than in Phase 3, because Phase 3 only ever
    # printed the decision -- it never tried to actually look the name
    # up and call it. A drifted/invalid tool name must not crash the loop.
    if tool_name not in FUNCTION_MAP:
        return {"error": f"Unrecognized tool name: '{tool_name}'. No such tool exists."}

    validation_error = validate_arguments(tool_name, arguments)
    if validation_error:
        return {"error": validation_error}

    func = FUNCTION_MAP[tool_name]
    try:
        result = func(**arguments)
        return {"result": result}
    except Exception as e:
        # A defensive last line, not the primary safety net -- the
        # validation above should catch malformed arguments before this
        # point. This exists for genuinely unexpected runtime errors
        # (e.g. a file that existed when scanned but was deleted by the
        # time a later tool tried to read it), so even those report
        # back cleanly instead of crashing the whole agent loop.
        return {"error": f"{tool_name} raised an unexpected error: {e}"}


def run_agent_loop(goal: str, starting_folder: str = "sample_data") -> None:
    client = get_client()

    initial_files = scan_folder(starting_folder, recursive=True)

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
        print(f"\n{'=' * 60}\nITERATION {iteration}\n{'=' * 60}")

        # [RISK 5] Real API/network failures during the call itself.
        # Reuses the same specific, named exception handling proven in
        # Phase 3 -- but now it must survive happening mid-loop, not
        # just on a single one-shot call.
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1500,
                tools=TOOL_CONTRACTS,
                messages=messages,
            )
        except anthropic.AuthenticationError:
            print("ERROR: Authentication failed. Check ANTHROPIC_API_KEY.")
            return
        except anthropic.RateLimitError:
            print("ERROR: Rate limit hit. Stopping loop early -- try again shortly.")
            return
        except anthropic.APIConnectionError:
            print("ERROR: Could not connect to the Anthropic API. Check your connection.")
            return
        except anthropic.APIStatusError as e:
            print(f"ERROR: API returned status {e.status_code}: {e.message}")
            return

        # [RISK 1] Claude returning zero, one, or multiple tool calls.
        # Collect ALL tool_use blocks this turn -- not just the first --
        # and separately track any plain-text commentary Claude gave.
        tool_calls = [block for block in response.content if block.type == "tool_use"]
        text_blocks = [block for block in response.content if block.type == "text"]

        for block in text_blocks:
            print(f"\n[Claude said]: {block.text}")

        # Natural stopping condition: Claude made no tool calls this
        # turn, meaning it considers the goal complete (or has nothing
        # further to propose). This is the "normal" way the loop ends,
        # distinct from the MAX_ITERATIONS safety cap.
        if not tool_calls:
            print("\n[Loop complete]: Claude made no further tool calls.")
            return

        # Claude's response (including its tool_use blocks) must be
        # added to the conversation history before we can reply with
        # tool results -- this is required by the API's message format.
        messages.append({"role": "assistant", "content": response.content})

        tool_results_content = []
        for call in tool_calls:
            print(f"\n[Claude calls]: {call.name}")
            print(f"[Arguments]: {json.dumps(call.input, indent=2)}")

            outcome = execute_tool_call(call.name, call.input)

            if "error" in outcome:
                print(f"[Result]: ERROR -- {outcome['error']}")
            else:
                print(f"[Result]: {json.dumps(outcome['result'], indent=2, default=str)[:500]}")

            # Feed the real outcome (success or error) back as an
            # observation, so Claude can see what actually happened and
            # decide the next step -- including recovering from an
            # error if possible, rather than the loop just halting.
            tool_results_content.append({
                "type": "tool_result",
                "tool_use_id": call.id,
                "content": json.dumps(outcome, default=str),
            })

        messages.append({"role": "user", "content": tool_results_content})

    # [RISK 4] Loop-termination condition: if we get here, we hit
    # MAX_ITERATIONS without Claude naturally stopping. This is reported
    # explicitly, not silently -- a portfolio-credible agent should never
    # just quietly stop without saying why.
    print(f"\n{'=' * 60}")
    print(f"[Loop stopped]: reached the safety limit of {MAX_ITERATIONS} iterations "
          f"without Claude indicating the goal was complete.")
    print("=" * 60)


if __name__ == "__main__":
    run_agent_loop(
        goal="Clean up this folder: find anything that should be removed or converted to a better format, and propose the specific actions.",
        starting_folder="sample_data",
    )
