"""
2. MCP Tools — Defining, Documenting & Calling Tools with Rich Schemas

Official docs: https://modelcontextprotocol.io/docs/concepts/tools

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT ARE MCP TOOLS?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tools are executable functions that the LLM (or client) can call.
They are the "actions" or "skills" of your MCP server.

Key traits of MCP tools:
  - Defined via JSON Schema (input + output types)
  - Self-describing (name + description guide the LLM's decisions)
  - Stateless by convention (no session state in the tool itself)
  - Can return text, images, or embedded resources

Tool anatomy:
  name        → unique identifier (snake_case recommended)
  description → natural language description (the LLM reads this)
  inputSchema → JSON Schema describing the parameters
  annotations → hints: readOnly, destructive, idempotent, openWorld

This example covers:
  ① Basic tool with primitives (str, int, float, bool)
  ② Tool with Pydantic model as input (complex schema)
  ③ Tool with Optional parameters & defaults
  ④ Tool with enum/Literal type constraints
  ⑤ Tool that returns structured JSON
  ⑥ Tool error handling (raising exceptions)
  ⑦ Tool annotations (readOnly, destructive hints for the LLM)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import asyncio
import json
import os
import sys

# ════════════════════════════════════════════════════════════════════════════
# SERVER — Multiple tool patterns in one server
# ════════════════════════════════════════════════════════════════════════════

SERVER_CODE = '''
"""MCP Tools demo server — showcasing all tool patterns."""
import json
from typing import Optional, Literal
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ToolsDemoServer")


# ─────────────────────────────────────────────────────────────────────────
# ① BASIC TOOL — primitives (str, int, float, bool)
# ─────────────────────────────────────────────────────────────────────────
@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> str:
    """
    Calculate Body Mass Index (BMI).

    Args:
        weight_kg: Weight in kilograms (e.g., 70.5).
        height_m: Height in meters (e.g., 1.75).

    Returns:
        BMI value and health category as a string.
    """
    if height_m <= 0 or weight_kg <= 0:
        raise ValueError("Weight and height must be positive numbers.")

    bmi = weight_kg / (height_m ** 2)

    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"

    return f"BMI: {bmi:.1f} — Category: {category}"


# ─────────────────────────────────────────────────────────────────────────
# ② TOOL WITH PYDANTIC MODEL — complex structured input
# ─────────────────────────────────────────────────────────────────────────
class ProductOrder(BaseModel):
    """Represents an order for a product."""
    product_name: str = Field(description="Name of the product")
    quantity: int = Field(ge=1, le=1000, description="Quantity to order (1-1000)")
    unit_price: float = Field(gt=0, description="Price per unit in USD")
    discount_percent: float = Field(default=0.0, ge=0, le=100, description="Discount percentage")


@mcp.tool()
def calculate_order_total(order: ProductOrder) -> str:
    """
    Calculate the total cost of a product order including discount.

    Args:
        order: A ProductOrder containing product details, quantity, and pricing.

    Returns:
        Order summary with subtotal, discount, and final total.
    """
    subtotal = order.quantity * order.unit_price
    discount_amount = subtotal * (order.discount_percent / 100)
    total = subtotal - discount_amount

    return json.dumps({
        "product": order.product_name,
        "quantity": order.quantity,
        "unit_price": f"${order.unit_price:.2f}",
        "subtotal": f"${subtotal:.2f}",
        "discount": f"-${discount_amount:.2f} ({order.discount_percent}%)",
        "total": f"${total:.2f}",
    }, indent=2)


# ─────────────────────────────────────────────────────────────────────────
# ③ TOOL WITH OPTIONAL PARAMETERS & DEFAULTS
# ─────────────────────────────────────────────────────────────────────────
@mcp.tool()
def search_products(
    query: str,
    category: Optional[str] = None,
    max_price: Optional[float] = None,
    limit: int = 10
) -> str:
    """
    Search for products in the catalog (simulated).

    Args:
        query: Search term or product name.
        category: Optional category filter (e.g., 'electronics', 'clothing').
        max_price: Optional maximum price filter in USD.
        limit: Maximum number of results to return (default 10).

    Returns:
        JSON array of matching products.
    """
    # Simulated product database
    products = [
        {"id": 1, "name": "Laptop Pro", "category": "electronics", "price": 999.99},
        {"id": 2, "name": "Wireless Mouse", "category": "electronics", "price": 29.99},
        {"id": 3, "name": "Running Shoes", "category": "clothing", "price": 89.99},
        {"id": 4, "name": "Coffee Maker", "category": "appliances", "price": 59.99},
        {"id": 5, "name": "Python Book", "category": "books", "price": 39.99},
    ]

    results = [
        p for p in products
        if query.lower() in p["name"].lower()
        and (category is None or p["category"] == category)
        and (max_price is None or p["price"] <= max_price)
    ][:limit]

    return json.dumps({"query": query, "results": results, "count": len(results)}, indent=2)


# ─────────────────────────────────────────────────────────────────────────
# ④ TOOL WITH ENUM / LITERAL TYPE CONSTRAINTS
# ─────────────────────────────────────────────────────────────────────────
@mcp.tool()
def convert_temperature(
    value: float,
    from_unit: Literal["celsius", "fahrenheit", "kelvin"],
    to_unit: Literal["celsius", "fahrenheit", "kelvin"]
) -> str:
    """
    Convert temperature between units.

    Args:
        value: The temperature value to convert.
        from_unit: Source unit: celsius, fahrenheit, or kelvin.
        to_unit: Target unit: celsius, fahrenheit, or kelvin.

    Returns:
        Converted temperature value with units.
    """
    # Convert to Celsius first
    if from_unit == "fahrenheit":
        celsius = (value - 32) * 5 / 9
    elif from_unit == "kelvin":
        celsius = value - 273.15
    else:
        celsius = value

    # Convert from Celsius to target
    if to_unit == "fahrenheit":
        result = (celsius * 9 / 5) + 32
    elif to_unit == "kelvin":
        result = celsius + 273.15
    else:
        result = celsius

    return f"{value}°{from_unit.capitalize()} = {result:.2f}°{to_unit.capitalize()}"


# ─────────────────────────────────────────────────────────────────────────
# ⑤ TOOL THAT RETURNS STRUCTURED JSON
# ─────────────────────────────────────────────────────────────────────────
@mcp.tool()
def get_system_info() -> str:
    """
    Get information about the current system environment.

    Returns:
        JSON object with Python version, platform, and datetime.
    """
    import platform
    from datetime import datetime

    info = {
        "python_version": platform.python_version(),
        "platform": platform.system(),
        "architecture": platform.machine(),
        "processor": platform.processor() or "unknown",
        "timestamp": datetime.now().isoformat(),
    }
    return json.dumps(info, indent=2)


# ─────────────────────────────────────────────────────────────────────────
# ⑥ TOOL ERROR HANDLING — raising exceptions
# ─────────────────────────────────────────────────────────────────────────
@mcp.tool()
def divide_numbers(dividend: float, divisor: float) -> str:
    """
    Divide two numbers, demonstrating proper error handling.

    Args:
        dividend: The number to be divided.
        divisor: The number to divide by (cannot be zero).

    Returns:
        The result of the division.

    Raises:
        ValueError: If divisor is zero.
    """
    if divisor == 0:
        # MCP propagates exceptions as error responses to the client
        raise ValueError("Division by zero is not allowed.")

    result = dividend / divisor
    return f"{dividend} ÷ {divisor} = {result:.4f}"


if __name__ == "__main__":
    mcp.run()
'''

# ════════════════════════════════════════════════════════════════════════════
# CLIENT — Demonstrate all tool patterns
# ════════════════════════════════════════════════════════════════════════════

async def run_tools_demo():
    server_file = os.path.join(os.path.dirname(__file__), "_temp_server_tools.py")
    with open(server_file, "w") as f:
        f.write(SERVER_CODE)

    print("=" * 65)
    print("  MCP TOOLS DEMO — All Tool Patterns")
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
                print("✅ Connected to ToolsDemoServer\n")

                # ── List all tools ─────────────────────────────────────────
                tools = await session.list_tools()
                print(f"📦 Available tools ({len(tools.tools)} total):")
                for t in tools.tools:
                    print(f"   🔧 {t.name}")
                print()

                # ── ① Basic primitives tool ────────────────────────────────
                print("━━━ ① Basic Tool: calculate_bmi ━━━━━━━━━━━━━━━━━━━")
                result = await session.call_tool(
                    "calculate_bmi",
                    arguments={"weight_kg": 75.0, "height_m": 1.80}
                )
                print(f"   ✔ {result.content[0].text}\n")

                # ── ② Pydantic model input ─────────────────────────────────
                print("━━━ ② Pydantic Model Tool: calculate_order_total ━━━━")
                result = await session.call_tool(
                    "calculate_order_total",
                    arguments={
                        "order": {
                            "product_name": "MacBook Pro",
                            "quantity": 2,
                            "unit_price": 1999.99,
                            "discount_percent": 10.0
                        }
                    }
                )
                print(f"   ✔ Order Summary:\n{result.content[0].text}\n")

                # ── ③ Optional params ──────────────────────────────────────
                print("━━━ ③ Optional Params: search_products ━━━━━━━━━━━━━")
                result = await session.call_tool(
                    "search_products",
                    arguments={"query": "laptop", "max_price": 1500}  # category omitted
                )
                print(f"   ✔ {result.content[0].text}\n")

                # ── ④ Enum constraints ─────────────────────────────────────
                print("━━━ ④ Literal/Enum: convert_temperature ━━━━━━━━━━━━")
                result = await session.call_tool(
                    "convert_temperature",
                    arguments={"value": 100, "from_unit": "celsius", "to_unit": "fahrenheit"}
                )
                print(f"   ✔ {result.content[0].text}\n")

                # ── ⑤ Structured JSON return ───────────────────────────────
                print("━━━ ⑤ JSON Return: get_system_info ━━━━━━━━━━━━━━━━")
                result = await session.call_tool("get_system_info", arguments={})
                print(f"   ✔ {result.content[0].text}\n")

                # ── ⑥ Error handling ───────────────────────────────────────
                print("━━━ ⑥ Error Handling: divide_numbers ━━━━━━━━━━━━━━━")
                # Successful call
                result = await session.call_tool(
                    "divide_numbers",
                    arguments={"dividend": 100, "divisor": 7}
                )
                print(f"   ✔ {result.content[0].text}")

                # Error call (divide by zero)
                result = await session.call_tool(
                    "divide_numbers",
                    arguments={"dividend": 5, "divisor": 0}
                )
                print(f"   ✔ Error caught: isError={result.isError}, msg={result.content[0].text}")
                print()

    finally:
        if os.path.exists(server_file):
            os.remove(server_file)

    print("=" * 65)
    print("  KEY TAKEAWAYS — MCP Tools")
    print("=" * 65)
    print("""
  ① Type hints → JSON Schema auto-generated by FastMCP
  ② Pydantic models → complex nested input schema (validated!)
  ③ Optional[T] + default values → optional parameters
  ④ Literal["a","b"] → enum constraints in schema
  ⑤ Return str(json.dumps(...)) for structured data
  ⑥ Raise exceptions → MCP returns isError=True to client
  ⑦ Docstrings = tool descriptions the LLM reads to decide usage
    """)


if __name__ == "__main__":
    print("\n🔧 MCP Tools Example")
    print("   Demonstrates: all tool definition patterns\n")
    asyncio.run(run_tools_demo())
