# agents/supervisor.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from state import MultiAgentState


from dotenv import load_dotenv
load_dotenv()

SUPERVISOR_SYSTEM = """
You are a supervisor orchestrating a team of specialist AI agents to complete
writing tasks. Your team consists of:

  - researcher : Searches the web and gathers facts, stats, quotes, sources
  - writer     : Drafts polished content based on the research notes
  - reviewer   : Reviews the draft for quality, accuracy, and completeness

Your job is to decide which agent should act next, given the current state
of work. Always respond with ONLY a JSON object like:
  {"next": "researcher"} or {"next": "writer"} or {"next": "reviewer"} or {"next": "DONE"}

Rules:
- Start with researcher (gather facts first)
- Move to writer only after research_notes is non-empty
- Move to reviewer only after a draft exists
- If the reviewer says needs_revision and revision_count < 2, go back to writer
- If the reviewer approves, or revision_count >= 2, return DONE
- Never skip steps
"""

llm = ChatOpenAI(model="gpt-4o", temperature=0)


def supervisor_node(state: MultiAgentState) -> dict:
    """
    Reads the full state and decides which agent runs next.
    Returns {"next_agent": "researcher"|"writer"|"reviewer"|"DONE"}
    """
    import json

    status = f"""
Current task: {state['task']}

Research notes collected: {len(state.get('research_notes', []))} items
Draft exists: {'Yes' if state.get('draft') else 'No'}
Review verdict: {state.get('review_verdict', 'none yet')}
Revision count: {state.get('revision_count', 0)}
""".strip()

    messages = [
        SystemMessage(content=SUPERVISOR_SYSTEM),
        HumanMessage(content=f"Current state:\n{status}\n\nWho should act next?"),
    ]

    response = llm.invoke(messages)
    raw = response.content.strip()

    # Parse {"next": "..."} from LLM output
    try:
        # Handle markdown code fences if LLM wraps output
        if "```" in raw:
            raw = raw.split("```")[1].strip()
            if raw.startswith("json"):
                raw = raw[4:].strip()
        data = json.loads(raw)
        next_agent = data.get("next", "DONE")
    except Exception:
        # Fallback: scan for known agent names
        raw_lower = raw.lower()
        if "researcher" in raw_lower:
            next_agent = "researcher"
        elif "writer" in raw_lower:
            next_agent = "writer"
        elif "reviewer" in raw_lower:
            next_agent = "reviewer"
        else:
            next_agent = "DONE"

    print(f"\n[supervisor] → next agent: {next_agent}")
    return {"next_agent": next_agent}