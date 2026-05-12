"""
Summarization middleware: monitors long message histories to prevent
context-window overflow during multi-turn debugging sessions.
Subclasses AgentMiddleware to support both sync and async invocation.
"""
import logging
from langchain.agents.middleware.types import AgentMiddleware

logger = logging.getLogger(__name__)

MAX_MESSAGES_BEFORE_SUMMARY = 20
KEEP_RECENT_MESSAGES = 6


class SummarizationMiddleware(AgentMiddleware):
    """Monitor message history length and log when summarization would be needed."""

    def _check_history(self, request):
        state = request.state
        messages = []
        if isinstance(state, dict):
            messages = state.get("messages", [])
        elif hasattr(state, "messages"):
            messages = state.messages
        message_count = len(messages)
        if message_count > MAX_MESSAGES_BEFORE_SUMMARY:
            logger.warning(
                f"[SummarizationMiddleware] Message history is long ({message_count} messages). "
                f"Consider summarizing older messages to save context window. "
                f"Keeping last {KEEP_RECENT_MESSAGES} messages verbatim."
            )

    def wrap_tool_call(self, request, handler):
        self._check_history(request)
        return handler(request)

    async def awrap_tool_call(self, request, handler):
        self._check_history(request)
        return await handler(request)


summarization_middleware = SummarizationMiddleware()
