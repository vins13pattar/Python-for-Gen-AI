import json
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing import List
from app.tools.utils import get_safe_writer

from app.prompts.debugger_prompt import GENERATE_FIX_PROMPT


class FixGeneration(BaseModel):
    fixed_code: str = Field(description="The corrected source code")
    changes_made: List[str] = Field(description="List of changes made to the original code")


@tool
def fix_strategy_tool(language: str, code: str, root_cause: str, expected_behavior: str) -> str:
    """Generate corrected code and explain the changes made.

    Call this tool after `bug_classifier_tool`. It produces a minimal fix
    that preserves the original intent and lists every change clearly.

    Args:
        language: Programming language of the code.
        code: The original (broken) source code.
        root_cause: Root cause string from bug_classifier_tool.
        expected_behavior: Description of what the code should do.
    """
    writer = get_safe_writer()
    writer("Generating fix strategy and corrected code...")

    model = init_chat_model("openai:gpt-4.1-mini", temperature=0.2)
    chain = GENERATE_FIX_PROMPT | model.with_structured_output(FixGeneration)
    result: FixGeneration = chain.invoke({
        "language": language,
        "code": code,
        "root_cause": root_cause,
        "expected_behavior": expected_behavior or "Not specified",
    })

    writer(f"Fix generated ({len(result.changes_made)} change(s) made)")
    return json.dumps(result.model_dump())
