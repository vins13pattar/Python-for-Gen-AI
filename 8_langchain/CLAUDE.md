# LangChain v0.3 — Claude Code Context

## Project
Educational examples covering the 14 core LangChain v0.3 building blocks.
Each file is standalone and runnable (`python <file>.py`).

## Environment
- Python 3.x, virtual environment expected
- Requires `.env` with `OPENAI_API_KEY` (and optionally `ANTHROPIC_API_KEY`)
- Load env at top of every script: `from dotenv import load_dotenv; load_dotenv()`

## Key Dependencies
| Package | Purpose |
|---------|---------|
| `langchain==1.2.x` | Core framework |
| `langchain-openai` | OpenAI chat + embeddings |
| `langchain-anthropic` | Anthropic/Claude models |
| `langchain-community` | ChatMessageHistory, loaders, etc. |
| `langchain-core` | LCEL, runnables, prompts, parsers |
| `langgraph` | Graph-based agent workflows |
| `faiss-cpu` | FAISS vector store |
| `chromadb` | Chroma vector store |
| `openai==2.x` | OpenAI SDK |
| `pypdf` | PDF document loader |

Install: `pip install -r requirements.txt`

## File Map
| File | Component |
|------|-----------|
| `1_chat_models.py` | LLMs & Chat Models |
| `2_prompts.py` | Prompt Templates |
| `3_chains.py` | Classic chains |
| `4_parsers.py` | Output Parsers |
| `5_lcel_runnables.py` | LCEL & Runnables |
| `6_document_loaders.py` | Document Loaders |
| `7_text_splitters.py` | Text Splitters |
| `8_embeddings.py` | Embeddings |
| `9_vector_stores.py` | Vector Stores (FAISS/Chroma) |
| `10_retrievers.py` | Retrievers & RAG chain |
| `11_memory.py` | Memory & Message History |
| `12_tools_agents.py` | Tools & Agents (ReAct) |
| `13_callbacks.py` | Callbacks & Streaming |
| `14_ecosystem.py` | LangSmith, LangGraph, LangServe |
| `workpad.py` | Scratch / experimentation |
| `faiss.py` | FAISS standalone experiments |
| `assignment1.py` / `assignment2.py` | Assignments |

## Conventions
- All examples use `ChatOpenAI(model="gpt-4o-mini")` unless testing another model
- Vector store persists to `chroma_langchain_db/` (Chroma) or `faiss_faqs_index/` (FAISS)
- `sample_docs/` holds test documents for loaders/splitters/RAG
- `faqs.txt` and `sample.txt` are local test data files

## LangChain v0.3 Patterns
- Prefer LCEL pipe syntax: `chain = prompt | llm | parser`
- Use `RunnableWithMessageHistory` for session memory (not deprecated `ConversationChain`)
- Use `create_react_agent` from `langgraph.prebuilt` for agents
- Output parsers: `StrOutputParser`, `JsonOutputParser`, `PydanticOutputParser`

## Projects
- `../projects/converstational_rag_bot/` — Conversational RAG bot using Chroma + LangChain
