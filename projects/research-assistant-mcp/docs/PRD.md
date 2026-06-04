# Product Requirements Document

## Mini Application: Research Assistant System

### Multi-Agent Collaboration with Shared State via MCP

---

## 1. Product Summary

**Research Assistant System** is a mini Python application that demonstrates how multiple AI agents collaborate on a research task using a shared context layer powered by **MCP — Model Context Protocol**.

The system will allow a user to enter a research topic such as:

> "Impact of Generative AI on Software Testing"

The application will coordinate multiple agents to:

1. Understand the user's research question.
2. Break the question into subtopics.
3. Search or retrieve relevant context.
4. Share findings through MCP-style structured messages.
5. Store shared context and embeddings.
6. Generate a final research summary.
7. Validate agent messages using JSON Schema.
8. Demonstrate agent-to-agent communication and shared state.

The project is mainly educational and should help learners understand:

* MCP overview and message structure
* Basic agent-to-agent communication
* Context sharing using MCP
* Embeddings sharing between agents
* Multi-agent coordination using LangGraph and CrewAI
* Structured message validation using `jsonschema`

---

## 2. Target Users

### Primary Users

| User Type             | Need                                                 |
| --------------------- | ---------------------------------------------------- |
| AI/ML learners        | Understand MCP and multi-agent systems practically   |
| Python developers     | Learn how to build agent collaboration workflows     |
| GenAI trainers        | Use the app as a classroom demo project              |
| Full-stack developers | Understand how shared state works in agentic systems |
| AI architects         | Explore MCP as a coordination layer                  |

---

## 3. Product Goals

### Functional Goals

1. Build a mini research assistant using Python.
2. Demonstrate multiple agents working together.
3. Use LangGraph to control workflow and state transitions.
4. Use CrewAI to model role-based agents.
5. Use MCP SDK concepts to expose shared tools, resources, and context.
6. Validate all inter-agent messages using `jsonschema`.
7. Store shared research context and embeddings.
8. Generate a final research report.

### Learning Goals

By completing this project, learners should understand:

* What MCP is
* How MCP messages are structured
* How one agent can communicate with another agent
* How shared context improves collaboration
* How embeddings can be reused across agents
* How LangGraph manages workflow state
* How CrewAI models role-based collaboration
* How schema validation prevents broken agent messages

---

## 4. Non-Goals

This mini app will **not** focus on:

* Building a production-grade SaaS platform
* Building a complex UI
* Real-time collaborative editing
* User authentication
* Advanced vector database scaling
* Enterprise security
* Long-term memory across many users
* Large-scale web crawling

---

## 5. Core Concept

The system will behave like a small AI research team.

### Example User Input

```text
Research topic: How AI agents are changing software development workflows
```

### Agents Involved

| Agent                   | Responsibility                           |
| ----------------------- | ---------------------------------------- |
| Research Planner Agent  | Breaks the topic into research questions |
| Context Retriever Agent | Collects relevant documents/context      |
| Embedding Agent         | Creates embeddings for retrieved content |
| Analyst Agent           | Reads context and extracts insights      |
| Critic Agent            | Reviews quality and identifies gaps      |
| Writer Agent            | Produces final research summary          |

### Shared State

All agents will read from and write to a shared MCP-style context object.

Example:

```json
{
  "session_id": "research_001",
  "topic": "AI agents in software development",
  "research_questions": [],
  "retrieved_context": [],
  "embeddings": [],
  "agent_messages": [],
  "final_report": ""
}
```

---

## 6. User Journey

### Step 1: User Enters Topic

The user runs the CLI:

```bash
python main.py --topic "Impact of AI agents on software development"
```

### Step 2: Planner Agent Creates Research Questions

Example output:

```json
{
  "agent": "planner",
  "message_type": "research_plan",
  "payload": {
    "questions": [
      "What are AI agents?",
      "How are AI agents used in software development?",
      "What are the benefits?",
      "What are the risks?",
      "What is the future outlook?"
    ]
  }
}
```

### Step 3: Context Retriever Agent Collects Context

The retriever uses local files, mock search results, or MCP tools to retrieve context.

### Step 4: Embedding Agent Generates Embeddings

The embedding agent converts retrieved chunks into vector representations.

### Step 5: Analyst Agent Extracts Insights

The analyst reads the context and produces structured findings.

### Step 6: Critic Agent Reviews Gaps

The critic checks whether the findings are weak, incomplete, or repetitive.

### Step 7: Writer Agent Creates Final Report

The final report includes:

* Executive summary
* Key findings
* Supporting evidence
* Limitations
* Future scope

---

## 7. Functional Requirements

## FR1: User Topic Input

### Description

The system should accept a research topic from the user.

### Input Options

* CLI argument
* `.env` default topic
* Interactive terminal prompt

### Example

```bash
python main.py --topic "MCP in multi-agent systems"
```

### Acceptance Criteria

* User can provide a topic.
* Topic is stored in shared state.
* Empty topic should show validation error.

---

## FR2: MCP-Style Message Structure

### Description

Every agent should communicate using a common message format.

### Message Fields

| Field            | Description                 |
| ---------------- | --------------------------- |
| `message_id`     | Unique message ID           |
| `session_id`     | Research session ID         |
| `sender_agent`   | Agent sending the message   |
| `receiver_agent` | Target agent or `broadcast` |
| `message_type`   | Type of message             |
| `timestamp`      | ISO timestamp               |
| `payload`        | Actual data                 |
| `metadata`       | Optional metadata           |

### Example Message

```json
{
  "message_id": "msg_001",
  "session_id": "research_001",
  "sender_agent": "planner_agent",
  "receiver_agent": "retriever_agent",
  "message_type": "research_plan_created",
  "timestamp": "2026-05-28T10:30:00Z",
  "payload": {
    "questions": [
      "What is MCP?",
      "How does MCP help agents share context?"
    ]
  },
  "metadata": {
    "priority": "high",
    "requires_response": true
  }
}
```

### Acceptance Criteria

* Every agent output follows this structure.
* Invalid messages are rejected.
* Messages are stored in shared state.

---

## FR3: JSON Schema Validation

### Description

The system should validate all agent messages before adding them to shared state.

### Example Schema

```json
{
  "type": "object",
  "required": [
    "message_id",
    "session_id",
    "sender_agent",
    "receiver_agent",
    "message_type",
    "timestamp",
    "payload"
  ],
  "properties": {
    "message_id": { "type": "string" },
    "session_id": { "type": "string" },
    "sender_agent": { "type": "string" },
    "receiver_agent": { "type": "string" },
    "message_type": { "type": "string" },
    "timestamp": { "type": "string" },
    "payload": { "type": "object" },
    "metadata": { "type": "object" }
  }
}
```

### Acceptance Criteria

* Valid messages pass.
* Invalid messages raise readable errors.
* Validation failures are logged.

---

## FR4: Shared MCP Context Store

### Description

The system should maintain a shared context store accessible by all agents.

### Shared State Structure

```python
class ResearchState(TypedDict):
    session_id: str
    topic: str
    research_questions: list[str]
    retrieved_context: list[dict]
    embeddings: list[dict]
    findings: list[dict]
    critique: list[str]
    agent_messages: list[dict]
    final_report: str
```

### Acceptance Criteria

* Agents can read from shared state.
* Agents can append new information.
* State is passed between LangGraph nodes.
* State can be exported as JSON.

---

## FR5–FR15: Agent Requirements

See full PRD for individual agent functional requirements (FR5–FR15).

---

## 8. Suggested Folder Structure

```text
research-assistant-mcp/
│
├── README.md
├── pyproject.toml
├── .env.example
│
├── docs/
│   └── PRD.md
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── schemas/
│   │   ├── mcp_message_schema.json
│   │   └── tool_input_schemas.json
│   ├── state/
│   │   ├── research_state.py
│   │   └── state_store.py
│   ├── mcp_server/
│   │   ├── server.py
│   │   ├── tools.py
│   │   └── resources.py
│   ├── agents/
│   │   ├── planner_agent.py
│   │   ├── retriever_agent.py
│   │   ├── embedding_agent.py
│   │   ├── analyst_agent.py
│   │   ├── critic_agent.py
│   │   └── writer_agent.py
│   ├── graph/
│   │   ├── workflow.py
│   │   └── nodes.py
│   ├── crew/
│   │   ├── crew_config.py
│   │   └── tasks.py
│   ├── validation/
│   │   └── message_validator.py
│   ├── embeddings/
│   │   └── embedding_service.py
│   ├── knowledge/
│   │   ├── mcp_overview.md
│   │   └── ai_agents_overview.md
│   └── outputs/
│       ├── research_state.json
│       ├── agent_messages.json
│       └── final_report.md
│
└── tests/
    ├── test_message_schema.py
    ├── test_state.py
    ├── test_agents.py
    └── test_workflow.py
```

---

## 9. Technology Stack

| Layer              | Technology                                 |
| ------------------ | ------------------------------------------ |
| Language           | Python 3.11+                               |
| Agent workflow     | LangGraph                                  |
| Role-based agents  | CrewAI                                     |
| Context protocol   | MCP SDK (fastmcp)                          |
| Message validation | jsonschema                                 |
| Data format        | JSON                                       |
| Report format      | Markdown                                   |
| Embeddings         | OpenAI embeddings or mock                  |
| CLI                | Typer                                      |
| Testing            | pytest                                     |

---

## 10. MCP Message Types

| Message Type            | Sender          | Receiver                 | Purpose                        |
| ----------------------- | --------------- | ------------------------ | ------------------------------ |
| `research_plan_created` | Planner         | Retriever                | Send research questions        |
| `context_retrieved`     | Retriever       | Embedding Agent          | Send context chunks            |
| `embeddings_created`    | Embedding Agent | Analyst                  | Notify embeddings ready        |
| `findings_created`      | Analyst         | Critic                   | Send findings for review       |
| `critique_created`      | Critic          | Planner/Retriever/Writer | Approve or request improvement |
| `final_report_created`  | Writer          | User/System              | Final output                   |

---

## 16. Implementation Phases

### Phase 1: Basic MCP Message System
- Message schema, validator, logger, shared state

### Phase 2: Basic Agent-to-Agent Communication
- Planner + Retriever agents, message passing

### Phase 3: Context and Embedding Sharing
- Context store, embedding service, embedding records

### Phase 4: Multi-Agent Coordination
- LangGraph workflow, CrewAI agents, critic loop, writer

### Phase 5: Final Demo and Documentation
- CLI demo, README, architecture diagram, sample outputs

---

## 17. Architecture Diagram

```text
                    ┌────────────────────┐
                    │       User CLI      │
                    │  Research Topic     │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │   LangGraph Flow    │
                    │ Stateful Workflow   │
                    └─────────┬──────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ Planner Agent │     │Retriever Agent│     │Embedding Agent│
└───────┬───────┘     └───────┬───────┘     └───────┬───────┘
        │                     │                     │
        └─────────────┬───────┴─────────────┬───────┘
                      ▼                     ▼
             ┌────────────────────────────────┐
             │      MCP Shared Context         │
             │ Messages, Context, Embeddings   │
             └────────────────────────────────┘
                      ▲                     ▲
        ┌─────────────┴───────┐     ┌───────┴────────┐
        │    Analyst Agent     │     │  Critic Agent   │
        └─────────────┬───────┘     └───────┬────────┘
                      │                     │
                      └──────────┬──────────┘
                                 ▼
                          ┌──────────────┐
                          │ Writer Agent │
                          └──────┬───────┘
                                 ▼
                          ┌──────────────┐
                          │ Final Report │
                          └──────────────┘
```

---

## 20. Definition of Done

The project is complete when:

* User can run research from CLI.
* At least five agents participate.
* Agents communicate using validated MCP-style messages.
* Shared context is updated across the workflow.
* Embeddings are created or mocked.
* Critic agent can approve or request improvement.
* Final report is generated.
* State and messages are exported as JSON.
* README explains how MCP, LangGraph, CrewAI, and jsonschema are used.
