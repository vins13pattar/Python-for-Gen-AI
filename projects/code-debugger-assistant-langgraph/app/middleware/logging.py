"""
Logging middleware: records every tool call with its inputs and outputs.
Applied via @wrap_tool_call on the create_agent middleware list.
"""
import logging
import time
from langchain.agents.middleware import wrap_tool_call

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("debugger.tools")


@wrap_tool_call
async def logging_middleware(request, handler):
    """Log tool name, inputs, output, and execution time."""
    tool_name = request.tool_call["name"]
    tool_args = request.tool_call.get("args", {})

    start = time.perf_counter()
    logger.info(f"→ Tool called: {tool_name!r}  input_keys={list(tool_args.keys())}")

    result = await handler(request)

    elapsed = (time.perf_counter() - start) * 1000
    output_preview = str(result)[:120].replace("\n", " ")
    logger.info(f"← Tool done:   {tool_name!r}  ({elapsed:.0f} ms)  output={output_preview!r}")

    return result
