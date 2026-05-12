"""
Call-limit middleware: prevents runaway tool loops by capping total tool
calls per agent invocation at MAX_TOOL_CALLS (default: 20).
Subclasses AgentMiddleware to support both sync and async invocation.
"""
import logging
from langchain.agents.middleware.types import AgentMiddleware

logger = logging.getLogger(__name__)

MAX_TOOL_CALLS = 20
_call_counter: dict[str, int] = {}


def reset_counter(thread_id: str) -> None:
    """Reset the call counter for a given thread (call at session start)."""
    _call_counter[thread_id] = 0


class LimitsMiddleware(AgentMiddleware):
    """Track total tool calls per thread and raise if MAX_TOOL_CALLS is exceeded."""

    def _check_limit(self, request):
        tool_name = request.tool_call["name"]
        thread_id = "default"
        if request.runtime and hasattr(request.runtime, "config"):
            config = request.runtime.config or {}
            configurable = config.get("configurable", {})
            thread_id = configurable.get("thread_id", "default")

        _call_counter[thread_id] = _call_counter.get(thread_id, 0) + 1
        count = _call_counter[thread_id]

        if count > MAX_TOOL_CALLS:
            msg = (
                f"[LimitsMiddleware] Tool call limit reached ({MAX_TOOL_CALLS}) "
                f"for thread '{thread_id}'. Stopping to prevent runaway loops."
            )
            logger.error(msg)
            raise RuntimeError(msg)

        logger.debug(f"[LimitsMiddleware] Tool call #{count}/{MAX_TOOL_CALLS} — {tool_name!r}")

    def wrap_tool_call(self, request, handler):
        self._check_limit(request)
        return handler(request)

    async def awrap_tool_call(self, request, handler):
        self._check_limit(request)
        return await handler(request)


limits_middleware = LimitsMiddleware()
