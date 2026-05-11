"""
Call-limit middleware: prevents runaway tool loops by capping total tool
calls per agent invocation at MAX_TOOL_CALLS (default: 20).
Applied via @wrap_tool_call on the create_agent middleware list.
"""
import logging
from langchain.agents.middleware import wrap_tool_call

logger = logging.getLogger(__name__)

MAX_TOOL_CALLS = 20
_call_counter: dict[str, int] = {}


def reset_counter(thread_id: str) -> None:
    """Reset the call counter for a given thread (call at session start)."""
    _call_counter[thread_id] = 0


@wrap_tool_call
async def limits_middleware(request, handler):
    """Track total tool calls per thread and raise if MAX_TOOL_CALLS is exceeded."""
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
    return await handler(request)
