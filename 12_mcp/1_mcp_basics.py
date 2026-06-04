"""
1. MCP Basics — Model Context Protocol: Core Concepts & First Server

Official docs: https://modelcontextprotocol.io/docs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT IS MCP?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MCP (Model Context Protocol) is an open protocol created by Anthropic
that standardizes how AI models (LLMs) connect to external tools,
data sources, and services.

Think of it as USB-C for AI:
  - USB-C  → one standard connector for all devices
  - MCP    → one standard protocol for LLMs to connect to any tool/service

MCP follows a Client-Server architecture:
  ┌─────────────────────────────────────────────────────────┐
  │  HOST (e.g., Claude Desktop, your Python app)           │
  │                                                         │
  │   ┌───────────────┐     ┌───────────────────────────┐  │
  │   │  MCP Client   │────▶│  MCP Server               │  │
  │   │  (AI/LLM app) │◀────│  (tools, resources,       │  │
  │   └───────────────┘     │   prompts)                │  │
  │                         └───────────────────────────┘  │
  └─────────────────────────────────────────────────────────┘

Key building blocks:
  - Tools     : Functions the LLM can call (like plugins)
  - Resources : Data/files the LLM can read (like a filesystem)
  - Prompts   : Reusable prompt templates the server exposes
  - Sampling  : Let the server ask the LLM to generate text

Transport types:
  - stdio    : Subprocess communication (most common for local servers)
  - SSE      : Server-Sent Events over HTTP (for remote servers)
  - WebSocket: Bidirectional streaming (advanced use cases)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THIS EXAMPLE:
  - Creates a minimal FastMCP server with 2 tools
  - Creates a client that connects via stdio transport
  - Lists and calls tools on the server
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import asyncio
import json
import subprocess
import sys
from datetime import datetime

# ── pip install fastmcp mcp ──────────────────────────────────────────────────
# FastMCP is the easiest Python SDK for building MCP servers.
# The `mcp` package provides the base protocol + client utilities.

# ════════════════════════════════════════════════════════════════════════════
# PART A — THE MCP SERVER  (would normally live in its own file, e.g. server.py)
# ════════════════════════════════════════════════════════════════════════════

SERVER_CODE = '''
"""
Minimal MCP Server — exposes two tools: greet and get_time.
Run standalone with: python server.py
Or connect via MCP client using stdio transport.
"""
import json
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# ── 1. Create the FastMCP application ─────────────────────────────────────
# FastMCP handles all the protocol boilerplate for us.
# The name "BasicMCPServer" is what clients see when they list servers.
mcp = FastMCP("BasicMCPServer")


# ── 2. Define Tools using @mcp.tool() decorator ───────────────────────────
# Every @mcp.tool() function becomes a callable tool for the LLM.
# The docstring becomes the tool's description (shown to the LLM).
# Type hints define the tool's input schema (JSON Schema under the hood).

@mcp.tool()
def greet(name: str) -> str:
    """
    Greet a person by name.

    Args:
        name: The name of the person to greet.

    Returns:
        A friendly greeting message.
    """
    return f"Hello, {name}! Welcome to MCP. 🎉"


@mcp.tool()
def get_time(timezone: str = "UTC") -> str:
    """
    Get the current date and time.

    Args:
        timezone: Timezone label (informational only, uses server local time).

    Returns:
        Current datetime as a formatted string.
    """
    now = datetime.now()
    return f"Current time ({timezone}): {now.strftime('%Y-%m-%d %H:%M:%S')}"


# ── 3. Run the server ─────────────────────────────────────────────────────
# mcp.run() starts the server on stdio by default.
# When launched as a subprocess, stdin/stdout carry MCP protocol messages.
if __name__ == "__main__":
    mcp.run()
'''

# ════════════════════════════════════════════════════════════════════════════
# PART B — THE MCP CLIENT  (connects to the server above)
# ════════════════════════════════════════════════════════════════════════════

async def run_mcp_demo():
    """
    Demonstrate MCP basics:
      1. Connect to the server via stdio transport
      2. List available tools
      3. Call the 'greet' tool
      4. Call the 'get_time' tool
    """
    # ── Save the server code to a temp file ───────────────────────────────
    import tempfile, os
    server_file = os.path.join(os.path.dirname(__file__), "_temp_server_basics.py")
    with open(server_file, "w") as f:
        f.write(SERVER_CODE)

    print("=" * 60)
    print("  MCP BASICS DEMO")
    print("=" * 60)
    print()

    try:
        # ── Import MCP client libraries ───────────────────────────────────
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        # ── StdioServerParameters: how to launch our server process ───────
        # MCP over stdio = the client spawns the server as a subprocess,
        # then communicates via stdin/stdout pipes.
        server_params = StdioServerParameters(
            command=sys.executable,      # run with same Python interpreter
            args=[server_file],          # path to our server script
            env=None,                    # inherit environment variables
        )

        print("📡 Connecting to MCP server via stdio transport...")
        print()

        # ── stdio_client: context manager that manages the subprocess ──────
        async with stdio_client(server_params) as (read, write):
            # ── ClientSession: MCP session over the stdio streams ──────────
            # initialize() performs the MCP handshake (capabilities negotiation)
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✅ Connected! MCP handshake complete.\n")

                # ── STEP 1: List tools ─────────────────────────────────────
                print("━━━ Step 1: Discover available tools ━━━━━━━━━━━━━━━")
                tools_result = await session.list_tools()

                print(f"📦 Server exposes {len(tools_result.tools)} tool(s):\n")
                for tool in tools_result.tools:
                    print(f"  🔧 Tool: {tool.name}")
                    print(f"     Description: {tool.description}")
                    print(f"     Input Schema: {json.dumps(tool.inputSchema, indent=6)}")
                    print()

                # ── STEP 2: Call 'greet' tool ──────────────────────────────
                print("━━━ Step 2: Call the 'greet' tool ━━━━━━━━━━━━━━━━━")
                greet_result = await session.call_tool(
                    "greet",
                    arguments={"name": "AI Developer"}
                )
                print(f"📨 Result: {greet_result.content[0].text}")
                print()

                # ── STEP 3: Call 'get_time' tool ───────────────────────────
                print("━━━ Step 3: Call the 'get_time' tool ━━━━━━━━━━━━━━")
                time_result = await session.call_tool(
                    "get_time",
                    arguments={"timezone": "IST"}
                )
                print(f"🕐 Result: {time_result.content[0].text}")
                print()

    finally:
        # Clean up temp server file
        if os.path.exists(server_file):
            os.remove(server_file)

    print("=" * 60)
    print("  KEY TAKEAWAYS")
    print("=" * 60)
    print("""
  1. MCP uses a Client-Server model with JSON-RPC under the hood
  2. FastMCP @mcp.tool() decorator = tool registration (type hints → schema)
  3. stdio transport = server runs as subprocess, comm via stdin/stdout
  4. ClientSession.initialize() = MCP handshake (capabilities negotiation)
  5. session.list_tools() → discover what a server offers
  6. session.call_tool(name, arguments) → invoke a tool
  7. Results come back as Content objects (text, image, embedded resource)
    """)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🔍 MCP Basics Example")
    print("   Demonstrates: Server creation, client connection, tool discovery & calling\n")
    asyncio.run(run_mcp_demo())
