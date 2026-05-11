"""
Retry middleware: retries tool calls on transient failures (timeouts,
rate limits, temporary API errors).
Applied via @wrap_tool_call on the create_agent middleware list.
"""
import asyncio
import logging
from langchain.agents.middleware import wrap_tool_call

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1.0
RETRYABLE_EXCEPTIONS = (
    TimeoutError,
    ConnectionError,
    OSError,
)


@wrap_tool_call
async def retry_middleware(request, handler):
    """Retry tool calls up to MAX_RETRIES times on transient failures."""
    tool_name = request.tool_call["name"]
    last_exception = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = await handler(request)
            if attempt > 1:
                logger.info(
                    f"[RetryMiddleware] Tool '{tool_name}' succeeded on attempt {attempt}/{MAX_RETRIES}"
                )
            return result

        except RETRYABLE_EXCEPTIONS as exc:
            last_exception = exc
            delay = RETRY_DELAY_SECONDS * (2 ** (attempt - 1))
            logger.warning(
                f"[RetryMiddleware] Tool '{tool_name}' failed (attempt {attempt}/{MAX_RETRIES}): "
                f"{type(exc).__name__}: {exc}. Retrying in {delay:.1f}s..."
            )
            await asyncio.sleep(delay)

        except Exception as exc:
            logger.error(
                f"[RetryMiddleware] Tool '{tool_name}' failed with non-retryable error: "
                f"{type(exc).__name__}: {exc}"
            )
            raise

    logger.error(
        f"[RetryMiddleware] Tool '{tool_name}' failed after {MAX_RETRIES} attempts. "
        f"Last error: {last_exception}"
    )
    raise last_exception
