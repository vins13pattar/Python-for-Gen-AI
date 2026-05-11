# agents/writer.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from state import MultiAgentState


from dotenv import load_dotenv
load_dotenv()

WRITER_SYSTEM = """
You are an expert content writer. You receive:
  1. A task/topic description
  2. Research notes with facts, statistics, and sources
  3. (Optional) Reviewer feedback on a previous draft

Your job is to write a clear, engaging, well-structured article or response.

Guidelines:
- Start with a compelling hook
- Organize with clear sections and headers (use markdown)
- Integrate research facts naturally — no bullet-dump
- End with a memorable conclusion
- Length: 400-600 words unless instructed otherwise
- If reviewer feedback is provided, specifically address every point raised
"""

llm = ChatOpenAI(model="gpt-4o", temperature=0.7)  # Higher temp for creative writing


def writer_node(state: MultiAgentState) -> dict:
    """
    Drafts (or redrafts) content using research notes.
    If review_feedback is present, it's a revision pass.
    """
    revision = state.get("revision_count", 0)
    feedback = state.get("review_feedback", "")
    is_revision = bool(feedback) and revision > 0

    print(f"\n[writer] {'Revising draft' if is_revision else 'Writing first draft'} "
          f"(revision #{revision})...")

    # Combine all research notes into one block
    notes = "\n\n---\n\n".join(state.get("research_notes", []))

    # Build the user prompt
    if is_revision:
        user_msg = f"""
Task: {state['task']}

Research notes:
{notes}

Previous draft:
{state.get('draft', '')}

Reviewer feedback (MUST address all points):
{feedback}

Please rewrite the draft, fixing all issues the reviewer identified.
""".strip()
    else:
        user_msg = f"""
Task: {state['task']}

Research notes:
{notes}

Write a polished article based on the above research.
""".strip()

    messages = [
        SystemMessage(content=WRITER_SYSTEM),
        HumanMessage(content=user_msg),
    ]

    response = llm.invoke(messages)
    new_draft = response.content

    print(f"[writer] Draft written ({len(new_draft)} chars).")

    return {
        "draft": new_draft,
        "revision_count": revision + (1 if is_revision else 0),
        "review_feedback": "",   # Clear feedback so next reviewer sees fresh draft
        "messages": [AIMessage(
            content=f"[Writer] {'Revised' if is_revision else 'Initial'} draft ready "
                    f"({len(new_draft)} chars)."
        )],
    }