# state.py
import operator
from typing import TypedDict, Annotated

class MultiAgentState(TypedDict):
    # The original task given by the human
    task: str

    # Full conversation / tool output history
    messages: Annotated[list, operator.add]

    # Which specialist agent the supervisor picked next
    next_agent: str

    # Research agent accumulates findings here
    research_notes: Annotated[list, operator.add]

    # Writer deposits draft here
    draft: str

    # Reviewer deposits feedback here
    review_feedback: str

    # Review verdict: "approved" | "needs_revision"
    review_verdict: str

    # How many times the writer has revised
    revision_count: int

    # Final polished output
    final_output: str