# MCP Overview — Model Context Protocol

## What is MCP?

The **Model Context Protocol (MCP)** is an open standard that enables AI applications to connect with external tools, data sources, and context providers in a structured, interoperable way.

MCP was introduced by Anthropic and is designed to solve the problem of AI models needing to access real-world context beyond their training data.

## Core Components

### 1. MCP Hosts
Applications that want to consume context — e.g., AI assistants, IDEs, coding tools.

### 2. MCP Servers
Services that expose tools, resources, and prompts to hosts.

### 3. MCP Clients
Components inside the host that manage connections to MCP servers.

## How MCP Works

```
Host (AI App)
  └── MCP Client
        └── MCP Server
              ├── Tools (callable functions)
              ├── Resources (data sources)
              └── Prompts (reusable templates)
```

## MCP Message Structure

MCP uses JSON-based messages to communicate between components.

A standard tool call in MCP looks like:

```json
{
  "method": "tools/call",
  "params": {
    "name": "save_context",
    "arguments": {
      "session_id": "research_001",
      "chunk": {
        "chunk_id": "chunk_001",
        "text": "MCP enables agents to share tools and context..."
      }
    }
  }
}
```

## MCP Tools

Tools are callable functions exposed by an MCP server.

Example tools in this project:

| Tool | Purpose |
|------|---------|
| `save_context` | Store retrieved context chunks |
| `get_context` | Retrieve stored context |
| `save_embedding` | Store an embedding vector |
| `search_context` | Semantic search over stored context |
| `log_agent_message` | Record agent-to-agent communication |

## MCP Resources

Resources are data providers that agents can read.

Example resources in this project:

| Resource | Description |
|----------|-------------|
| `research://session/{id}` | Current research session data |
| `research://context/{id}` | All retrieved context chunks |
| `research://embeddings/{id}` | Stored embedding records |
| `research://messages/{id}` | Agent message log |

## Why MCP for Multi-Agent Systems?

MCP solves key challenges in multi-agent collaboration:

1. **Standardization**: All agents speak the same protocol
2. **Context Sharing**: Agents read/write shared context through tools
3. **Tool Reuse**: Any agent can call any tool exposed by the server
4. **Decoupling**: Agents don't need direct knowledge of each other
5. **Auditability**: All tool calls are logged and inspectable

## MCP in This Project

In this Research Assistant System, we implement:

- **MCP-style message schemas** for agent-to-agent communication
- **MCP tools** for accessing shared research context
- **MCP resources** for exposing session state to agents
- **JSON Schema validation** to ensure message integrity

The shared context store acts as the "memory" of the MCP server, with all agents reading and writing through defined tools rather than direct memory access.

## Benefits Demonstrated

- Agents can collaborate without knowing each other's implementation
- Context retrieved by one agent is immediately available to all others
- Embeddings created by the Embedding Agent can be reused by the Analyst Agent
- All communication is structured, validated, and auditable
