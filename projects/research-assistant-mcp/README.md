# 🔬 Research Assistant System

**Multi-Agent Collaboration with MCP, LangGraph, and CrewAI**

An educational Python mini-application that demonstrates how multiple AI agents collaborate on a research task using **MCP-style structured messages**, **LangGraph stateful workflows**, and **CrewAI role-based agents**.

---

## 🎯 What This Project Demonstrates

| Concept | Implementation |
|---------|---------------|
| **MCP (Model Context Protocol)** | JSON-schema validated agent messages, shared tools & resources |
| **Agent-to-agent communication** | 6 agents passing structured MCP messages through shared state |
| **Shared context store** | `ResearchState` TypedDict accessible by all agents |
| **Embeddings sharing** | Mock/real vector embeddings reused across Embedding → Analyst agents |
| **LangGraph orchestration** | Stateful workflow with conditional critic feedback loop |
| **CrewAI role definitions** | Role, goal, and backstory for each agent |
| **JSON Schema validation** | Every message validated before entering shared state |

---

## 🏗️ Architecture

```
User CLI Input (Research Topic)
         │
         ▼
┌─────────────────────────────────┐
│       LangGraph Workflow         │
│       (Stateful Pipeline)        │
└─────────────────────────────────┘
         │
         ▼
┌──────────────┐    ┌──────────────────────────────────┐
│  Planner     │    │                                  │
│  Agent       │───▶│   MCP Shared Context Store        │
└──────┬───────┘    │                                  │
       ▼            │  ┌─────────────────────────────┐ │
┌──────────────┐    │  │  ResearchState TypedDict     │ │
│  Retriever   │    │  │  - research_questions        │ │
│  Agent       │───▶│  │  - retrieved_context         │ │
└──────┬───────┘    │  │  - embeddings                │ │
       ▼            │  │  - findings                  │ │
┌──────────────┐    │  │  - critique                  │ │
│  Embedding   │    │  │  - agent_messages            │ │
│  Agent       │───▶│  └─────────────────────────────┘ │
└──────┬───────┘    │                                  │
       ▼            │  MCP Tools:                       │
┌──────────────┐    │  ├── save_context()              │
│  Analyst     │    │  ├── get_context()               │
│  Agent       │◀──▶│  ├── save_embedding()            │
└──────┬───────┘    │  ├── search_context()            │
       ▼            │  └── log_agent_message()         │
┌──────────────┐    │                                  │
│  Critic      │───▶│  MCP Resources:                  │
│  Agent       │    │  ├── research://session/{id}     │
└──────┬───────┘    │  ├── research://context/{id}     │
  ┌────┴────┐       │  ├── research://embeddings/{id}  │
  │ needs   │       │  └── research://messages/{id}    │
  │ improve │       └──────────────────────────────────┘
  └────┬────┘
  ↑    ▼ approved
  │  ┌──────────────┐
  │  │   Writer     │
  │  │   Agent      │
  │  └──────┬───────┘
  │          ▼
  │    Final Report (MD)
  │    + JSON Exports
  └── (retry loop, max 2)
```

---

## 🤝 Agent Roster

| Agent | Role | MCP Message Sent |
|-------|------|-----------------|
| **Planner** | Generates 4-6 prioritized research questions | `research_plan_created` |
| **Retriever** | Fetches context from knowledge base | `context_retrieved` |
| **Embedding** | Creates vector embeddings for semantic search | `embeddings_created` |
| **Analyst** | Extracts insights using semantic similarity | `findings_created` |
| **Critic** | Reviews quality and routes workflow | `critique_created` |
| **Writer** | Generates final Markdown report | `final_report_created` |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) package manager

### Installation

```bash
# Clone / navigate to project
cd research-assistant-mcp

# Install dependencies
uv sync

# Copy environment template
cp .env.example .env
```

### Run in Demo Mode (No API Key Needed!)

```bash
# Uses mock LLM responses and mock embeddings by default
uv run python app/main.py --topic "Impact of AI agents on software development"
```

### Run with Real OpenAI

```bash
# Add your key to .env
echo "OPENAI_API_KEY=sk-your-key" >> .env
echo "USE_MOCK_LLM=false" >> .env
echo "USE_MOCK_EMBEDDINGS=false" >> .env

uv run python app/main.py --topic "MCP for multi-agent systems"
```

### All CLI Options

```bash
# Basic usage
uv run python app/main.py --topic "Your Research Topic"

# Export report to custom file
uv run python app/main.py --topic "AI in healthcare" --export my_report.md

# Show all agent messages in terminal
uv run python app/main.py --topic "Agentic AI" --show-messages

# Show CrewAI agent role definitions
uv run python app/main.py --topic "LangGraph" --show-crew

# Enable verbose debug logging
uv run python app/main.py --topic "MCP" --debug
```

---

## 📁 Project Structure

```
research-assistant-mcp/
│
├── docs/
│   └── PRD.md                    ← Full Product Requirements Document
│
├── app/
│   ├── main.py                   ← CLI entry point (Typer)
│   ├── config.py                 ← Environment configuration
│   │
│   ├── schemas/
│   │   ├── mcp_message_schema.json   ← JSON Schema for agent messages
│   │   └── tool_input_schemas.json   ← JSON Schema for MCP tool inputs
│   │
│   ├── state/
│   │   ├── research_state.py     ← ResearchState TypedDict
│   │   └── state_store.py        ← In-memory singleton state store
│   │
│   ├── validation/
│   │   └── message_validator.py  ← jsonschema validation + helpers
│   │
│   ├── mcp_server/
│   │   ├── server.py             ← FastMCP server (5 tools, 4 resources)
│   │   ├── tools.py              ← MCP tool implementations
│   │   └── resources.py          ← MCP resource implementations
│   │
│   ├── agents/
│   │   ├── planner_agent.py      ← Research Planner
│   │   ├── retriever_agent.py    ← Context Retriever
│   │   ├── embedding_agent.py    ← Embedding Generator
│   │   ├── analyst_agent.py      ← Insight Analyst
│   │   ├── critic_agent.py       ← Quality Critic (+ routing logic)
│   │   └── writer_agent.py       ← Report Writer
│   │
│   ├── graph/
│   │   ├── nodes.py              ← LangGraph node wrappers
│   │   └── workflow.py           ← StateGraph with conditional routing
│   │
│   ├── crew/
│   │   ├── crew_config.py        ← CrewAI Agent definitions
│   │   └── tasks.py              ← CrewAI Task definitions
│   │
│   ├── embeddings/
│   │   └── embedding_service.py  ← Mock/real embeddings + cosine search
│   │
│   ├── knowledge/
│   │   ├── mcp_overview.md       ← Local knowledge: MCP
│   │   └── ai_agents_overview.md ← Local knowledge: AI agents
│   │
│   └── outputs/                  ← Generated at runtime
│       ├── research_state.json
│       ├── agent_messages.json
│       ├── embeddings.json
│       └── final_report.md
│
└── tests/
    ├── test_message_schema.py    ← MCP schema validation tests
    ├── test_state.py             ← State store tests
    ├── test_agents.py            ← Individual agent tests
    └── test_workflow.py          ← End-to-end workflow tests
```

---

## 🧪 Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_message_schema.py -v

# Run with coverage
uv run pytest tests/ --cov=app -v
```

---

## 📤 Output Files

After each run, the system generates:

| File | Contents |
|------|---------|
| `app/outputs/research_state.json` | Complete shared state (all fields) |
| `app/outputs/agent_messages.json` | All 6+ MCP agent messages |
| `app/outputs/embeddings.json` | All embedding records |
| `app/outputs/final_report.md` | Final Markdown research report |

---

## 🔑 Configuration

All settings live in `.env`:

```env
# API Settings (optional in mock mode)
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# Mock mode (true = no API key needed)
USE_MOCK_LLM=true
USE_MOCK_EMBEDDINGS=true

# Research settings
RESEARCH_TOPIC=Impact of AI agents on software development
MAX_CRITIC_RETRIES=2

# Logging
LOG_LEVEL=INFO
```

---

## 📚 Key Learning Concepts

### 1. MCP Message Structure

Every agent communicates using this validated format:

```json
{
  "message_id": "msg_001",
  "session_id": "research_abc123",
  "sender_agent": "planner_agent",
  "receiver_agent": "retriever_agent",
  "message_type": "research_plan_created",
  "timestamp": "2026-05-28T10:00:00Z",
  "payload": {
    "questions": ["What is MCP?", "How does MCP enable context sharing?"]
  },
  "metadata": {
    "priority": "high"
  }
}
```

### 2. Shared State (MCP Context Layer)

```python
class ResearchState(TypedDict):
    session_id: str
    topic: str
    research_questions: list[ResearchQuestion]
    retrieved_context: list[ContextChunk]
    embeddings: list[EmbeddingRecord]
    findings: list[Finding]
    critique: list[str]
    critique_status: str
    agent_messages: list[AgentMessage]
    final_report: str
```

### 3. LangGraph Conditional Routing

```python
graph.add_conditional_edges(
    "critic",
    route_after_critic,
    {
        "retry": "retriever",   # ← loop back for more context
        "write": "writer",      # ← proceed to final report
    },
)
```

### 4. CrewAI Role-Based Agents

```python
Agent(
    role="Research Planner",
    goal="Transform broad topics into focused research questions",
    backstory="Expert research strategist with 15 years of experience...",
)
```

---

## 🛣️ Future Enhancements

- [ ] Web UI (Streamlit)
- [ ] Real web search integration
- [ ] Vector DB (Qdrant or Chroma)
- [ ] Human approval before final report
- [ ] PDF upload support
- [ ] Multi-session memory
- [ ] Evaluation agent (score report quality)
- [ ] Citation manager

---

## 📜 License

Educational use only. Built for the **Python for Gen AI** course.

---

*Research Assistant System | MCP + LangGraph + CrewAI Demo*
