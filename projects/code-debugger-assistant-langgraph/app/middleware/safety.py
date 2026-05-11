"""
Safety middleware: blocks tool calls that contain unsafe execution keywords.
Applied via @wrap_tool_call on the create_agent middleware list.
"""
import logging
from langchain.agents.middleware import wrap_tool_call

logger = logging.getLogger(__name__)

_BLOCKED_PATTERNS = [
    "os.system(",
    "subprocess.",
    "eval(",
    "exec(",
    "rm -rf",
    "drop table",
    "__import__(",
    "shutil.rmtree",
]


@wrap_tool_call
async def safety_middleware(request, handler):
    """Intercept tool calls and block any that contain unsafe patterns."""
    tool_name = request.tool_call["name"]
    serialized_input = str(request.tool_call.get("args", {})).lower()
    flagged = [p for p in _BLOCKED_PATTERNS if p.lower() in serialized_input]

    if flagged:
        msg = (
            f"[SafetyMiddleware] Blocked tool '{tool_name}' — "
            f"unsafe pattern(s) detected: {flagged}"
        )
        logger.warning(msg)
        return (
            f"BLOCKED: This request contains potentially unsafe patterns: {flagged}. "
            "The assistant can only analyze code as text."
        )

    return await handler(request)
