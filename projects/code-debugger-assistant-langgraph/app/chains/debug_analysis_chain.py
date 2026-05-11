"""
LCEL chain: Debug Analysis
Classifies the bug type and root cause from code + parsed error.
"""
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

from app.prompts.debugger_prompt import CLASSIFY_BUG_PROMPT


class BugClassification(BaseModel):
    bug_type: str = Field(description="Bug category")
    root_cause: str = Field(description="Plain-language root cause explanation")


def get_debug_analysis_chain():
    """Return the debug analysis LCEL chain (lazy, so .env is loaded first)."""
    model = init_chat_model("openai:gpt-4.1-mini", temperature=0.2)
    return CLASSIFY_BUG_PROMPT | model.with_structured_output(BugClassification)
