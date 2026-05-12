import json
import langsmith as ls
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from app.tools.utils import get_safe_writer

from app.prompts.debugger_prompt import CLASSIFY_BUG_PROMPT


class BugClassification(BaseModel):
    bug_type: str = Field(
        description=(
            "Bug category: Syntax error, Runtime error, Logic error, "
            "Dependency error, API error, Database error, or Configuration error"
        )
    )
    root_cause: str = Field(description="Plain-language explanation of the root cause")


@tool
def bug_classifier_tool(language: str, code: str, parsed_error: str, expected_behavior: str) -> str:
    """Classify the bug category and identify the root cause.

    Call this tool after `traceback_parser_tool`. It analyzes the code,
    parsed error details, and expected behavior to determine what went wrong.

    Args:
        language: Programming language of the code (e.g. python, javascript).
        code: The original source code submitted by the user.
        parsed_error: JSON string of parsed error details from traceback_parser_tool.
        expected_behavior: Description of what the code should do.
    """
    # Attach LangSmith metadata to the current trace
    rt = ls.get_current_run_tree()
    if rt:
        rt.name = "BugClassifier"
        rt.metadata.update({"pipeline_step": "bug_classification", "tool_type": "analysis"})
        rt.tags = list(set((rt.tags or []) + ["code-debugger", "tool", "bug-classification"]))

    writer = get_safe_writer()
    writer("Classifying bug type and root cause...")

    model = init_chat_model("openai:gpt-4.1-mini", temperature=0.2)
    chain = CLASSIFY_BUG_PROMPT | model.with_structured_output(BugClassification)
    result: BugClassification = chain.invoke(
        {
            "language": language,
            "code": code,
            "parsed_error": parsed_error,
            "expected_behavior": expected_behavior or "Not specified",
        },
        config={
            "run_name": "BugClassifier-Chain",
            "tags": ["code-debugger", "tool", "bug-classification"],
            "metadata": {"tool": "bug_classifier_tool", "pipeline_step": "bug_classification"},
        },
    )

    writer(f"Bug classified: {result.bug_type}")
    return json.dumps(result.model_dump())
