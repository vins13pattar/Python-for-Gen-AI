from typing import TypedDict, List, Optional, Annotated
from langgraph.graph.message import add_messages


class DebuggerState(TypedDict):
    # Message history (required by create_agent; reducer appends messages)
    messages: Annotated[list, add_messages]

    # User-submitted debug context
    language: Optional[str]
    code: str
    error_message: Optional[str]
    traceback: Optional[str]
    expected_behavior: Optional[str]

    # Intermediate analysis results
    parsed_error: Optional[dict]
    bug_type: Optional[str]
    root_cause: Optional[str]
    fixed_code: Optional[str]
    changes_made: List[str]
    test_cases: List[str]
    prevention_tips: List[str]

    # Final output
    final_report: Optional[dict]
