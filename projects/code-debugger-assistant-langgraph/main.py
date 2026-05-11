"""
Code Debugger Assistant — interactive runner.

Supports two modes:
  python main.py          → single-turn (prompts for input once)
  python main.py --multi  → multi-turn session with memory across turns

Streaming: uses stream_mode="custom" to display real progress messages
           emitted by get_stream_writer() inside each tool.
"""
import json
import sys
import textwrap
from dotenv import load_dotenv

load_dotenv()  # Must run before importing app modules (they use init_chat_model lazily)

from langgraph.checkpoint.memory import MemorySaver  # noqa: E402
from app.graph import graph as _graph  # noqa: E402

# Add checkpointer for local CLI usage (LangGraph Platform provides its own)
checkpointer = MemorySaver()
graph = _graph.compile(checkpointer=checkpointer) if hasattr(_graph, 'compile') else _graph

# ── Helpers ───────────────────────────────────────────────────────────────────

SEPARATOR = "─" * 60


def build_user_message(code: str, error_message: str, expected_behavior: str) -> str:
    """Format user inputs into a clear message for the agent."""
    parts = []
    if code:
        parts.append(f"Here is my code:\n\n```\n{code}\n```")
    if error_message:
        parts.append(f"Error message:\n{error_message}")
    if expected_behavior:
        parts.append(f"Expected behavior:\n{expected_behavior}")
    return "\n\n".join(parts)


def stream_and_print(content: str, config: dict) -> dict | str:
    """Invoke graph with streaming and return the final structured report."""
    print(f"\n{SEPARATOR}")
    print("📡 Streaming Progress:")
    print()

    for chunk in graph.stream(
        {"messages": [{"role": "user", "content": content}]},
        config=config,
        stream_mode="custom",
    ):
        print(f"   ⟳  {chunk}")

    # Retrieve final state
    final_state = graph.get_state(config).values
    structured = final_state.get("structured_response")
    if structured:
        return structured.model_dump() if hasattr(structured, "model_dump") else structured
    messages = final_state.get("messages", [])
    return messages[-1].content if messages else "No response."


def print_report(report: dict | str) -> None:
    print()
    print(SEPARATOR)
    print("📋 Final Debug Report:")
    print(SEPARATOR)
    if isinstance(report, dict):
        print(json.dumps(report, indent=2))
    else:
        print(report)
    print()


def prompt_code_block() -> str:
    """
    Prompt the user to paste multi-line code.
    User types END on a blank line to finish.
    """
    print("Paste your code below. Type END on a new line when done (or leave blank to skip):")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines).strip()


# ── Single-turn mode ──────────────────────────────────────────────────────────

def run_single_turn(thread_id: str = "debug-session-1") -> None:
    """Prompt for inputs once, debug, and print the report."""
    print(f"\n{SEPARATOR}")
    print("  Code Debugger Assistant")
    print(SEPARATOR)
    print(textwrap.dedent("""
  Instructions:
    • Paste your code (type END on a new blank line to finish)
    • Provide the error message / traceback
    • Describe the expected behavior
    • Type 'exit' at any prompt to quit
    """))

    # ── Code input ──────────────────────────────────────────────────────────
    code = prompt_code_block()
    if code.lower() == "exit":
        return

    # ── Error message ────────────────────────────────────────────────────────
    print("\nError message or traceback (or press Enter to skip):")
    error_message = input("> ").strip()
    if error_message.lower() == "exit":
        return

    # ── Expected behavior ────────────────────────────────────────────────────
    print("\nExpected behavior (or press Enter to skip):")
    expected_behavior = input("> ").strip()
    if expected_behavior.lower() == "exit":
        return

    if not code and not error_message:
        print("⚠️  Please provide at least some code or an error message.")
        return

    content = build_user_message(code, error_message, expected_behavior)
    config = {"configurable": {"thread_id": thread_id}}

    report = stream_and_print(content, config)
    print_report(report)


# ── Multi-turn mode ───────────────────────────────────────────────────────────

def run_multi_turn(thread_id: str = "debug-session-multi") -> None:
    """
    Interactive multi-turn session.
    The agent remembers context across turns using the same thread_id.
    """
    print(f"\n{SEPARATOR}")
    print("  Code Debugger Assistant — Multi-Turn Session")
    print(SEPARATOR)
    print("  The assistant remembers your previous code and errors within this session.")
    print("  Type 'exit' at any prompt to quit.\n")

    config = {"configurable": {"thread_id": thread_id}}
    turn = 1

    while True:
        print(f"{SEPARATOR}")
        print(f"  Turn {turn}")
        print(SEPARATOR)

        # ── Code input ────────────────────────────────────────────────────
        code = prompt_code_block()
        if code.lower() == "exit":
            break

        # ── Error message ─────────────────────────────────────────────────
        print("\nError message or traceback (or press Enter to skip):")
        error_msg = input("> ").strip()
        if error_msg.lower() == "exit":
            break

        # ── Expected behavior ─────────────────────────────────────────────
        print("\nExpected behavior (or press Enter to skip):")
        expected = input("> ").strip()
        if expected.lower() == "exit":
            break

        # ── Follow-up mode if no code/error provided ──────────────────────
        if not code and not error_msg:
            print("\nFollow-up question for the assistant (based on previous context):")
            content = input("> ").strip()
            if content.lower() == "exit":
                break
        else:
            content = build_user_message(code, error_msg, expected)

        report = stream_and_print(content, config)
        print_report(report)
        turn += 1


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "single"
    if mode == "--multi":
        run_multi_turn()
    else:
        run_single_turn()
