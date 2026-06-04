# MCP — Model Context Protocol

Learn MCP from basics to production patterns, with practical, self-contained, runnable examples.

## What is MCP?

**Model Context Protocol (MCP)** is an open protocol by Anthropic that standardizes how AI models connect to external tools, data sources, and services — think of it as **USB-C for AI**.

```
┌──────────────────────────────────────────────────────────────┐
│  HOST  (Claude Desktop / your Python app / IDE plugin)       │
│                                                              │
│   ┌────────────────┐   JSON-RPC 2.0   ┌──────────────────┐  │
│   │   MCP Client   │ ◄──────────────► │   MCP Server     │  │
│   │  (LLM / Agent) │                  │  Tools           │  │
│   └────────────────┘                  │  Resources       │  │
│                                       │  Prompts         │  │
│                                       └──────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## Examples Map

| # | File | Concept | Key APIs |
|---|------|---------|----------|
| 1 | [`1_mcp_basics.py`](1_mcp_basics.py) | Protocol overview, first server & client | `FastMCP`, `ClientSession`, `stdio_client`, `list_tools`, `call_tool` |
| 2 | [`2_mcp_tools.py`](2_mcp_tools.py) | Tool definitions — all schema patterns | `@mcp.tool()`, Pydantic models, `Optional`, `Literal`, error handling |
| 3 | [`3_mcp_resources.py`](3_mcp_resources.py) | Resources — expose data & files to LLMs | `@mcp.resource()`, URI templates, `list_resources`, `read_resource` |
| 4 | [`4_mcp_prompts.py`](4_mcp_prompts.py) | Prompt templates — reusable LLM prompts | `@mcp.prompt()`, multi-turn messages, `list_prompts`, `get_prompt` |
| 5 | [`5_mcp_transports.py`](5_mcp_transports.py) | Transports — stdio, SSE & in-process | `StdioServerParameters`, `sse_client`, `test_client()` |
| 6 | [`6_mcp_with_langchain.py`](6_mcp_with_langchain.py) | MCP + LangChain agent integration | `load_mcp_tools`, `create_tool_calling_agent`, resources as context |
| 7 | [`7_mcp_context_and_state.py`](7_mcp_context_and_state.py) | Server context, lifespan & state | `lifespan=`, `Context`, `ctx.info()`, `report_progress`, caching |

---

## Core MCP Concepts

### 🔧 Tools
Executable functions the LLM can invoke. The **"actions"** of your server.
```python
@mcp.tool()
def greet(name: str) -> str:
    """Greet a person by name."""
    return f"Hello, {name}!"
```

### 📂 Resources
Read-only data the LLM can browse. The **"filesystem"** of your server.
```python
@mcp.resource("db://users/{user_id}/profile")
def get_user(user_id: str) -> str:
    """Return user profile JSON."""
    ...
```

### 📝 Prompts
Reusable message templates the server exposes. Like **"slash commands"**.
```python
@mcp.prompt()
def code_review(code: str, language: str = "python") -> str:
    """Generate a code review prompt."""
    return f"Review this {language} code:\n```\n{code}\n```"
```

### 🚀 Transports
How messages travel between client and server.

| Transport | Use Case | How |
|-----------|----------|-----|
| `stdio` | Local tools, IDE plugins, agents | Subprocess pipes |
| `SSE` | Remote servers, web clients | HTTP + Server-Sent Events |
| `WebSocket` | Low-latency streaming | Full-duplex HTTP |
| In-process | Unit tests, embedded servers | Direct Python calls |

---

## Setup

```bash
cd "12_mcp"

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# Install dependencies
pip install fastmcp mcp python-dotenv
```

### Optional (for LangChain example)
```bash
pip install langchain langchain-openai langchain-mcp-adapters
```

### Environment variables
Create a `.env` file for API key examples:
```
OPENAI_API_KEY=sk-your-key-here
```

---

## Run Examples

Each file is fully self-contained — it embeds the server code and spins it up automatically.

```bash
# 1. MCP Basics — server/client, tool discovery & calling
python 1_mcp_basics.py

# 2. Tools — all schema patterns (Pydantic, Optional, Literal, errors)
python 2_mcp_tools.py

# 3. Resources — static, dynamic, template, file resources
python 3_mcp_resources.py

# 4. Prompts — static, parameterized, multi-turn templates
python 4_mcp_prompts.py

# 5. Transports — stdio, SSE overview, in-process testing
python 5_mcp_transports.py

# 6. MCP + LangChain — load MCP tools into LangChain agents
python 6_mcp_with_langchain.py

# 7. Context & State — lifespan, caching, logging, progress
python 7_mcp_context_and_state.py
```

---

## Architecture Overview

```
                        ┌─────────────────────────────────┐
                        │         MCP SERVER               │
                        │                                  │
  @mcp.tool()      ───► │  Tools      (actions/writes)     │
  @mcp.resource()  ───► │  Resources  (reads/data)         │
  @mcp.prompt()    ───► │  Prompts    (LLM templates)      │
  lifespan=        ───► │  Context    (state/lifecycle)    │
                        └───────────┬─────────────────────┘
                                    │  JSON-RPC 2.0
                          ┌─────────▼──────────┐
                          │    Transport        │
                          │  stdio / SSE / WS   │
                          └─────────┬───────────┘
                                    │
                        ┌───────────▼─────────────────────┐
                        │         MCP CLIENT               │
                        │                                  │
  list_tools()     ◄─── │  Discover tools / resources      │
  call_tool()      ◄─── │  Invoke tools                    │
  read_resource()  ◄─── │  Read resources                  │
  get_prompt()     ◄─── │  Render prompt templates         │
                        └─────────────────────────────────┘
                                    │
                        ┌───────────▼─────────────────────┐
                        │    LLM / Agent Layer             │
                        │  LangChain · LangGraph · CrewAI  │
                        └─────────────────────────────────┘
```

---

## Key Packages

| Package | Purpose |
|---------|---------|
| `fastmcp` | High-level Python SDK for building MCP servers (Pythonic decorator API) |
| `mcp` | Official MCP base library (protocol types, client session, transports) |
| `langchain-mcp-adapters` | Bridge: converts MCP tools → LangChain `StructuredTool` |

---

## MCP vs Other Protocols

| | MCP | REST API | OpenAI Plugins |
|---|-----|----------|----------------|
| **Standard** | Open (Anthropic) | HTTP/REST | OpenAI proprietary |
| **Discovery** | Built-in | Manual/OpenAPI | OpenAPI |
| **Streaming** | Yes (SSE/WS) | Optional | Limited |
| **Resources** | First-class | Endpoints only | No |
| **Prompts** | First-class | No | No |
| **LLM-native** | Yes | No | Yes (OpenAI only) |

---

## Notes

- Each example **embeds the server code** in a `SERVER_CODE` string and writes it to a temp file — so you only need one file per concept.
- Temp files (`_temp_server_*.py`) are created and deleted automatically during each run.
- No API key is needed for examples 1–5 and 7 — they use local Python logic only.
- Example 6 (LangChain) can run without `OPENAI_API_KEY` for the tool-loading demo, but needs a key for full agent invocation.
