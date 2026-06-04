"""
7. MCP Server Context, Lifespan & State Management

Official docs: https://modelcontextprotocol.io/docs/concepts/architecture

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT IS MCP SERVER CONTEXT?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MCP servers often need to:
  - Initialize resources (DB connections, API clients, caches)
  - Share state between tool calls (e.g., a shopping cart)
  - Access request-level context (client info, logging)
  - Clean up on shutdown (close connections, flush buffers)

FastMCP provides several mechanisms:
  - lifespan context manager: startup/shutdown lifecycle hooks
  - mcp.get_context(): access request context inside tools
  - Application-level state: shared across all tool calls
  - Dependencies: inject shared resources into tools

This example covers:
  ① Lifespan management (startup/shutdown hooks)
  ② Shared application state across tool calls
  ③ Request context access (logging, client info)
  ④ Dependencies injection pattern
  ⑤ Progress reporting via context
  ⑥ Server-side caching pattern
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import asyncio
import json
import os
import sys
import time

SERVER_CODE = '''
"""MCP Server with Context, Lifespan & State Management demo."""
import asyncio
import sys
import json
import time
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any
from mcp.server.fastmcp import FastMCP, Context

# ─────────────────────────────────────────────────────────────────────────
# Application state — shared across all tool calls
# ─────────────────────────────────────────────────────────────────────────
@dataclass
class AppState:
    """Shared application state for all tool calls."""
    database_connected: bool = False
    api_client_ready: bool = False
    request_count: int = 0
    cache: dict = field(default_factory=dict)
    startup_time: float = field(default_factory=time.time)
    events: list = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────
# ① LIFESPAN — startup and shutdown hooks
#
# The lifespan context manager runs:
#   - On startup: initialize resources (DB, API clients, caches)
#   - On shutdown: clean up (close connections, flush data)
# The value yielded is available to tools via ctx.request_context.lifespan_context
# ─────────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def app_lifespan(server):
    """
    Application lifespan manager.
    Handles startup and shutdown of shared resources.
    """
    state = AppState()

    # ── STARTUP ───────────────────────────────────────────────────────────
    print("[Server] 🚀 Startup: Initializing resources...", file=sys.stderr, flush=True)

    # Simulate DB connection
    await asyncio.sleep(0.1)  # Simulate async init
    state.database_connected = True
    print("[Server] ✅ Database connected", file=sys.stderr, flush=True)

    # Simulate API client setup
    state.api_client_ready = True
    print("[Server] ✅ API client ready", file=sys.stderr, flush=True)

    state.events.append({"event": "startup", "time": time.time()})
    print("[Server] ✅ Server ready to handle requests", file=sys.stderr, flush=True)

    # Yield state to tools (accessible via ctx.request_context.lifespan_context)
    yield state

    # ── SHUTDOWN ──────────────────────────────────────────────────────────
    print("[Server] 🛑 Shutdown: Cleaning up resources...", file=sys.stderr, flush=True)
    state.database_connected = False
    state.api_client_ready = False
    total_requests = state.request_count
    print(f"[Server] ✅ Served {total_requests} requests. Goodbye!", file=sys.stderr, flush=True)


# Create FastMCP with lifespan
mcp = FastMCP("ContextDemoServer", lifespan=app_lifespan)


# ─────────────────────────────────────────────────────────────────────────
# ② SHARED STATE — tools access and modify shared state
# ─────────────────────────────────────────────────────────────────────────
@mcp.tool()
def get_server_status(ctx: Context) -> str:
    """
    Get current server status including connection states and request count.

    Returns:
        JSON with server status information.
    """
    state: AppState = ctx.request_context.lifespan_context
    state.request_count += 1  # ← mutating shared state

    uptime = time.time() - state.startup_time

    return json.dumps({
        "database_connected": state.database_connected,
        "api_client_ready": state.api_client_ready,
        "total_requests_served": state.request_count,
        "uptime_seconds": round(uptime, 2),
        "cache_entries": len(state.cache),
    }, indent=2)


# ─────────────────────────────────────────────────────────────────────────
# ③ REQUEST CONTEXT — access client info and logger
# ─────────────────────────────────────────────────────────────────────────
@mcp.tool()
async def process_data(data: str, operation: str, ctx: Context) -> str:
    """
    Process data with logging and request context access.

    Args:
        data: The data string to process.
        operation: Processing operation: 'upper', 'lower', 'reverse', 'length'.
        ctx: MCP request context (automatically injected by FastMCP).

    Returns:
        Processed data result.
    """
    state: AppState = ctx.request_context.lifespan_context
    state.request_count += 1

    # ── Access request-level context ───────────────────────────────────
    # ctx.request_context provides access to:
    #   - ctx.info("message")  → structured logging
    #   - ctx.warning("msg")   → warning log
    #   - ctx.error("msg")     → error log
    await ctx.info(f"Processing data: operation='{operation}', length={len(data)}")

    # Process based on operation
    operations = {
        "upper":   lambda d: d.upper(),
        "lower":   lambda d: d.lower(),
        "reverse": lambda d: d[::-1],
        "length":  lambda d: str(len(d)),
    }

    if operation not in operations:
        await ctx.warning(f"Unknown operation '{operation}', defaulting to 'upper'")
        operation = "upper"

    result = operations[operation](data)
    state.events.append({"event": "process_data", "operation": operation})
    await ctx.info(f"Processing complete. Result length: {len(result)}")

    return json.dumps({
        "input": data[:50] + "..." if len(data) > 50 else data,
        "operation": operation,
        "result": result,
        "request_number": state.request_count,
    }, indent=2)


# ─────────────────────────────────────────────────────────────────────────
# ⑥ SERVER-SIDE CACHING — cache expensive operation results
# ─────────────────────────────────────────────────────────────────────────
@mcp.tool()
async def expensive_calculation(n: int, ctx: Context) -> str:
    """
    Perform an expensive calculation with server-side caching.
    First call computes (slow); subsequent calls return from cache (fast).

    Args:
        n: Input number for the calculation.

    Returns:
        Calculation result (from cache if available).
    """
    state: AppState = ctx.request_context.lifespan_context
    state.request_count += 1

    cache_key = f"calc_{n}"

    # Check cache first
    if cache_key in state.cache:
        await ctx.info(f"Cache HIT for key '{cache_key}' ✅")
        cached = state.cache[cache_key]
        return json.dumps({
            "n": n,
            "result": cached["result"],
            "from_cache": True,
            "cached_at": cached["timestamp"],
        }, indent=2)

    # Cache MISS — perform expensive computation
    await ctx.info(f"Cache MISS for key '{cache_key}' — computing...")

    # Simulate expensive computation
    result = sum(i * i for i in range(n))  # sum of squares

    # Store in cache
    state.cache[cache_key] = {
        "result": result,
        "timestamp": time.time(),
        "n": n,
    }
    await ctx.info(f"Computation complete, stored in cache")

    return json.dumps({
        "n": n,
        "result": result,
        "from_cache": False,
        "cache_size": len(state.cache),
    }, indent=2)


# ─────────────────────────────────────────────────────────────────────────
# ⑤ PROGRESS REPORTING — stream progress for long-running tools
# ─────────────────────────────────────────────────────────────────────────
@mcp.tool()
async def long_running_task(steps: int, ctx: Context) -> str:
    """
    Simulate a long-running task with progress reporting via context.

    Args:
        steps: Number of processing steps (1-10).

    Returns:
        Final result after completing all steps.
    """
    state: AppState = ctx.request_context.lifespan_context
    state.request_count += 1

    steps = max(1, min(10, steps))  # clamp to 1-10
    results = []

    for i in range(steps):
        # Report progress via ctx.report_progress
        # progress: current step, total: total steps
        await ctx.report_progress(progress=i, total=steps)
        await ctx.info(f"Step {i+1}/{steps} processing...")

        # Simulate work
        await asyncio.sleep(0.1)
        results.append(f"step_{i+1}_done")

    await ctx.report_progress(progress=steps, total=steps)

    return json.dumps({
        "completed_steps": steps,
        "results": results,
        "status": "complete",
    }, indent=2)


if __name__ == "__main__":
    mcp.run()
'''

async def run_context_demo():
    server_file = os.path.join(os.path.dirname(__file__), "_temp_server_context.py")
    with open(server_file, "w") as f:
        f.write(SERVER_CODE)

    print("=" * 65)
    print("  MCP SERVER CONTEXT & STATE DEMO")
    print("=" * 65)
    print()

    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_file],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✅ Connected (lifespan startup ran automatically)\n")

                # ── ① Server status (shared state) ────────────────────────
                print("━━━ ① Shared State: get_server_status ━━━━━━━━━━━━━━━")
                result = await session.call_tool("get_server_status", {})
                print(f"   {result.content[0].text}\n")

                # ── ③ Request context with logging ─────────────────────────
                print("━━━ ③ Request Context: process_data ━━━━━━━━━━━━━━━━━")
                result = await session.call_tool(
                    "process_data",
                    {"data": "Hello, Model Context Protocol!", "operation": "upper"}
                )
                print(f"   {result.content[0].text}\n")

                # ── ⑥ Caching — first call (miss) ──────────────────────────
                print("━━━ ⑥ Server Caching: expensive_calculation ━━━━━━━━━")
                print("   First call (cache MISS — computing):")
                t0 = time.time()
                result = await session.call_tool("expensive_calculation", {"n": 1000})
                print(f"   ⏱ Time: {(time.time()-t0)*1000:.0f}ms")
                print(f"   {result.content[0].text}")

                print("   Second call (cache HIT — instant):")
                t0 = time.time()
                result = await session.call_tool("expensive_calculation", {"n": 1000})
                print(f"   ⏱ Time: {(time.time()-t0)*1000:.0f}ms")
                print(f"   {result.content[0].text}")

                # ── ⑤ Progress reporting ───────────────────────────────────
                print("━━━ ⑤ Progress Reporting: long_running_task ━━━━━━━━━")
                result = await session.call_tool("long_running_task", {"steps": 5})
                print(f"   {result.content[0].text}")

                # ── Final status check (request_count incremented) ─────────
                print("━━━ Final server status (after all calls) ━━━━━━━━━━━━")
                result = await session.call_tool("get_server_status", {})
                status = json.loads(result.content[0].text)
                print(f"   Total requests served: {status['total_requests_served']}")
                print(f"   Cache entries: {status['cache_entries']}")
                print()

    finally:
        if os.path.exists(server_file):
            os.remove(server_file)

    print("=" * 65)
    print("  KEY TAKEAWAYS — Server Context & Lifecycle")
    print("=" * 65)
    print("""
  ① lifespan=async_ctx_mgr → startup/shutdown hooks in FastMCP
  ② Yielded state → accessible in tools via ctx.lifespan_context
  ③ ctx: Context parameter → automatically injected into tools
  ④ ctx.info() / warning() / error() → structured server-side logs
  ⑤ ctx.report_progress(n, total) → stream progress to client
  ⑥ Shared state (cache, counters) → persists across tool calls
  ⑦ Lifespan cleanup runs automatically when server shuts down
    """)


if __name__ == "__main__":
    print("\n⚙️  MCP Server Context & State Example")
    print("   Demonstrates: lifespan, shared state, logging, caching, progress\n")
    asyncio.run(run_context_demo())
