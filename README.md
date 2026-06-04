# Python for Gen AI

A hands-on learning workspace for Python fundamentals and the building blocks commonly used in Gen AI apps — HTTP clients, FastAPI, Pydantic, LangChain, LangGraph, CrewAI, and **MCP (Model Context Protocol)**.

## Repository map

- **`1_python_basics/`**: Core Python (types, strings, collections, control flow, functions, files, exceptions, OOP, decorators).
- **`2_packages/`**: A tiny package + unit tests (good for learning imports + tests).
- **`3_fastapi/`**: A small FastAPI app demonstrating common API patterns.
- **`4_requests_basics/`**: Runnable `requests` examples (auth, retries, sessions).
- **`5_basic_pydantic/`**: Pydantic basics + a few advanced patterns.
- **`6_httpx_basics/`**: `httpx` sync/async/streaming patterns, plus LLM-style examples.
- **`7_jupyter_notebook/`**: Notebook(s) for interactive exploration.
- **`8_langchain/`**: LangChain v0.3 components — chains, prompts, memory, tools, agents, and LCEL.
- **`9_langserve/`**: Serving LangChain chains as REST APIs with LangServe.
- **`10_langgraph/`**: LangGraph — stateful multi-agent workflows with graph-based control flow, HITL, and multi-agent patterns.
- **`11_crewai/`**: CrewAI — multi-agent orchestration from basics to advanced (tools, flows, hierarchical crews, guardrails, callbacks).
- **`12_mcp/`**: MCP (Model Context Protocol) — full coverage from basics to production patterns: tools, resources, prompts, transports, server context, lifespan, caching, and LangChain integration.
- **`projects/`**: Larger "projects" sample projects (complete mini-apps you can run end-to-end).

## Projects

### Smart Study Assistant (`projects/smart-study-assistant/`)

Multi-role CLI assistant that routes tasks between OpenAI / Gemini / Claude based on the query type/complexity.

```bash
cd "projects/smart-study-assistant"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set at least one API key (recommended: use a local .env file)
# OPENAI_API_KEY=...
# GEMINI_API_KEY=...
# ANTHROPIC_API_KEY=...

python main.py chat
```

### Smart Study Assistant Simple (`projects/smart-study-assistant-simple/`)

A streamlined version of the Smart Study Assistant, focusing on core logic.

```bash
cd "projects/smart-study-assistant-simple"
# ... setup steps similar to above ...
```

### Function Calling: Weather (`projects/function_calling/`)

Small demo showing OpenAI tool/function calling that fetches current weather from OpenWeatherMap (city name or ZIP+country).

```bash
cd "projects/function_calling"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create a .env file (see env.example)
# OPENAI_API_KEY=...
# WEATHER_API_KEY=...

python main.py
```

### FAQ RAG System (`projects/faq-rag-system/`)

A Retrieval-Augmented Generation (RAG) system for answering FAQs interactive CLI, supporting OpenAI and local embeddings (Sentence Transformers).

```bash
cd "projects/faq-rag-system"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create .env with OPENAI_API_KEY if using OpenAI
# Or use local embeddings (see README)

python main.py
```

### LLM API Wrapper (`projects/llm-api-wrapper/`)

Unified wrapper for multiple LLM providers.

```bash
cd "projects/llm-api-wrapper"
# ... setup steps ...
```

## Setup (recommended)

Create a virtual environment **per module** (each folder may have its own `requirements.txt`).

```bash
# From this repo root
cd "3_fastapi"  # or 4_requests_basics / 6_httpx_basics / ...

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt  # if this module has one
```

## Run examples

### Python scripts

```bash
python3 1_python_basics/1_print_functions.py
python3 4_requests_basics/01_get_json.py
python3 6_httpx_basics/01_httpx-basics.py
```

### MCP (Model Context Protocol)

```bash
cd "12_mcp"
python3 -m venv .venv
source .venv/bin/activate
pip install fastmcp mcp python-dotenv

python 1_mcp_basics.py          # protocol basics, server & client
python 2_mcp_tools.py           # all tool definition patterns
python 3_mcp_resources.py       # static, dynamic & template resources
python 4_mcp_prompts.py         # reusable prompt templates
python 5_mcp_transports.py      # stdio, SSE & in-process transports
python 6_mcp_with_langchain.py  # MCP tools inside LangChain agents
python 7_mcp_context_and_state.py  # lifespan, caching, progress reporting
```

### FastAPI

```bash
cd "3_fastapi"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

uvicorn main:app --reload
```

Then open:
- **Docs**: `http://127.0.0.1:8000/docs`
- **Health**: `http://127.0.0.1:8000/health`

## Notes

- **Internet required** for many HTTP examples (`requests`/`httpx`).
- **API keys**: if you run any LLM/OpenAI-style examples, prefer environment variables (e.g. `OPENAI_API_KEY`) and keep secrets out of git.

