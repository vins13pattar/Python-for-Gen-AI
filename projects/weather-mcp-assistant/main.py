"""
Weather MCP Assistant — Main Entry Point & Orchestrator.
Spawns the WeatherMCP server and client demo to demonstrate full protocol power.
"""

import asyncio
import os
import sys

def print_premium_banner():
    """Print an eye-catching modern CLI banner."""
    print("=" * 70)
    print(" ☁️  WEATHER MCP ASSISTANT — MINI PROJECT DEMO")
    print("=" * 70)
    print("""
  Architecture flow demonstrated:
  
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
    """)
    print("=" * 70)
    print()

async def main():
    print_premium_banner()
    
    # Resolve paths to the server and client
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(current_dir, "weather_server.py")
    
    if not os.path.exists(server_path):
        print(f"❌ Error: Required server file not found at: {server_path}", file=sys.stderr)
        sys.exit(1)
        
    print(f"🚀 Spawning WeatherMCP Server subprocess: {server_path}")
    print("🔌 Starting connection lifecycle...")
    print()
    
    # Import and run client demonstration
    # A standard Python absolute import or adding to system path is best:
    sys.path.append(current_dir)
    from client_agent import run_client_demo
    
    try:
        await run_client_demo(server_path)
    except Exception as e:
        print(f"\n❌ Execution Error occurred: {str(e)}", file=sys.stderr)
        sys.exit(1)
        
    print("=" * 70)
    print("  KEY CONCEPTS DEMONSTRATED SUCCESSFULLY")
    print("=" * 70)
    print("""
  1. Stdio Subprocess Communication (Client spawns Server and pipes I/O).
  2. Live Geocoding API lookup and real-time Weather Forecast calls.
  3. Safe Local database fallbacks on network error / unknown inputs.
  4. Parameterized read-only resource retrieval (weather://alerts/{city}).
  5. Multi-turn prompt template rendering for travel advisories.
  6. Automatic schema compilation from Python type hints.
  7. Seamless adapter bridge into the LangChain Tool ecosystem.
    """)
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
