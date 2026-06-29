"""
Phase 3: The decision loop, built against the live Anthropic API.

This is the first phase where an actual AI model is involved. Everything
before this (Phase 1's functions, Phase 2's contracts) was just setup --
this is where we hand Claude a goal and the tool contracts, and Claude
decides which tool to call and with what arguments.

IMPORTANT: this script does NOT execute anything yet. It only proves
that Claude can read the tool contracts and make a single, correct,
structured decision. Actually running the chosen tool and looping
multiple steps is Phase 4. Nothing in this script touches the
filesystem beyond the read-only scan_folder() call used to show
Claude the current folder state.

SECURITY NOTE: the API key is read from an environment variable
(ANTHROPIC_API_KEY), never hardcoded here. This file is safe to push
to a public GitHub repo because of that -- there is no secret in this
file itself.
"""

import os
import json

import anthropic

from tools import scan_folder
from tool_contracts import TOOL_CONTRACTS


def get_client() -> anthropic.Anthropic:
    """
    Create the Anthropic API client, reading the key from the
    ANTHROPIC_API_KEY environment variable.

    If the key isn't set, this fails with a clear error rather than
    silently doing nothing -- so it's obvious during setup if the
    environment variable wasn't picked up (e.g. forgot to open a new
    terminal window after setting it).
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY environment variable not found. "
            "Set it, then open a NEW terminal window before running this script."
        )
    return anthropic.Anthropic(api_key=api_key)


def ask_claude_to_decide(client: anthropic.Anthropic, goal: str, folder_state: list[dict]) -> anthropic.types.Message | None:
    """
    Send Claude the goal, the four tool contracts, and the current
    folder state, and let it decide which tool (if any) to call next.

    This is a single decision, not a loop -- Phase 4 will repeat this
    step, feeding each tool's result back in as the next "folder state"
    style observation.

    Returns None if the API call failed for a reason we recognize and
    handle gracefully (see error handling below) -- callers should
    check for None rather than assume a response always comes back.
    """
    user_message = (
        f"Goal: {goal}\n\n"
        f"Current folder contents (already scanned):\n"
        f"{json.dumps(folder_state, indent=2)}\n\n"
        f"Decide which tool to call next to make progress on the goal."
    )

    # Real API calls can fail in ways that are entirely normal and
    # expected, not exceptional bugs: the network can drop, the
    # account can run out of credit, or too many requests can be sent
    # too quickly. Each is caught specifically (not as one generic
    # "something went wrong") so the printed message tells you exactly
    # what happened and what to actually do about it, rather than
    # dumping a raw Python stack trace.
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            tools=TOOL_CONTRACTS,
            messages=[
                {"role": "user", "content": user_message}
            ],
        )
        return response

    except anthropic.AuthenticationError:
        print(
            "ERROR: Authentication failed. The API key was rejected.\n"
            "Check that ANTHROPIC_API_KEY is set correctly and hasn't been "
            "revoked or regenerated in the console."
        )
        return None

    except anthropic.RateLimitError:
        print(
            "ERROR: Rate limit hit. Too many requests sent too quickly.\n"
            "Wait a short while and try again."
        )
        return None

    except anthropic.APIConnectionError:
        print(
            "ERROR: Could not connect to the Anthropic API.\n"
            "Check your internet connection and try again."
        )
        return None

    except anthropic.APIStatusError as e:
        # Covers cases like insufficient credit/quota (e.g. the $6
        # balance running out) and other API-reported errors that
        # don't fit the more specific cases above.
        print(
            f"ERROR: The API returned an error (status {e.status_code}).\n"
            f"Details: {e.message}\n"
            "If this mentions credit or billing, check your balance at "
            "console.anthropic.com."
        )
        return None


def print_decision(response: anthropic.types.Message) -> None:
    """
    Print out what Claude decided, in a readable way -- either a tool
    call (name + arguments) or, if no tool call was made, the plain
    text response instead.
    """
    print("=" * 60)
    print("CLAUDE'S RESPONSE")
    print("=" * 60)

    for block in response.content:
        if block.type == "text":
            print(f"\n[Claude said]: {block.text}")
        elif block.type == "tool_use":
            print(f"\n[Claude chose to call]: {block.name}")
            print(f"[With arguments]: {json.dumps(block.input, indent=2)}")

    print(f"\n[Stop reason]: {response.stop_reason}")
    print("=" * 60)


if __name__ == "__main__":
    client = get_client()

    # Scan the sample folder first, so Claude has real data to reason about.
    # This is the only "tool" we run ourselves before involving Claude --
    # everything after this is Claude's decision, not ours.
    current_files = scan_folder("sample_data", recursive=True)

    goal = "Clean up this folder: find anything that should be removed or converted to a better format."

    response = ask_claude_to_decide(client, goal, current_files)

    if response is None:
        # ask_claude_to_decide already printed a specific, actionable
        # error message above -- nothing further to do here except
        # stop cleanly instead of crashing on the next line.
        print("\nStopping: no response to process.")
    else:
        print_decision(response)
