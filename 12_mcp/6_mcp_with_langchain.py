"""
6. MCP with LangChain — Connecting MCP Servers to LLM Agents

Official docs:
  https://modelcontextprotocol.io/docs
  https://python.langchain.com/docs/integrations/tools/mcp

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHY MCP + LANGCHAIN?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MCP defines HOW to expose tools/resources.
LangChain defines HOW to use them in LLM agents.

Together:
  MCP Server  →  exposes tools (weather, DB, calculator...)
  LangChain   →  LLM agent decides which tools to call
  langchain_mcp_adapters → bridges MCP tools → LangChain tools

The key adapter: langchain-mcp-adapters
  pip install langchain-mcp-adapters

Flow:
  ┌───────────────┐   MCP Protocol   ┌──────────────────┐
  │  LangChain    │◄────────────────►│  MCP Server      │
  │  Agent + LLM  │                  │  (your tools)    │
  └───────────────┘                  └──────────────────┘
          ↑
  langchain_mcp_adapters.tools.load_mcp_tools()
  converts MCP tools → LangChain StructuredTool objects

This example covers:
  ① Load MCP tools into LangChain
  ② Create a LangChain ReAct agent using MCP tools
  ③ Multi-server configuration (connecting to multiple MCPs)
  ④ Using MCP resources as agent context
  ⑤ MCP with OpenAI function calling
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import asyncio
import os
import sys
import json

from dotenv import load_dotenv
load_dotenv()

# ════════════════════════════════════════════════════════════════════════════
# SERVER — A realistic math + data science MCP server
# ════════════════════════════════════════════════════════════════════════════

SERVER_CODE = '''
"""MCP Server for LangChain integration demo."""
import json
import math
import statistics
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DataScienceServer")


@mcp.tool()
def calculate_statistics(numbers: list[float]) -> str:
    """
    Calculate descriptive statistics for a list of numbers.

    Args:
        numbers: A list of numeric values to analyze.

    Returns:
        JSON with mean, median, std_dev, min, max, and count.
    """
    if not numbers:
        raise ValueError("Cannot calculate statistics on an empty list.")

    stats = {
        "count": len(numbers),
        "mean": round(statistics.mean(numbers), 4),
        "median": round(statistics.median(numbers), 4),
        "std_dev": round(statistics.stdev(numbers), 4) if len(numbers) > 1 else 0,
        "minimum": min(numbers),
        "maximum": max(numbers),
        "range": max(numbers) - min(numbers),
    }
    return json.dumps(stats, indent=2)


@mcp.tool()
def solve_equation(equation_type: str, coefficients: list[float]) -> str:
    """
    Solve common mathematical equations.

    Args:
        equation_type: Type of equation: 'linear' (ax + b = 0) or
                       'quadratic' (ax² + bx + c = 0).
        coefficients: List of coefficients [a, b] for linear or
                      [a, b, c] for quadratic.

    Returns:
        Solution(s) as a JSON string.
    """
    if equation_type == "linear":
        if len(coefficients) != 2:
            raise ValueError("Linear equation needs exactly 2 coefficients [a, b].")
        a, b = coefficients
        if a == 0:
            raise ValueError("Coefficient 'a' cannot be zero for linear equation.")
        x = -b / a
        return json.dumps({"equation": f"{a}x + {b} = 0", "solution": f"x = {x:.4f}"})

    elif equation_type == "quadratic":
        if len(coefficients) != 3:
            raise ValueError("Quadratic equation needs exactly 3 coefficients [a, b, c].")
        a, b, c = coefficients
        if a == 0:
            raise ValueError("Coefficient 'a' cannot be zero for quadratic equation.")
        discriminant = b**2 - 4*a*c
        if discriminant > 0:
            x1 = (-b + math.sqrt(discriminant)) / (2*a)
            x2 = (-b - math.sqrt(discriminant)) / (2*a)
            solutions = [round(x1, 4), round(x2, 4)]
            nature = "two real roots"
        elif discriminant == 0:
            x = -b / (2*a)
            solutions = [round(x, 4)]
            nature = "one repeated root"
        else:
            real = -b / (2*a)
            imag = math.sqrt(-discriminant) / (2*a)
            solutions = [f"{round(real,4)} ± {round(imag,4)}i"]
            nature = "complex roots"
        return json.dumps({
            "equation": f"{a}x² + {b}x + {c} = 0",
            "discriminant": discriminant,
            "nature": nature,
            "solutions": solutions
        }, indent=2)

    else:
        raise ValueError(f"Unknown equation_type '{equation_type}'. Use 'linear' or 'quadratic'.")


@mcp.tool()
def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """
    Convert between common measurement units.

    Args:
        value: The numeric value to convert.
        from_unit: Source unit (e.g., 'km', 'miles', 'kg', 'lbs', 'celsius', 'fahrenheit').
        to_unit: Target unit.

    Returns:
        Converted value with units.
    """
    # Conversion table (all values relative to SI base unit)
    conversions = {
        # Distance (base: meters)
        "km": ("distance", 1000), "miles": ("distance", 1609.344),
        "meters": ("distance", 1), "feet": ("distance", 0.3048),
        "cm": ("distance", 0.01), "inches": ("distance", 0.0254),
        # Weight (base: kg)
        "kg": ("weight", 1), "lbs": ("weight", 0.453592),
        "grams": ("weight", 0.001), "ounces": ("weight", 0.0283495),
    }

    # Special temperature handling
    temp_units = {"celsius", "fahrenheit", "kelvin"}
    if from_unit.lower() in temp_units and to_unit.lower() in temp_units:
        f, t = from_unit.lower(), to_unit.lower()
        if f == "celsius" and t == "fahrenheit": result = value * 9/5 + 32
        elif f == "fahrenheit" and t == "celsius": result = (value - 32) * 5/9
        elif f == "celsius" and t == "kelvin": result = value + 273.15
        elif f == "kelvin" and t == "celsius": result = value - 273.15
        elif f == "fahrenheit" and t == "kelvin": result = (value - 32) * 5/9 + 273.15
        elif f == "kelvin" and t == "fahrenheit": result = (value - 273.15) * 9/5 + 32
        else: result = value
        return f"{value} {from_unit} = {round(result, 4)} {to_unit}"

    # General conversion via SI base
    from_key, to_key = from_unit.lower(), to_unit.lower()
    if from_key not in conversions or to_key not in conversions:
        raise ValueError(f"Unknown units: '{from_unit}' or '{to_unit}'")

    from_cat, from_factor = conversions[from_key]
    to_cat, to_factor = conversions[to_key]

    if from_cat != to_cat:
        raise ValueError(f"Cannot convert {from_cat} to {to_cat}.")

    result = value * from_factor / to_factor
    return f"{value} {from_unit} = {round(result, 6)} {to_unit}"


@mcp.resource("data://sample/dataset")
def get_sample_dataset() -> str:
    """A sample dataset for demonstrating data analysis."""
    dataset = {
        "name": "Monthly Sales Data 2024",
        "columns": ["month", "revenue_usd", "units_sold", "avg_price"],
        "data": [
            ["Jan", 45200, 451, 100.2],
            ["Feb", 38700, 387, 100.0],
            ["Mar", 52100, 473, 110.1],
            ["Apr", 61300, 520, 117.9],
            ["May", 58900, 503, 117.1],
            ["Jun", 71200, 594, 119.9],
        ]
    }
    return json.dumps(dataset, indent=2)


if __name__ == "__main__":
    mcp.run()
'''

# ════════════════════════════════════════════════════════════════════════════
# LANGCHAIN INTEGRATION — Load MCP tools and use them in an agent
# ════════════════════════════════════════════════════════════════════════════

async def demo_langchain_mcp():
    """Demonstrate LangChain agent using MCP tools."""
    server_file = os.path.join(os.path.dirname(__file__), "_temp_server_langchain.py")
    with open(server_file, "w") as f:
        f.write(SERVER_CODE)

    print("=" * 65)
    print("  MCP + LANGCHAIN INTEGRATION DEMO")
    print("=" * 65)
    print()

    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        # ── Check for LangChain MCP adapters ──────────────────────────────
        try:
            from langchain_mcp_adapters.tools import load_mcp_tools
            HAS_LC_MCP = True
        except ImportError:
            HAS_LC_MCP = False
            print("⚠️  langchain-mcp-adapters not installed.")
            print("   Install with: pip install langchain-mcp-adapters langchain-openai")
            print()

        server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_file],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✅ Connected to DataScienceServer\n")

                # ── ① Load MCP tools as LangChain tools ───────────────────
                print("━━━ ① Load MCP Tools into LangChain ━━━━━━━━━━━━━━━━━")
                if HAS_LC_MCP:
                    # load_mcp_tools(): converts MCP tool schemas → LangChain StructuredTool
                    lc_tools = await load_mcp_tools(session)
                    print(f"   ✔ Loaded {len(lc_tools)} MCP tools as LangChain tools:\n")
                    for tool in lc_tools:
                        print(f"     🔧 {tool.name}: {tool.description[:60]}...")
                    print()
                else:
                    print("   Showing manual tool loading approach...\n")
                    # Manual approach: wrap MCP calls as LangChain tools
                    raw_tools = await session.list_tools()
                    print(f"   Raw MCP tools (manual conversion needed): {len(raw_tools.tools)}")
                    for t in raw_tools.tools:
                        print(f"     🔧 {t.name}")
                    print()

                # ── ② Manual tool invocation (always works) ────────────────
                print("━━━ ② Manual MCP Tool Calls via LangChain Session ━━━")

                # Calculate statistics on sales data
                print("   📊 Calculating statistics on revenue data...")
                stats_result = await session.call_tool(
                    "calculate_statistics",
                    arguments={"numbers": [45200, 38700, 52100, 61300, 58900, 71200]}
                )
                print(f"   ✔ Revenue Statistics:\n{stats_result.content[0].text}")

                print("   📐 Solving quadratic equation: x² - 5x + 6 = 0")
                eq_result = await session.call_tool(
                    "solve_equation",
                    arguments={
                        "equation_type": "quadratic",
                        "coefficients": [1, -5, 6]
                    }
                )
                print(f"   ✔ Solution:\n{eq_result.content[0].text}")

                print("   📏 Converting units: 100 km → miles")
                unit_result = await session.call_tool(
                    "convert_units",
                    arguments={"value": 100, "from_unit": "km", "to_unit": "miles"}
                )
                print(f"   ✔ {unit_result.content[0].text}\n")

                # ── ③ Read resource ────────────────────────────────────────
                print("━━━ ③ MCP Resource as Agent Context ━━━━━━━━━━━━━━━━━")
                dataset_resource = await session.read_resource("data://sample/dataset")
                dataset = json.loads(dataset_resource.contents[0].text)
                print(f"   📁 Loaded dataset: '{dataset['name']}'")
                print(f"   Columns: {dataset['columns']}")
                print(f"   Rows: {len(dataset['data'])}\n")

                # Analyze dataset using tools
                revenues = [row[1] for row in dataset["data"]]
                stats_result = await session.call_tool(
                    "calculate_statistics",
                    arguments={"numbers": revenues}
                )
                print(f"   📊 Revenue statistics:\n{stats_result.content[0].text}")

                # ── ④ Show LangChain agent code pattern ───────────────────
                print("━━━ ④ LangChain Agent Code Pattern (Reference) ━━━━━━━")
                print("""
   # Full LangChain agent using MCP tools:

   from langchain_openai import ChatOpenAI
   from langchain.agents import create_tool_calling_agent, AgentExecutor
   from langchain_mcp_adapters.tools import load_mcp_tools
   from langchain_core.prompts import ChatPromptTemplate

   async with stdio_client(server_params) as (read, write):
       async with ClientSession(read, write) as session:
           await session.initialize()

           # Load ALL MCP tools as LangChain tools
           tools = await load_mcp_tools(session)

           # Create LLM
           llm = ChatOpenAI(model="gpt-4o-mini")

           # Create agent that can call MCP tools
           prompt = ChatPromptTemplate.from_messages([
               ("system", "You are a helpful data science assistant."),
               ("human", "{input}"),
               ("placeholder", "{agent_scratchpad}"),
           ])

           agent = create_tool_calling_agent(llm, tools, prompt)
           executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

           # The agent will automatically decide which MCP tools to call!
           result = await executor.ainvoke({
               "input": "Analyze the dataset and solve x² - 5x + 6 = 0"
           })
                """)

    finally:
        if os.path.exists(server_file):
            os.remove(server_file)

    print("=" * 65)
    print("  KEY TAKEAWAYS — MCP + LangChain")
    print("=" * 65)
    print("""
  ① langchain-mcp-adapters bridges MCP ↔ LangChain tool format
  ② load_mcp_tools(session) → list of LangChain StructuredTool
  ③ LangChain agents can call MCP tools just like native tools
  ④ MCP resources provide context; tools provide actions
  ⑤ Works with any LangChain-compatible LLM (OpenAI, Anthropic...)
  ⑥ Multi-server: connect to multiple MCP servers, merge tools
    """)


if __name__ == "__main__":
    print("\n🔗 MCP + LangChain Integration Example")
    print("   Demonstrates: loading MCP tools into LangChain agents\n")
    asyncio.run(demo_langchain_mcp())
