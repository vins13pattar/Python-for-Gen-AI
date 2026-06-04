"""
3. MCP Resources — Exposing Data & Files to LLMs

Official docs: https://modelcontextprotocol.io/docs/concepts/resources

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT ARE MCP RESOURCES?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Resources represent READ-ONLY data that the LLM can access.
They are like a "filesystem" or "database" the LLM can browse.

Resources vs Tools:
  Tools     → actions (write, compute, call APIs) — the LLM *calls* tools
  Resources → data (read config, files, DB rows)  — the LLM *reads* resources

Resource URI scheme:
  resources use URIs to identify content:
    file:///config/settings.json     → a file resource
    db://customers/42                → a database row resource
    api://weather/london             → a live API resource
    mem://notes/2024-01-01           → an in-memory resource

Resource types:
  - Static  : fixed content (e.g., a configuration file)
  - Dynamic : generated at read time (e.g., a DB query result)
  - Template: URI templates with {params} for parametric access

This example covers:
  ① Static text resource (plain text)
  ② Static JSON resource (structured data)
  ③ Dynamic resource (generated at runtime)
  ④ Resource template (URI with parameters)
  ⑤ File-based resource (reads an actual file)
  ⑥ Resource listing (list_resources)
  ⑦ Resource change notifications
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import asyncio
import json
import os
import sys
import tempfile

SERVER_CODE = '''
"""MCP Resources demo server."""
import json
from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ResourcesDemoServer")


# ─────────────────────────────────────────────────────────────────────────
# ① STATIC TEXT RESOURCE — plain text content, fixed URI
# ─────────────────────────────────────────────────────────────────────────
@mcp.resource("config://app/settings")
def get_app_settings() -> str:
    """
    Application configuration (read-only).
    Returns the app's runtime settings as plain text.
    """
    return """
[Application Settings]
app_name       = MyAIApp
version        = 2.1.0
debug_mode     = false
max_tokens     = 4096
temperature    = 0.7
log_level      = INFO
api_timeout_s  = 30
"""


# ─────────────────────────────────────────────────────────────────────────
# ② STATIC JSON RESOURCE — structured data
# ─────────────────────────────────────────────────────────────────────────
@mcp.resource("db://products/catalog")
def get_product_catalog() -> str:
    """
    Product catalog from the database.
    Returns the full product list as JSON.
    """
    catalog = {
        "updated_at": "2025-01-15",
        "products": [
            {"id": "P001", "name": "AI Starter Kit", "price": 49.99, "stock": 150},
            {"id": "P002", "name": "Pro LLM Pack",   "price": 199.99,"stock": 45},
            {"id": "P003", "name": "Enterprise Suite","price": 999.99,"stock": 12},
        ]
    }
    return json.dumps(catalog, indent=2)


# ─────────────────────────────────────────────────────────────────────────
# ③ DYNAMIC RESOURCE — content generated at read time
# ─────────────────────────────────────────────────────────────────────────
@mcp.resource("api://metrics/live")
def get_live_metrics() -> str:
    """
    Live system metrics (generated at request time).
    Returns current CPU, memory and request stats.
    """
    import random
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": round(random.uniform(10, 80), 1),
        "memory_used_mb": random.randint(512, 4096),
        "requests_per_second": round(random.uniform(50, 500), 2),
        "active_connections": random.randint(5, 200),
        "uptime_hours": round(random.uniform(1, 720), 1),
    }
    return json.dumps(metrics, indent=2)


# ─────────────────────────────────────────────────────────────────────────
# ④ RESOURCE TEMPLATE — parametric URI with {user_id}
#
# Resource templates let clients request resources with dynamic identifiers.
# The URI pattern uses {param_name} placeholders.
# ─────────────────────────────────────────────────────────────────────────
@mcp.resource("db://users/{user_id}/profile")
def get_user_profile(user_id: str) -> str:
    """
    User profile by ID (parametric resource template).
    
    Args:
        user_id: The unique user identifier (from URI).
    
    Returns:
        User profile as JSON. Returns 404-style message if not found.
    """
    # Simulated user database
    users = {
        "u001": {"name": "Alice Chen",  "role": "ML Engineer",   "plan": "pro"},
        "u002": {"name": "Bob Kumar",   "role": "Data Scientist", "plan": "enterprise"},
        "u003": {"name": "Carol Smith", "role": "DevOps Lead",    "plan": "starter"},
    }

    if user_id not in users:
        return json.dumps({"error": f"User '{user_id}' not found", "available_ids": list(users.keys())})

    profile = {"user_id": user_id, **users[user_id], "last_seen": datetime.now().isoformat()}
    return json.dumps(profile, indent=2)


# ─────────────────────────────────────────────────────────────────────────
# ⑤ FILE-BASED RESOURCE — reads from the filesystem at runtime
# ─────────────────────────────────────────────────────────────────────────
DEMO_README_PATH = "/tmp/mcp_demo_readme.md"

# Create a demo file to read
with open(DEMO_README_PATH, "w") as f:
    f.write("""# MCP Resources Demo
This file is served as an MCP resource.

## About
MCP Resources allow LLMs to READ data from various sources:
- Files on the filesystem
- Database records  
- API responses
- In-memory state

## Key Points
- Resources are READ-ONLY (use Tools for writes)
- Resources use URI addressing
- Content can be text, JSON, or binary (base64)
""")

@mcp.resource("file:///tmp/mcp_demo_readme.md")
def get_readme() -> str:
    """
    README file served as a file resource.
    Returns the contents of the demo README.md file.
    """
    with open(DEMO_README_PATH, "r") as f:
        return f.read()


if __name__ == "__main__":
    mcp.run()
'''

async def run_resources_demo():
    server_file = os.path.join(os.path.dirname(__file__), "_temp_server_resources.py")
    with open(server_file, "w") as f:
        f.write(SERVER_CODE)

    print("=" * 65)
    print("  MCP RESOURCES DEMO")
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
                print("✅ Connected to ResourcesDemoServer\n")

                # ── List all resources ─────────────────────────────────────
                print("━━━ ⑥ list_resources() — Discover available resources ━")
                resources_result = await session.list_resources()
                print(f"📚 Server exposes {len(resources_result.resources)} resource(s):\n")
                for r in resources_result.resources:
                    print(f"   📄 URI : {r.uri}")
                    print(f"      Name: {r.name}")
                    print(f"      Desc: {r.description}")
                    print()

                # ── List resource templates ────────────────────────────────
                templates_result = await session.list_resource_templates()
                if templates_result.resourceTemplates:
                    print(f"📋 Resource templates ({len(templates_result.resourceTemplates)}):")
                    for t in templates_result.resourceTemplates:
                        print(f"   📑 Template: {t.uriTemplate}")
                        print(f"      Desc: {t.description}")
                    print()

                # ── ① Static text resource ─────────────────────────────────
                print("━━━ ① Static Text: config://app/settings ━━━━━━━━━━━━")
                result = await session.read_resource("config://app/settings")
                print(result.contents[0].text)

                # ── ② Static JSON resource ─────────────────────────────────
                print("━━━ ② Static JSON: db://products/catalog ━━━━━━━━━━━━━")
                result = await session.read_resource("db://products/catalog")
                print(result.contents[0].text[:300], "...\n")

                # ── ③ Dynamic resource ─────────────────────────────────────
                print("━━━ ③ Dynamic Resource: api://metrics/live ━━━━━━━━━━━")
                result = await session.read_resource("api://metrics/live")
                print(result.contents[0].text)

                # ── ④ Resource template ────────────────────────────────────
                print("━━━ ④ Resource Template: db://users/{user_id}/profile ━")
                result = await session.read_resource("db://users/u002/profile")
                print(f"   User u002 profile:")
                print(result.contents[0].text)

                # ── ⑤ File resource ────────────────────────────────────────
                print("━━━ ⑤ File Resource: file:///tmp/mcp_demo_readme.md ━━")
                result = await session.read_resource("file:///tmp/mcp_demo_readme.md")
                print(result.contents[0].text)

    finally:
        if os.path.exists(server_file):
            os.remove(server_file)

    print("=" * 65)
    print("  KEY TAKEAWAYS — MCP Resources")
    print("=" * 65)
    print("""
  ① @mcp.resource("uri") decorator registers a resource
  ② Resources are READ-ONLY; use Tools for mutations
  ③ URIs use custom schemes: config://, db://, api://, file://
  ④ Resource templates use {param} in URI for dynamic access
  ⑤ Dynamic resources generate content fresh at read time
  ⑥ session.list_resources() → discover all available resources
  ⑦ session.list_resource_templates() → discover URI templates
  ⑧ session.read_resource(uri) → fetch resource content
  ⑨ Content comes back as TextContent or BlobContent (binary)
    """)


if __name__ == "__main__":
    print("\n📂 MCP Resources Example")
    print("   Demonstrates: static, dynamic, template and file resources\n")
    asyncio.run(run_resources_demo())
