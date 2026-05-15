# MicroDegree Support Chatbot

This project is a sophisticated Retrieval-Augmented Generation (RAG) chatbot designed to assist with support queries for MicroDegree. It uses a graph-based agent architecture to route, retrieve, grade, and generate accurate answers based strictly on a provided local knowledge base.

## Features

- **LangGraph Agent Architecture**: Routes incoming queries (Greetings, Out of Scope, Support Queries).
- **RAG Pipeline**: Retrieves context using OpenAI Embeddings and a local ChromaDB vector store.
- **LLM-Based Context Grading**: An LLM grader evaluates the retrieved documents to ensure relevance to the user's question, reducing hallucinations.
- **Streamlit Interface**: An interactive, stateful chat interface with a modern web design.
- **Directory Ingestion**: Automatically indexes all Markdown (`.md`) files found in the `data/` directory.

## Prerequisites

1. Python 3.9+
2. An OpenAI API Key

Setup your environment variables by setting `OPENAI_API_KEY`:
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

## Setup & Installation

1. Navigate to the project directory:
```bash
cd "/Users/vinod/Desktop/Python for Gen AI/projects/support_chatbot"
```

2. (Optional but recommended) Activate your virtual environment:
```bash
source venv/bin/activate
```

3. Install the dependencies (if you haven't already):
```bash
pip install -r requirements.txt
```

## Usage Instructions

### 1. Managing the Knowledge Base (Data Ingestion)

Before the chatbot can answer questions, it needs to index the knowledge base. Place any `.md` files you want the chatbot to know about inside the `data/` folder.

**To index new files (without deleting the existing database):**
Run the following command from the root of the project:
```bash
python -m src.ingest
```

**To re-index everything from scratch (Deletes existing database):**
If you have updated existing files or want to start fresh:
```bash
python -m src.ingest --reindex
```
*(Note: Use `python -m src.ingest` instead of `python src/ingest.py` to avoid Python module import errors!)*

### 2. Running the Chatbot

Start the Streamlit application to interact with the bot:
```bash
streamlit run app.py
```

This will launch a web server and open a new tab in your default browser where you can chat with the MicroDegree Support Assistant.

## Project Structure

- `app.py`: Streamlit frontend application.
- `data/`: Directory where Markdown (`.md`) knowledge base files are stored.
- `src/`: Core Python modules.
  - `ingest.py`: Script to process and embed `data/` files into ChromaDB.
  - `graph.py`: LangGraph state machine orchestrating the chatbot's decision flow.
  - `grader.py`: Pydantic and LLM setup for binary relevance grading of retrieved context.
  - `prompts.py`: System prompts for the conversational bot.
  - `config.py`: Centralized configuration variables.
  - `vectorstore.py`: Logic for instantiating the retriever.
- `chroma_db/`: Auto-generated persistent vector database directory (created after running ingestion).
