# CrewAI — Multi-Agent AI Framework

Learn CrewAI from basics to advanced, with practical, runnable examples.

## Key Concepts

| # | File | Concept |
|---|------|---------| 
| 1 | `1_basics.py` | Core building blocks — Agent, Task, Crew, Process |
| 2 | `2_tools.py` | Built-in & custom tools — @tool decorator, SerperDevTool |
| 3 | `3_collaboration.py` | Agent collaboration — delegation, context passing, memory |
| 4 | `4_flows.py` | Flows — @start, @listen, @router, structured state |
| 5 | `5_hierarchical_crew.py` | Hierarchical process — manager agent orchestration |
| 6 | `6_flow_with_crew.py` | Production pattern — Flows orchestrating multiple Crews |
| 7 | `7_guardrails_callbacks.py` | Guardrails, callbacks, output validation & structured output |

## Setup

```bash
cd 11_crewai
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
pip install -r requirements.txt
```

Create `.env` with your API keys:

```
OPENAI_API_KEY=sk-...
SERPER_API_KEY=...              # optional, for web search tool examples
```

## Run

```bash
python 1_basics.py
python 2_tools.py
python 3_collaboration.py
# ... etc.
```

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│                  FLOW                        │
│  (orchestrates crews, state, routing)        │
│                                              │
│   ┌─────────────────────────────────────┐    │
│   │              CREW                    │    │
│   │  (team of agents working together)   │    │
│   │                                      │    │
│   │   ┌──────────┐    ┌──────────┐      │    │
│   │   │  AGENT   │    │  AGENT   │      │    │
│   │   │ (role,   │    │ (role,   │      │    │
│   │   │  goal,   │──▶│  goal,   │      │    │
│   │   │  tools)  │    │  tools)  │      │    │
│   │   └──────────┘    └──────────┘      │    │
│   │        │                │            │    │
│   │   ┌────▼───┐      ┌────▼───┐        │    │
│   │   │  TASK  │      │  TASK  │        │    │
│   │   └────────┘      └────────┘        │    │
│   └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```
