"""
Logging middleware: records every tool call with its inputs and outputs.
Subclasses AgentMiddleware to support both sync and async invocation.
"""
import logging
import time
from langchain.agents.middleware.types import AgentMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("debugger.tools")


class LoggingMiddleware(AgentMiddleware):
    """Log tool name, inputs, output, and execution time."""

    def _log_start(self, request):
        tool_name = request.tool_call["name"]
        tool_args = request.tool_call.get("args", {})
        logger.info(f"→ Tool called: {tool_name!r}  input_keys={list(tool_args.keys())}")
        return tool_name, time.perf_counter()

    def _log_end(self, tool_name, start, result):
        elapsed = (time.perf_counter() - start) * 1000
        output_preview = str(result)[:120].replace("\n", " ")
        logger.info(f"← Tool done:   {tool_name!r}  ({elapsed:.0f} ms)  output={output_preview!r}")

    def wrap_tool_call(self, request, handler):
        tool_name, start = self._log_start(request)
        result = handler(request)
        self._log_end(tool_name, start, result)
        return result

    async def awrap_tool_call(self, request, handler):
        tool_name, start = self._log_start(request)
        result = await handler(request)
        self._log_end(tool_name, start, result)
        return result


logging_middleware = LoggingMiddleware()
