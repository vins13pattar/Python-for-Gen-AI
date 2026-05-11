# Code Debugger Assistant

An AI-powered debugging assistant built with **LangChain**, **LCEL**, and **LangGraph Platform**.

Submit code and an error message — the assistant returns a structured `DebugReport` with the root cause, corrected code, test cases, and prevention tips.

---

## Architecture

```
User Input (code + error + expected behavior)
        │
        ▼
  create_agent (LangChain Agent)
        │  ┌─────────────────────────────────┐
        ├─▶│ security_check_tool             │  ← Always called first
        ├─▶│ detect_language_tool            │  ← LCEL: prompt | model
        ├─▶│ traceback_parser_tool           │  ← LCEL: structured output
        ├─▶│ bug_classifier_tool             │  ← LCEL: structured output
        ├─▶│ fix_strategy_tool               │  ← LCEL: structured output
        └─▶│ test_case_generator_tool        │  ← LCEL: structured output
           └─────────────────────────────────┘
        │
        ▼  Middleware (applied to every tool call)
           ├── safety_middleware         (blocks unsafe patterns)
           ├── pii_detection_middleware  (detects PII/secrets)
           ├── retry_middleware          (retries transient failures)
           ├── logging_middleware        (logs calls + timing)
           ├── summarization_middleware  (monitors history length)
           └── limits_middleware         (caps tool calls/session)
        │
        ▼
  DebugReport (Pydantic structured output)
```

### Key Design Decisions
| PRD Requirement | Implementation |
|---|---|
| LangChain Agent | `create_agent()` with 6 `@tool` functions |
| Model | `openai:gpt-4.1-mini` |
| LCEL Chains | `prompt | model.with_structured_output(...)` inside each tool |
| Short-term memory | `MemorySaver()` checkpointer + `thread_id` |
| Streaming | `stream_mode="custom"` via `get_stream_writer()` in each tool |
| Middleware | 6 `@wrap_tool_call` middleware (safety, PII, retry, logging, summarization, limits) |
| Structured output | `response_format=DebugReport` on `create_agent()` |

---

## Project Structure

```
code-debugger-assistant-langgraph/
├── app/
│   ├── graph.py                 ← create_agent() entry point (langgraph dev)
│   ├── state.py                 ← DebuggerState with add_messages reducer
│   ├── tools/
│   │   ├── security_check.py   ← @tool — blocks unsafe requests
│   │   ├── language_detector.py ← @tool — detects language
│   │   ├── traceback_parser.py  ← @tool — parses error/traceback
│   │   ├── bug_classifier.py    ← @tool — classifies bug + root cause
│   │   ├── fix_strategy.py      ← @tool — generates corrected code
│   │   ├── test_generator.py    ← @tool — generates test cases
│   │   └── utils.py             ← safe stream writer helper
│   ├── chains/
│   │   ├── debug_analysis_chain.py
│   │   ├── fix_generation_chain.py
│   │   ├── test_generation_chain.py
│   │   └── final_report_chain.py ← Compiles findings into DebugReport
│   ├── middleware/
│   │   ├── safety.py            ← @wrap_tool_call — blocks unsafe patterns
│   │   ├── pii_detection.py     ← @wrap_tool_call — detects PII/secrets
│   │   ├── retry.py             ← @wrap_tool_call — retries transient failures
│   │   ├── logging.py           ← @wrap_tool_call — logs tool calls
│   │   ├── summarization.py     ← @wrap_tool_call — monitors history length
│   │   └── limits.py            ← @wrap_tool_call — caps call count
│   ├── schemas/
│   │   ├── request.py           ← DebugRequest schema
│   │   └── response.py          ← DebugReport + DebugIssue schemas
│   └── prompts/
│       ├── debugger_prompt.py   ← System prompt + all ChatPromptTemplates
│       ├── fix_prompt.py        ← Re-exports GENERATE_FIX_PROMPT
│       └── test_prompt.py       ← Re-exports TEST_GENERATOR_PROMPT
├── tests/
│   ├── test_tools.py            ← Unit tests for security_check_tool
│   ├── test_structured_output.py ← Unit tests for DebugReport schema
│   └── test_graph.py            ← Structural tests for graph import
├── main.py                      ← Interactive runner
├── langgraph.json               ← LangGraph Platform config
├── requirements.txt
└── .env.example
```

---

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Fill in OPENAI_API_KEY and LANGSMITH_API_KEY
   ```

---

## Usage

### Single-turn debug run
```bash
python main.py
```

### Multi-turn interactive session
```bash
python main.py --multi
```

### LangGraph Studio (local dev server)
```bash
langgraph dev
```

### Run tests
```bash
pytest tests/ -v
```

---

## Sample Input / Output

**Input:**
```json
{
  "code": "def divide(a, b): return a / b\nprint(divide(10, 0))",
  "error_message": "ZeroDivisionError: division by zero",
  "expected_behavior": "Handle division safely"
}
```

**Output (`DebugReport`):**
```json
{
  "language": "python",
  "issue": {
    "error_type": "ZeroDivisionError",
    "root_cause": "Division by zero when b=0",
    "affected_line": 2,
    "severity": "high"
  },
  "explanation": "...",
  "fixed_code": "def divide(a, b):\n    if b == 0: return None\n    return a / b",
  "changes_made": ["Added zero guard before division"],
  "test_cases": ["assert divide(10,2)==5", "assert divide(10,0) is None"],
  "prevention_tips": ["Always validate divisors"],
  "confidence_score": 0.96
}
```
