# Projects

Welcome to the Projects directory! Here you will find various implementations and examples of Generative AI applications using Python.

## Project List

### 1. [Function Calling](./function_calling/)
Explore examples and implementations demonstrating how to utilize function calling capabilities with Large Language Models (LLMs). This project shows how to connect LLMs to external tools and APIs.

### 2. [LLM API Wrapper](./llm-api-wrapper/)
A unified, extensible wrapper library designed to simplify interactions with multiple LLM providers.
- **Providers Supported**: OpenAI, Google Gemini, Anthropic.
- **Features**: Common interface, easy configuration, and extensibility.

### 3. [Smart Study Assistant](./smart-study-assistant/)
A comprehensive AI-powered application designed to assist users in their learning journey. Features include quiz generation, topic explanations, and progress tracking.

### 4. [Smart Study Assistant (Simple)](./smart-study-assistant-simple/)
A streamlined version of the Smart Study Assistant. This project focuses on the core logic and basic implementations, making it an excellent starting point for understanding how to build educational AI tools without the complexity of a full-scale application.

### 5. [Smart Text Summariser](./smart-text-summerizer/)
A Python-based multi-LLM summarisation engine that provides a unified interface for generating structured summaries using various AI providers.
- **Providers Supported**: OpenAI, Anthropic, Google Gemini, LM Studio.
- **Features**: Structured Pydantic output, robust retry logic, and easy provider switching via CLI.

### 6. [Conversational RAG bot](./converstational_rag_bot/)
A compact LangChain demo that pairs **retrieval-augmented generation** with **per-session chat memory**: tutorial snippets live in a persisted **Chroma** store, each question pulls relevant context, and **RunnableWithMessageHistory** keeps prior turns for the same `session_id`.
- **Stack**: LangChain (LCEL), Chroma, OpenAI (chat + embeddings).
- **Features**: CLI loop, explicit prepare step for prompt inputs (context / question / history), optional Excalidraw diagram; see the project `README.md` for setup and env vars.

### 7. [Stock Analysis Crew](./stock_analysis_crew/)
A state-of-the-art multi-agent investment research and education assistant designed for the Indian stock market using CrewAI.
- **Stack**: CrewAI (Flows & Crews), yfinance, pandas-ta, Streamlit, OpenAI.
- **Agents**: Collaborative 6-agent sequential team (Market Data, Technicals, Fundamentals, News Sentiment, Risk, and Report Writer).
- **Features**: Real-time price tracking, automated indicator computation (SMAs, RSI, MACD), news sentiment classification, key risks evaluation, educational view, SEBI disclaimer compliance, and a premium interactive Streamlit dashboard.


