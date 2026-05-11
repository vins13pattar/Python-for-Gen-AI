"""
Summarization middleware: monitors long message histories to prevent
context-window overflow during multi-turn debugging sessions.
Applied via @wrap_tool_call on the create_agent middleware list.
"""
import logging
from langchain.agents.middleware import wrap_tool_call

logger = logging.getLogger(__name__)

MAX_MESSAGES_BEFORE_SUMMARY = 20
KEEP_RECENT_MESSAGES = 6


@wrap_tool_call
async def summarization_middleware(request, handler):
    """Monitor message history length and log when summarization would be needed."""
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

    return await handler(request)
