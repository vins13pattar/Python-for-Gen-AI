# run.py
"""
Multi-Agent pipeline: Supervisor → Researcher → Writer → Reviewer
with automatic revision loops.

Usage:
    export OPENAI_API_KEY="sk-..."
    export TAVILY_API_KEY="tvly-..."   # free tier at tavily.com
    python run.py
"""

import uuid
import time
from langchain_core.messages import HumanMessage

from graph import build_graph, print_graph_structure
from state import MultiAgentState


def print_banner(text: str, width: int = 60, char: str = "═") -> None:
    print(f"\n{char * width}")
    print(f"  {text}")
    print(f"{char * width}")


def stream_run(app, initial_state: MultiAgentState, config: dict) -> dict:
    """
    Runs the graph with streaming so you see each node's output
    as it happens rather than waiting for the full run.
    """
    final_state = None

    for step in app.stream(initial_state, config, stream_mode="updates"):
        for node_name, updates in step.items():
            print(f"\n{'─' * 50}")
            print(f"  NODE: {node_name.upper()}")
            print(f"{'─' * 50}")

            if "next_agent" in updates:
                print(f"  Next → {updates['next_agent']}")

            if "research_notes" in updates and updates["research_notes"]:
                note = updates["research_notes"][-1]
                print(f"  Research snippet: {note[:200]}...")

            if "draft" in updates and updates["draft"]:
                draft = updates["draft"]
                print(f"  Draft preview ({len(draft)} chars):\n  {draft[:300]}...")

            if "review_verdict" in updates:
                print(f"  Review verdict: {updates['review_verdict']}")
                if updates.get("review_feedback"):
                    print(f"  Feedback: {updates['review_feedback'][:200]}...")

            if "messages" in updates:
                for msg in updates["messages"]:
                    if hasattr(msg, "content") and msg.content:
                        print(f"  Message: {msg.content[:150]}")

        final_state = step

    return app.get_state(config).values


def main():
    print_banner("LangGraph Multi-Agent Pipeline")
    print("Agents: Supervisor | Researcher | Writer | Reviewer")
    print("Flow: START → Supervisor → [Researcher ↔ Writer ↔ Reviewer] → END")

    # Build graph
    app = build_graph()
    print_graph_structure(app)

    # Get topic from user
    print("\nEnter a topic for the AI team to research and write about.")
    print("Example: 'The impact of quantum computing on cybersecurity'")
    print()
    topic = input("Topic: ").strip()
    if not topic:
        topic = "The rise of agentic AI systems and their real-world applications in 2026"
        print(f"\n[using default topic]: {topic}")

    # Setup
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    initial: MultiAgentState = {
        "task":            topic,
        "messages":        [HumanMessage(content=f"Research and write about: {topic}")],
        "next_agent":      "",
        "research_notes":  [],
        "draft":           "",
        "review_feedback": "",
        "review_verdict":  "",
        "revision_count":  0,
        "final_output":    "",
    }

    # Run
    print_banner("Pipeline Running", char="─")
    start_time = time.time()

    try:
        final = stream_run(app, initial, config)
    except KeyboardInterrupt:
        print("\n[interrupted] Getting current state...")
        final = app.get_state(config).values

    elapsed = time.time() - start_time

    # Output
    print_banner("FINAL ARTICLE")
    draft = final.get("draft", "")
    if draft:
        print(draft)
    else:
        print("[No draft produced]")

    print_banner("PIPELINE SUMMARY", char="─")
    print(f"  Topic:          {topic[:70]}")
    print(f"  Research notes: {len(final.get('research_notes', []))} block(s)")
    print(f"  Revisions:      {final.get('revision_count', 0)}")
    print(f"  Final verdict:  {final.get('review_verdict', 'n/a').upper()}")
    print(f"  Time elapsed:   {elapsed:.1f}s")
    print(f"  Total messages: {len(final.get('messages', []))}")

    # Save to file
    if draft:
        filename = f"output_{uuid.uuid4().hex[:8]}.md"
        with open(filename, "w") as f:
            f.write(f"# {topic}\n\n")
            f.write(draft)
        print(f"\n  Saved to: {filename}")


if __name__ == "__main__":
    main()