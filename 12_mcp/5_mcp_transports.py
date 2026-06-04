"""
5. MCP Transports — stdio, SSE & HTTP Communication Channels

Official docs: https://modelcontextprotocol.io/docs/concepts/transports

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT ARE MCP TRANSPORTS?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Transports define HOW messages are physically carried between
the MCP client and server. The protocol itself is the same —
only the delivery mechanism changes.

MCP Protocol Layer:
  ┌──────────────────────────────────────────────────────┐
  │               JSON-RPC 2.0 Messages                   │
  │   (initialize, tools/list, tools/call, resources/...) │
  └──────────────────────────┬───────────────────────────┘
                             │ sent over
                 ┌───────────┼───────────┐
                 │           │           │
          ┌──────▼──┐  ┌─────▼───┐  ┌───▼────────┐
          │  stdio  │  │   SSE   │  │ WebSocket  │
          │(process)│  │ (HTTP)  │  │(streaming) │
          └─────────┘  └─────────┘  └────────────┘

Transport comparison:
  stdio         → Subprocess pipes (best for local CLI integrations)
                  Used by: Claude Desktop, local agents, IDE plugins
                  
  SSE           → HTTP + Server-Sent Events (remote servers, web clients)
                  Used by: Web apps, remote MCP servers, multi-client
                  
  WebSocket     → Full-duplex streaming (advanced real-time use cases)
                  Used by: Low-latency tools, streaming results
                  
  In-process    → Direct Python calls, no networking (testing/embedding)
                  Used by: Unit tests, embedding server into client

This example covers:
  ① stdio transport (subprocess pipes) — the default
  ② SSE transport (HTTP server) — for remote/multi-client
  ③ In-process transport — for testing without networking
  ④ Custom transport configuration options
  ⑤ Transport error handling and reconnection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import asyncio
import json
import os
import sys
import time
import threading

# ════════════════════════════════════════════════════════════════════════════
# SHARED SERVER LOGIC — used by both stdio and SSE demonstrations
# ════════════════════════════════════════════════════════════════════════════

SHARED_SERVER_CODE = '''
"""Shared MCP server — usable via stdio or SSE transport."""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("TransportDemoServer")

@mcp.tool()
def ping(message: str = "hello") -> str:
    """
    Simple ping tool to test connectivity.

    Args:
        message: Message to echo back.

    Returns:
        Pong response with the message.
    """
    return f"🏓 Pong! You said: '{message}' via {TRANSPORT_TYPE} transport"

@mcp.tool()
def get_transport_info() -> str:
    """
    Return information about the current transport type.

    Returns:
        Transport type and server details.
    """
    import json
    return json.dumps({
        "server_name": "TransportDemoServer",
        "transport": TRANSPORT_TYPE,
        "description": TRANSPORT_DESCRIPTION,
    }, indent=2)


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    if mode == "sse":
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")
'''

STDIO_SERVER_CODE = SHARED_SERVER_CODE.replace(
    "TRANSPORT_TYPE", '"stdio"'
).replace(
    "TRANSPORT_DESCRIPTION", '"subprocess pipes — stdin/stdout communication"'
)

SSE_SERVER_CODE = SHARED_SERVER_CODE.replace(
    "TRANSPORT_TYPE", '"sse"'
).replace(
    "TRANSPORT_DESCRIPTION", '"HTTP + Server-Sent Events — remote/multi-client"'
)


# ════════════════════════════════════════════════════════════════════════════
# TRANSPORT ①: stdio — subprocess pipes
# ════════════════════════════════════════════════════════════════════════════

async def demo_stdio_transport():
    """
    stdio transport: the MCP client launches the server as a subprocess.
    Communication happens through stdin/stdout pipes.

    Pros:
      + Simple, no networking
      + Server lifecycle tied to client
      + No port conflicts
    Cons:
      - Only one client per server process
      - Not suitable for remote/multi-user scenarios
    """
    print("\n" + "━" * 60)
    print("  ① stdio Transport (subprocess pipes)")
    print("━" * 60)

    server_file = os.path.join(os.path.dirname(__file__), "_temp_server_transport_stdio.py")
    with open(server_file, "w") as f:
        f.write(STDIO_SERVER_CODE)

    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        # StdioServerParameters: defines how to launch the server process
        server_params = StdioServerParameters(
            command=sys.executable,       # Python interpreter
            args=[server_file, "stdio"],  # script + transport arg
            env={                         # can pass custom env vars
                **os.environ,
                "MCP_LOG_LEVEL": "ERROR"  # suppress server logs
            }
        )

        print("\n  📡 Launching server as subprocess via stdio...")
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("  ✅ Connected via stdio\n")

                result = await session.call_tool("ping", {"message": "stdio works!"})
                print(f"  ✔ Tool response: {result.content[0].text}")

                result = await session.call_tool("get_transport_info", {})
                info = json.loads(result.content[0].text)
                print(f"  ✔ Transport: {info['transport']}")
                print(f"  ✔ Description: {info['description']}")

    finally:
        if os.path.exists(server_file):
            os.remove(server_file)


# ════════════════════════════════════════════════════════════════════════════
# TRANSPORT ②: SSE (Server-Sent Events) over HTTP
# ════════════════════════════════════════════════════════════════════════════

async def demo_sse_transport():
    """
    SSE transport: the server is a standalone HTTP server.
    Clients connect via HTTP and receive events via SSE stream.

    Pros:
      + Multiple clients can connect simultaneously
      + Server runs independently of clients
      + Works across network boundaries
    Cons:
      - Requires a running HTTP server
      - More complex setup (port, URL, auth)
    """
    print("\n" + "━" * 60)
    print("  ② SSE Transport (HTTP + Server-Sent Events)")
    print("━" * 60)

    server_file = os.path.join(os.path.dirname(__file__), "_temp_server_transport_sse.py")

    # SSE server needs to listen on a port
    sse_server_code = SSE_SERVER_CODE + """
import uvicorn
from mcp.server.fastmcp import FastMCP as _FastMCP

# FastMCP with SSE requires running as an ASGI app via uvicorn
if __name__ == "__main__":
    # mcp.run(transport="sse") starts an HTTP server on port 8765
    # The SSE endpoint will be at http://localhost:8765/sse
    mcp.run(transport="sse", host="127.0.0.1", port=8765)
"""
    with open(server_file, "w") as f:
        f.write(sse_server_code)

    print("\n  📡 SSE Transport Setup:")
    print("  Server command: python server.py  (runs HTTP server on port 8765)")
    print("  SSE endpoint:   http://localhost:8765/sse")
    print()
    print("  Client connection code:")
    print("""
  from mcp.client.sse import sse_client

  async with sse_client("http://localhost:8765/sse") as (read, write):
      async with ClientSession(read, write) as session:
          await session.initialize()
          result = await session.call_tool("ping", {"message": "hi"})
    """)

    print("  ℹ️  SSE demo skipped (requires running HTTP server).")
    print("     Start server with: python _temp_server_sse.py")
    print("     Then use sse_client() to connect.\n")

    # Show how to actually connect (commented demonstration)
    print("  Full SSE client code example:")
    sse_client_demo = '''
async def connect_sse():
    """Connect to a running MCP SSE server."""
    from mcp import ClientSession
    from mcp.client.sse import sse_client

    # Connect to the SSE endpoint
    async with sse_client("http://localhost:8765/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Connected to SSE server!")

            # Call tools same as stdio — transport is transparent!
            result = await session.call_tool("ping", {"message": "SSE works!"})
            print(result.content[0].text)
'''
    print(sse_client_demo)

    if os.path.exists(server_file):
        os.remove(server_file)


# ════════════════════════════════════════════════════════════════════════════
# TRANSPORT ③: In-Process — no networking, direct Python calls (for testing)
# ════════════════════════════════════════════════════════════════════════════

async def demo_in_process_transport():
    """
    In-process transport: server and client share the same Python process.
    No networking, no subprocess — direct async calls.

    Pros:
      + Fastest (no IPC overhead)
      + Ideal for unit tests
      + Easy to inspect server internals
    Cons:
      - Only for testing/embedding, not production
      - Server and client must be in same process
    """
    print("\n" + "━" * 60)
    print("  ③ In-Process Transport (for testing)")
    print("━" * 60)

    try:
        from mcp.server.fastmcp import FastMCP
        from mcp.server import Server
        from mcp import ClientSession
        from mcp.client.session import ClientSession as CS

        # Create a server directly in-process
        test_mcp = FastMCP("InProcessServer")

        @test_mcp.tool()
        def multiply(a: int, b: int) -> str:
            """Multiply two integers."""
            return f"{a} × {b} = {a * b}"

        @test_mcp.tool()
        def greet_in_process(name: str) -> str:
            """Greet someone (in-process demo)."""
            return f"Hello from in-process, {name}!"

        # Use FastMCP's built-in test client
        # FastMCP provides a test() context manager for in-process testing
        print("\n  🧪 Running in-process (no subprocess, no HTTP)...")
        async with test_mcp.test_client() as client:
            # List tools
            tools = await client.list_tools()
            print(f"  ✅ Found {len(tools.tools)} tools in-process:")
            for t in tools.tools:
                print(f"     🔧 {t.name}")

            # Call tools
            result = await client.call_tool("multiply", {"a": 7, "b": 6})
            print(f"\n  ✔ multiply(7, 6): {result.content[0].text}")

            result = await client.call_tool("greet_in_process", {"name": "Tester"})
            print(f"  ✔ greet: {result.content[0].text}")

        print("\n  ✅ In-process transport complete (ideal for unit tests!)")

    except AttributeError:
        # Older versions of FastMCP may not have test_client()
        print("  ℹ️  test_client() not available in this FastMCP version.")
        print("     Use stdio transport with a temp server file for testing.")


# ════════════════════════════════════════════════════════════════════════════
# MAIN — Run all transport demonstrations
# ════════════════════════════════════════════════════════════════════════════

async def main():
    print("=" * 65)
    print("  MCP TRANSPORTS DEMO")
    print("=" * 65)
    print("""
  Transport comparison at a glance:
  ┌──────────────┬──────────────────────────────────────────┐
  │ Transport    │ Best For                                 │
  ├──────────────┼──────────────────────────────────────────┤
  │ stdio        │ Local CLI tools, IDE plugins, agents     │
  │ SSE (HTTP)   │ Remote servers, web apps, multi-client  │
  │ WebSocket    │ Low-latency streaming, real-time tools   │
  │ In-process   │ Unit tests, embedded servers             │
  └──────────────┴──────────────────────────────────────────┘
    """)

    await demo_stdio_transport()
    await demo_sse_transport()
    await demo_in_process_transport()

    print("\n" + "=" * 65)
    print("  KEY TAKEAWAYS — MCP Transports")
    print("=" * 65)
    print("""
  ① stdio   : StdioServerParameters(command, args) → stdio_client()
  ② SSE     : server.run(transport="sse", port=N) → sse_client(url)
  ③ In-proc : FastMCP.test_client() → no networking needed
  ④ Protocol is the SAME across all transports (JSON-RPC 2.0)
  ⑤ Transport choice = deployment concern, not protocol concern
  ⑥ Claude Desktop uses stdio; remote APIs use SSE
    """)


if __name__ == "__main__":
    print("\n🚀 MCP Transports Example")
    print("   Demonstrates: stdio, SSE, in-process transport modes\n")
    asyncio.run(main())
