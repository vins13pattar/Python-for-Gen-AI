# ☁️ Weather MCP Assistant

A minimal yet powerful weather advisory system designed to demonstrate the complete Model Context Protocol (MCP) lifecycle.

This project shows how an **MCP Client** spawns an **MCP Server** over standard I/O streams (`stdio`) to discover and call **Tools**, query **Resources**, and render **Prompts**.

---

## 🏗️ Architecture

```
┌───────────────────────────────────────────────────────────┐
│  HOST / CLIENT (main.py / client_agent.py)                │
│                                                           │
│   ┌────────────────┐   JSON-RPC over   ┌──────────────┐  │
│   │   MCP Client   │ ◄────────────────►│  MCP Server  │  │
│   │  (Python/Stdio)│   stdio pipe      │(weather_srv) │  │
│   └───────┬────────┘                   └──────┬───────┘  │
│           │                                   │          │
│           ▼ load_mcp_tools()                  ▼          │
│    [LangChain adapters]                 [Tools: Weather] │
│                                         [Resources:Alerts]
│                                         [Prompts: Advisers]
└───────────────────────────────────────────────────────────┘
```

---

## 🌟 Key Features

1. **🔧 Weather Tool (`get_weather`)**:
   - Queries a free geocoding API to resolve coordinates (lat/lon) for any city name.
   - Fetches current weather (temperature and wind speed) dynamically via a live forecast API.
   - Gracefully falls back to a high-fidelity local database on network failure or API timeouts (meaning it runs even when offline!).
2. **📂 Read-only Alerts Resource (`weather://alerts/{city}`)**:
   - Exposes dynamic plain-text reports containing severe weather alerts, monsoon notices, and seasonal packing tips.
3. **📝 Parameterized Prompt (`weather_adviser`)**:
   - Generates senior meteorologist system prompt structures and conversation templates optimized for travel advisory agents.
4. **🔌 LangChain Adapter Integration**:
   - Explores loading MCP server schemas into native LangChain `StructuredTool` objects instantly.

---

## 🚀 Setup & Execution

### 1. Prerequisites
Ensure you are using the virtual environment configured in the `12_mcp` directory (which contains all necessary packages: `fastmcp`, `mcp`, `httpx`, `langchain`, etc.).

If you need to set up a new environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Full Demo
The project features a single-click entry point that launches both the server and client seamlessly:

```bash
python main.py
```

This will output:
- Active **handshake and connection** status.
- Automatic **schema compilation** for your tool from Python type hints.
- Live **dynamic tool calls** (fetching actual weather data for Mumbai, Bangalore, and London!).
- Exposing read-only **resources** under the `weather://` custom URI scheme.
- Pre-packaged system and user **prompt templates** rendered dynamically.
- Native **LangChain adapter loading** logs.

---

## 🔍 Core MCP Code Reference

### 1. Creating the Server
We register tools, resources, and prompts using the simple `FastMCP` decorator APIs:

```python
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("WeatherServer")

# Tool registration
@mcp.tool()
async def get_weather(city: str, ctx: Context) -> str:
    """Fetch live weather forecast for a city."""
    ...
    return weather_json

# Resource registration
@mcp.resource("weather://alerts/{city}")
async def get_weather_alerts(city: str, ctx: Context) -> str:
    """Expose plain-text alerts and warnings for a city."""
    ...
    return alert_text

# Prompt registration
@mcp.prompt()
def weather_adviser(city: str, travel_plan: str = "") -> list[dict]:
    """Generates meteorologist travel advisory prompt scaffold."""
    ...
```

### 2. Client Transport Setup
The client connects to the server script as a subprocess via standard input and output pipes:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="python",
    args=["weather_server.py"]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        
        # Discover tools
        tools = await session.list_tools()
        
        # Call a tool
        result = await session.call_tool("get_weather", {"city": "mumbai"})
```
