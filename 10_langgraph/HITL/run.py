"""
Human-in-the-Loop email agent.

The agent composes an email, then PAUSES for your review.
You can:
  [y] Approve and send
  [n] Cancel entirely
  [e] Request edits (agent rewrites and asks again)
"""

import uuid
from langchain_core.messages import HumanMessage
from agent import build_graph, EmailAgentState


def print_banner(title: str, char: str = "═") -> None:
    print(f"\n{char * 54}")
    print(f"  {title}")
    print(f"{char * 54}")


def show_draft(pending: dict) -> None:
    print()
    print("┌" + "─" * 52 + "┐")
    print(f"│  📧  EMAIL DRAFT{'':35}│")
    print("├" + "─" * 52 + "┤")
    print(f"│  To:      {pending.get('to', ''):<41}│")
    print(f"│  Subject: {pending.get('subject', ''):<41}│")
    print(f"│  Tone:    {pending.get('tone', 'professional'):<41}│")
    print("├" + "─" * 52 + "┤")
    body_lines = (pending.get("body", "") or "").split("\n")
    for line in body_lines:
        # Word-wrap at 50 chars
        while len(line) > 50:
            print(f"│  {line[:50]}  │")
            line = line[50:]
        print(f"│  {line:<50}  │")
    print("└" + "─" * 52 + "┘")


def main():
    print_banner("LangGraph — Email Sending HITL Demo")

    app    = build_graph()
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    # ── Collect task from user ─────────────────────────────────────
    print("\nDescribe the email you want to send.")
    print("Example: 'Send a follow-up email to john@example.com about")
    print("          the Q3 report we discussed yesterday.'")
    print()
    task = input("Your request: ").strip()
    if not task:
        task = (
            "Send a professional follow-up email to sarah@example.com "
            "thanking her for the meeting today and confirming next steps "
            "for the product launch."
        )
        print(f"\n[using demo task]: {task}")

    initial: EmailAgentState = {
        "messages":       [HumanMessage(task)],
        "pending_email":  None,
        "human_approved": None,
        "edit_request":   "",
        "outcome":        "",
    }

    # ── Run / resume loop ──────────────────────────────────────────
    current_input = initial

    while True:
        print_banner("Agent running...", char="─")
        app.invoke(current_input, config)
        current_input = None   # subsequent invokes resume from checkpoint

        snapshot  = app.get_state(config)

        next_node = snapshot.next

        # ── Not interrupted → graph finished ──────────────────────
        if not next_node or "human_review" not in next_node:
            break

        # ── Interrupted at human_review → show draft ──────────────
        pending = snapshot.values.get("pending_email")
        if not pending:
            print("[warning] Interrupted but no pending email found.")
            break

        print_banner("⚠️  REVIEW REQUIRED — Email ready to send")
        show_draft(pending)

        # ── Ask human ─────────────────────────────────────────────
        print()
        print("  [y] Approve and send")
        print("  [n] Cancel")
        print("  [e] Request edits")
        print()

        while True:
            choice = input("Your decision [y/n/e]: ").strip().lower()
            if choice in ("y", "yes", "n", "no", "e", "edit"):
                break
            print("  Please enter y, n, or e.")

        if choice in ("y", "yes"):
            # ── Approve ───────────────────────────────────────────
            print("\n✓ Approved.")
            app.update_state(
                config,
                {"human_approved": True},
            )
            # One final resume to complete send + summarise
            app.invoke(None, config)
            break

        elif choice in ("n", "no"):
            # ── Cancel ────────────────────────────────────────────
            print("\n✗ Cancelled.")
            app.update_state(
                config,
                {"human_approved": False, "edit_request": ""},
            )
            app.invoke(None, config)
            break

        else:
            # ── Edit request — loop back ───────────────────────────
            edits = input("\nDescribe your changes: ").strip()
            if not edits:
                edits = "Make the tone more concise and friendly."
            print(f"\n↻ Sending edit request to agent: '{edits}'")
            app.update_state(
                config,
                {
                    "human_approved": False,
                    "edit_request":   edits,
                },
            )
            # Loop continues — agent rewrites, graph interrupts again

    # ── Final outcome ──────────────────────────────────────────────
    final_state = app.get_state(config).values
    print_banner("✅  Done")

    outcome = final_state.get("outcome", "")
    if outcome:
        print(f"\n{outcome}")

    last_ai = next(
        (m for m in reversed(final_state.get("messages", []))
         if hasattr(m, "content") and m.content
         and type(m).__name__ == "AIMessage"),
        None,
    )
    if last_ai:
        print(f"\nSummary: {last_ai.content}")


if __name__ == "__main__":
    main()