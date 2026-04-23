# Python for Gen AI — Claude Code Context

## What this repo is

A hands-on learning workspace progressing from Python fundamentals through production-grade Gen AI patterns. Each numbered module is self-contained. `projects/` contains complete runnable mini-apps.

## Environment conventions

- **Python**: 3.x, one virtual environment per module (`python3 -m venv .venv && source .venv/bin/activate`)
- **API keys**: always via `.env` file — never hardcoded. Load with `from dotenv import load_dotenv; load_dotenv()`
- **Required keys** (depending on module): `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`
- **Install deps**: `pip install -r requirements.txt` inside the relevant module directory

## Repository map

| Directory | Topic |
|-----------|-------|
| `1_python_basics/` | Core Python — types, strings, collections, OOP, decorators, file I/O, exceptions |
| `2_packages/` | Package structure + unit tests |
| `3_fastapi/` | FastAPI REST API (uvicorn, routes, docs at `/docs`) |
| `4_requests_basics/` | `requests` library — auth, retries, sessions, timeouts |
| `5_basic_pydantic/` | Pydantic v2 — validation, models, advanced patterns |
| `6_httpx_basics/` | `httpx` — sync/async/streaming, LLM-style HTTP calls |
| `7_jupyter_notebook/` | Interactive notebooks |
| `8_langchain/` | LangChain v0.3 — 14 building blocks (see `8_langchain/CLAUDE.md`) |
| `9_langserve/` | LangServe — serving LangChain chains as APIs |
| `interview_questions/` | Real-world interview Q&A for each topic |
| `projects/` | Complete mini-apps (see below) |

## Projects

| Project | Description | Key tech |
|---------|-------------|----------|
| `converstational_rag_bot/` | Conversational RAG with memory | LangChain, Chroma |
| `faq-rag-system/` | FAQ answering via RAG | Chroma, OpenAI/local embeddings |
| `rag-system/` | Basic RAG pipeline | LangChain, embeddings |
| `smart-study-assistant/` | Multi-model CLI (routes by query type) | OpenAI, Gemini, Claude |
| `smart-study-assistant-simple/` | Streamlined study assistant | OpenAI |
| `function_calling/` | OpenAI tool/function calling demo | OpenAI, OpenWeatherMap API |
| `llm-api-wrapper/` | Unified wrapper across LLM providers | OpenAI, Anthropic |
| `code-debugger-assistant/` | AI code debugging assistant | LangChain |
| `code-debugger-assistant-extended/` | Extended debugger with more features | LangChain |
| `smart-text-summerizer/` | Text summarization app | LLM APIs |

## Running things

```bash
# Any standalone script
python3 1_python_basics/1_print_functions.py

# FastAPI server
cd 3_fastapi && uvicorn main:app --reload
# → http://127.0.0.1:8000/docs

# LangChain examples
cd 8_langchain && python 1_chat_models.py

# Any project
cd projects/converstational_rag_bot
python conv_rag_bot.py
```

## Key patterns in this codebase

- **LangChain**: LCEL pipe syntax (`chain = prompt | llm | parser`), `RunnableWithMessageHistory` for memory, `create_react_agent` from `langgraph.prebuilt`
- **Vector stores**: Chroma persists to `chroma_langchain_db/` or `chroma_db/`; FAISS to `faiss_faqs_index/`
- **Default model**: `ChatOpenAI(model="gpt-4o-mini")` unless testing another provider
- **workpad.py files**: scratch/experimentation — not production code

## Reference docs (at repo root)

| File | Content |
|------|---------|
| `AI_ML_DL_GEN_AI.md` | AI/ML/DL/Gen AI concepts overview |
| `GEN_AI_BEST_PRACTICES.md` | Gen AI engineering best practices |
| `JINJA2_PROMPT_ENGINEERING.md` | Prompt engineering with Jinja2 |
| `LLM_ECO_SYSTEM_AND_LIFECYCLE.md` | LLM ecosystem and lifecycle |
| `LLM_INFERENCE_PARAMETERS.md` | Inference parameters reference |
| `ML_MATH.md` | Math foundations for ML |
| `OPENAI_DEEPDIVE.md` | OpenAI API deep-dive |
| `STREAMLIT.md` | Streamlit reference |
| `PART_1_ASSIGMENTS.md` | Assignment prompts and specs |
