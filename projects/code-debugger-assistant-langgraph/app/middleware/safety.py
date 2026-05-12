"""
Safety middleware: blocks tool calls that contain unsafe execution keywords.
Subclasses AgentMiddleware to support both sync and async invocation.
"""
import logging
from langchain.agents.middleware.types import AgentMiddleware

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


class SafetyMiddleware(AgentMiddleware):
    """Intercept tool calls and block any that contain unsafe patterns."""

    def _check(self, request):
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
        return None

    def wrap_tool_call(self, request, handler):
        blocked = self._check(request)
        if blocked:
            return blocked
        return handler(request)

    async def awrap_tool_call(self, request, handler):
        blocked = self._check(request)
        if blocked:
            return blocked
        return await handler(request)


safety_middleware = SafetyMiddleware()
