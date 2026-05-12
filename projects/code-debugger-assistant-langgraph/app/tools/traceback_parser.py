import json
import langsmith as ls
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing import Optional
from app.tools.utils import get_safe_writer

from app.prompts.debugger_prompt import PARSE_TRACEBACK_PROMPT


class TracebackDetails(BaseModel):
    error_type: str = Field(description="Type of error, e.g. NameError, TypeError")
    error_message: str = Field(description="The exact error message text")
    affected_line: Optional[int] = Field(default=None, description="Line number where error occurred")
    file_name: Optional[str] = Field(default=None, description="File name if present in traceback")
    severity: str = Field(description="Severity level: low, medium, high, or critical")


@tool
def traceback_parser_tool(error_message: str) -> str:
    """Parse an error message or traceback to extract structured details.

    Call this tool when the user provides an error message or traceback.
    It extracts the error type, line number, file name, and severity.

    Args:
        error_message: The raw error message string or full traceback text.
    """
    # Attach LangSmith metadata to the current trace
    rt = ls.get_current_run_tree()
    if rt:
        rt.name = "TracebackParser"
        rt.metadata.update({"pipeline_step": "traceback_parsing", "tool_type": "analysis"})
        rt.tags = list(set((rt.tags or []) + ["code-debugger", "tool", "traceback-parsing"]))

    writer = get_safe_writer()
    writer("Parsing error traceback...")

    model = init_chat_model("openai:gpt-4.1-mini", temperature=0.0)
    chain = PARSE_TRACEBACK_PROMPT | model.with_structured_output(TracebackDetails)
    result: TracebackDetails = chain.invoke(
        {"error_message": error_message},
        config={
            "run_name": "TracebackParser-Chain",
            "tags": ["code-debugger", "tool", "traceback-parsing"],
            "metadata": {"tool": "traceback_parser_tool", "pipeline_step": "traceback_parsing"},
        },
    )

    writer(f"Error identified: {result.error_type} (severity: {result.severity})")
    return json.dumps(result.model_dump())
