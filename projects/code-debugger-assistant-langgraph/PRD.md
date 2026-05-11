# PRD: Code Debugger Assistant

## 1. Product Overview

**Product Name:** Code Debugger Assistant
**Project Type:** Mini AI Project
**Difficulty Level:** Easy to Medium
**Estimated Build Time:** 40–60 minutes for MVP
**Primary Stack:** Python, LangChain, LCEL, LangGraph Platform, OpenAI API

The **Code Debugger Assistant** is an AI-powered assistant that helps developers debug code by analyzing the submitted code, error message, traceback, and expected behavior. It returns a clear debugging report containing the root cause, explanation, corrected code, test cases, and prevention tips.

The project will be implemented using LangChain core components such as **Agents, Models, Messages, Tools, Short-term memory, Streaming, Structured output, and Middleware**.

---

## 2. Objective

The objective is to build a mini project that demonstrates how LangChain can be used to create a practical AI debugging assistant.

The assistant should:

1. Accept code and error details from the user.
2. Detect or confirm the programming language.
3. Analyze the error and traceback.
4. Identify the root cause.
5. Explain the issue in simple language.
6. Generate corrected code.
7. Suggest test cases.
8. Return structured output.
9. Support multi-turn debugging using short-term memory.
10. Stream progress during debugging.

---

## 3. Problem Statement

Developers, students, and beginners often struggle to understand why their code fails. Error messages can be confusing, and general AI answers may be too broad or inconsistent.

This project solves that problem by creating a focused **Code Debugger Assistant** that follows a reliable debugging workflow and produces a predictable response format.

---

## 4. Target Users

| User Type           | Need                                             |
| ------------------- | ------------------------------------------------ |
| Beginner developers | Understand basic coding errors                   |
| Students            | Learn debugging step by step                     |
| Backend developers  | Debug API, database, and runtime errors          |
| Frontend developers | Debug JavaScript, TypeScript, and React issues   |
| Python learners     | Debug scripts, functions, and LangChain examples |
| Trainers            | Use as a teaching/demo project                   |

---

## 5. Use Cases

| Use Case              | Description                                                 |
| --------------------- | ----------------------------------------------------------- |
| Python debugging      | Debug Python syntax, runtime, and logic errors              |
| JavaScript debugging  | Debug JS/TS errors and frontend issues                      |
| API error debugging   | Analyze API response errors and failed requests             |
| LangChain debugging   | Help debug LangChain chain, prompt, model, and agent errors |
| SQL/debugging support | Explain SQL query or DB-related errors                      |
| Learning support      | Explain bugs in beginner-friendly language                  |

---

## 6. In Scope

The MVP should support:

| Feature                 | Description                                    |
| ----------------------- | ---------------------------------------------- |
| Code input              | User can paste code                            |
| Error message input     | User can paste error or traceback              |
| Expected behavior input | User can describe what should happen           |
| Error analysis          | Assistant identifies issue type and root cause |
| Fixed code generation   | Assistant generates corrected code             |
| Explanation             | Assistant explains the bug simply              |
| Test suggestions        | Assistant suggests basic test cases            |
| Structured response     | Output follows a strict schema                 |
| Streaming               | Show progress while debugging                  |
| Short-term memory       | Continue debugging in the same session         |
| Middleware              | Add safety, retry, logging, and call limits    |

---

## 7. Out of Scope for MVP

| Feature                            | Reason                        |
| ---------------------------------- | ----------------------------- |
| Executing user-submitted code      | Security risk                 |
| Full IDE extension                 | Future enhancement            |
| GitHub repository scanning         | Future enhancement            |
| Multi-file project debugging       | Future enhancement            |
| Auto-fixing files directly         | Future enhancement            |
| Production-grade sandbox execution | Not required for mini project |

---

# 8. Core LangChain Components

## 8.1 Agents

The assistant should use a LangChain agent to reason about the debugging task and decide which tool to use.

The agent should be responsible for:

| Responsibility        | Description                                                                 |
| --------------------- | --------------------------------------------------------------------------- |
| Understand user input | Read code, error, traceback, and expected behavior                          |
| Select tools          | Use language detector, traceback parser, bug classifier, and test generator |
| Generate answer       | Produce a final debugging report                                            |
| Follow safety rules   | Avoid executing unsafe code                                                 |
| Maintain context      | Continue the debugging session using memory                                 |

Example agent setup:

```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()

debug_agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[
        security_check_tool,
        detect_language_tool,
        traceback_parser_tool,
        bug_classifier_tool,
        fix_strategy_tool,
        test_case_generator_tool,
    ],
    system_prompt=DEBUGGER_SYSTEM_PROMPT,
    checkpointer=checkpointer,
    middleware=[
        safety_middleware,
        logging_middleware,
        limits_middleware,
    ],
    response_format=DebugReport,
)

# Expose as `graph` for `langgraph dev`
graph = debug_agent
```

---

## 8.2 Models

The assistant will use OpenAI models through LangChain’s model interface.

Recommended model settings:

```python
from langchain.chat_models import init_chat_model

model = init_chat_model(
    "openai:gpt-4o-mini",
    temperature=0.2,
    max_retries=3,
)
```

Recommended model behavior:

| Setting       | Value                                       |
| ------------- | ------------------------------------------- |
| Temperature   | `0.2`                                       |
| Reason        | Debugging requires consistency and accuracy |
| Max retries   | `3`                                         |
| Output format | Structured JSON using Pydantic              |

---

## 8.3 Messages

The assistant should use message-based communication.

Required message types:

| Message Type   | Purpose                                  |
| -------------- | ---------------------------------------- |
| System message | Defines assistant behavior               |
| Human message  | User’s code and error input              |
| AI message     | Assistant’s explanation and final result |
| Tool message   | Output from debugging tools              |

System prompt:

```text
You are a Code Debugger Assistant.

Your job is to analyze code, errors, tracebacks, and expected behavior.

Rules:
1. Identify the root cause clearly.
2. Explain the bug in beginner-friendly language.
3. Generate corrected code with minimal changes.
4. Suggest practical test cases.
5. Do not execute user-submitted code.
6. Do not invent missing details.
7. Mention assumptions clearly.
8. Return the final response using the required structured schema.
```

---

## 8.4 Tools

The assistant should use tools to break the debugging process into smaller steps.

Recommended tools:

| Tool Name                  | Purpose                                            |
| -------------------------- | -------------------------------------------------- |
| `detect_language_tool`     | Detect programming language from code              |
| `traceback_parser_tool`    | Extract error type, line number, and stack details |
| `bug_classifier_tool`      | Classify the bug category                          |
| `fix_strategy_tool`        | Suggest the best fix approach                      |
| `test_case_generator_tool` | Generate test cases                                |
| `security_check_tool`      | Detect unsafe code or risky requests               |

Bug categories:

| Category            | Example                                       |
| ------------------- | --------------------------------------------- |
| Syntax error        | Missing colon, bracket, semicolon             |
| Runtime error       | `NameError`, `TypeError`, `ZeroDivisionError` |
| Logic error         | Wrong condition or calculation                |
| Dependency error    | Missing package or import                     |
| API error           | Invalid request, auth failure, wrong endpoint |
| Database error      | Query error, connection error                 |
| Configuration error | Missing environment variable or wrong config  |

---

## 8.5 Short-Term Memory

The assistant should remember the current debugging session.

Example conversation:

```text
User:
Here is my Python code and error.

Assistant:
The issue is a NameError. You used variable c, but it is not defined.

User:
Now I am getting TypeError after applying the fix.

Assistant:
Based on the previous code and new error, the next issue is...
```

Memory requirements:

| Requirement            | Description                                        |
| ---------------------- | -------------------------------------------------- |
| Thread-based memory    | Each debugging session should have a unique thread |
| Store previous code    | Keep the latest submitted code                     |
| Store previous error   | Keep previous debugging context                    |
| Continue debugging     | Support follow-up questions                        |
| Summarize long history | Use summarization middleware if needed             |

Development checkpointer:

```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()
```

---

## 8.6 Streaming

The assistant should stream progress while debugging.

Streaming progress messages:

```text
Reading code...
Detecting language...
Parsing traceback...
Classifying bug...
Finding root cause...
Generating fixed code...
Creating test cases...
Preparing final report...
```

Streaming modes:

| Mode       | Usage                           |
| ---------- | ------------------------------- |
| `updates`  | Show graph/node progress        |
| `messages` | Stream model output tokens      |
| `custom`   | Stream custom progress messages |

---

## 8.7 Structured Output

The final answer should always follow a strict schema.

Pydantic schema:

```python
from pydantic import BaseModel, Field
from typing import List, Optional


class DebugIssue(BaseModel):
    error_type: str = Field(description="Type of error")
    root_cause: str = Field(description="Main reason for the issue")
    affected_line: Optional[int] = Field(default=None)
    severity: str = Field(description="low, medium, high, or critical")


class DebugReport(BaseModel):
    language: str
    issue: DebugIssue
    explanation: str
    fixed_code: str
    changes_made: List[str]
    test_cases: List[str]
    prevention_tips: List[str]
    confidence_score: float
```

Expected output format:

```json
{
  "language": "python",
  "issue": {
    "error_type": "NameError",
    "root_cause": "Variable c is used but not defined",
    "affected_line": 1,
    "severity": "medium"
  },
  "explanation": "The function receives a and b, but tries to return a + c. Since c does not exist, Python raises a NameError.",
  "fixed_code": "def add(a, b):\n    return a + b",
  "changes_made": [
    "Replaced undefined variable c with b"
  ],
  "test_cases": [
    "assert add(2, 3) == 5",
    "assert add(-1, 1) == 0"
  ],
  "prevention_tips": [
    "Use clear variable names",
    "Run small unit tests after writing each function"
  ],
  "confidence_score": 0.95
}
```

---

## 8.8 Middleware

Middleware should be used to make the assistant safer and more reliable.

Middleware is applied via `@wrap_tool_call` decorators and passed to `create_agent(middleware=[...])`. Every tool call flows through the full middleware stack.

Implemented middleware:

| Middleware                  | Purpose                                   | File                   |
| --------------------------- | ----------------------------------------- | ---------------------- |
| Safety middleware            | Block unsafe execution requests           | `safety.py`            |
| PII detection middleware    | Detect secrets, tokens, emails, or keys   | `pii_detection.py`     |
| Retry middleware            | Retry tool calls on transient failures    | `retry.py`             |
| Logging middleware           | Track debugging steps with timing         | `logging.py`           |
| Summarization middleware    | Monitor long debugging sessions           | `summarization.py`     |
| Call limit middleware        | Prevent tool loop issues and high cost    | `limits.py`            |

> Note: Model-level retry is also handled by `init_chat_model(max_retries=3)` inside each tool. The retry middleware adds tool-level retry with exponential backoff on top of that.

Custom safety rule:

```text
The assistant must not execute user-submitted code.
The assistant must not run shell commands.
The assistant must not access files, secrets, or environment variables.
The assistant can only analyze code as text in MVP.
```

---

# 9. LangGraph Platform Architecture

## 9.1 High-Level Architecture

The assistant uses `create_agent()` from LangChain, which provides an agent that autonomously reasons about tool usage order. The agent is exposed as a graph for `langgraph dev`.

```text
Frontend / API Client
        |
        v
LangGraph Platform Agent Server
        |
        v
create_agent() — Code Debugger Agent
        |
        |-- Middleware Stack (safety → logging → limits)
        |
        |-- @tool: security_check_tool
        |-- @tool: detect_language_tool
        |-- @tool: traceback_parser_tool
        |-- @tool: bug_classifier_tool
        |-- @tool: fix_strategy_tool
        |-- @tool: test_case_generator_tool
        |
        v
response_format=DebugReport → Structured JSON Response
```

> Note: The agent decides tool invocation order dynamically based on the system prompt instructions. The system prompt guides the agent to call tools in a logical debugging sequence (security → language → traceback → classify → fix → tests).

---

## 9.2 LangGraph Runtime Concepts

| Concept      | Meaning in This Project               |
| ------------ | ------------------------------------- |
| Assistant    | The deployed Code Debugger Assistant  |
| Thread       | One debugging conversation/session    |
| Run          | One execution request inside a thread |
| State        | Current debugging context             |
| Node         | One step in the debugging workflow    |
| Edge         | Connection between workflow steps     |
| Checkpointer | Stores short-term memory              |

---

## 9.3 Graph State

```python
from typing import TypedDict, List, Optional, Annotated
from langgraph.graph.message import add_messages


class DebuggerState(TypedDict):
    # Message history (required by create_agent; reducer appends messages)
    messages: Annotated[list, add_messages]

    # User-submitted debug context
    language: Optional[str]
    code: str
    error_message: Optional[str]
    traceback: Optional[str]
    expected_behavior: Optional[str]

    # Intermediate analysis results
    parsed_error: Optional[dict]
    bug_type: Optional[str]
    root_cause: Optional[str]
    fixed_code: Optional[str]
    changes_made: List[str]
    test_cases: List[str]
    prevention_tips: List[str]

    # Final output
    final_report: Optional[dict]
```

---

## 9.4 Agent Tool Invocation Order

The agent autonomously decides tool order based on the system prompt. The recommended sequence is:

| Step | Tool                       | Responsibility                      |
| ---- | -------------------------- | ----------------------------------- |
| 1    | `security_check_tool`      | Check for unsafe execution requests |
| 2    | `detect_language_tool`     | Detect programming language         |
| 3    | `traceback_parser_tool`    | Extract error details               |
| 4    | `bug_classifier_tool`      | Identify bug category               |
| 5    | `fix_strategy_tool`        | Generate corrected code             |
| 6    | `test_case_generator_tool` | Generate test cases                 |

The final structured output is produced by `response_format=DebugReport` on `create_agent()`.

> Note: Unlike an explicit `StateGraph` with fixed edges, the agent may skip or reorder tools based on context (e.g., skip language detection if the user already specified the language).

---

## 9.5 Agent Flow

```text
START
  |
  v
User message → Agent reasoning loop
  |
  |── security_check_tool (always first per system prompt)
  |── detect_language_tool (if language unknown)
  |── traceback_parser_tool (if error/traceback provided)
  |── bug_classifier_tool (classify + root cause)
  |── fix_strategy_tool (generate corrected code)
  |── test_case_generator_tool (generate test cases)
  |
  v
Agent produces DebugReport (structured output)
  |
  v
END
```

---

# 10. LCEL Design

LCEL chains are used inside `@tool` functions for predictable, structured LLM calls. Each tool internally constructs a `prompt | model.with_structured_output(Schema)` chain.

Example chain (inside a tool):

```python
fix_chain = fix_prompt | model.with_structured_output(FixGeneration)
```

LCEL chains:

| Chain                   | Purpose                           | Used In                    |
| ----------------------- | --------------------------------- | -------------------------- |
| `debug_analysis_chain`  | Analyze issue and root cause      | `bug_classifier_tool`      |
| `fix_generation_chain`  | Generate corrected code           | `fix_strategy_tool`        |
| `test_generation_chain` | Generate test cases               | `test_case_generator_tool` |
| `final_report_chain`    | Produce final structured report   | standalone / agent output  |

Standalone chain modules are provided in `app/chains/` for reuse outside the agent context.

> Note: The agent also uses `response_format=DebugReport` on `create_agent()` for automatic structured output. The `final_report_chain` is available as a standalone LCEL chain for cases where you need to compile findings outside the agent context.

LCEL pipeline (inside each tool):

```text
Tool Input (args)
  |
  v
ChatPromptTemplate
  |
  v
init_chat_model("openai:gpt-4o-mini")
  |
  v
.with_structured_output(PydanticSchema)
  |
  v
Validated Pydantic Model → JSON string
```

---

# 11. Functional Requirements

## FR1: Submit Code for Debugging

The user should be able to submit:

```json
{
  "language": "python",
  "code": "def add(a,b): return a + c",
  "error_message": "NameError: name 'c' is not defined",
  "expected_behavior": "Return sum of a and b"
}
```

The assistant should return:

```json
{
  "language": "python",
  "issue": {
    "error_type": "NameError",
    "root_cause": "Variable c is used but not defined",
    "affected_line": 1,
    "severity": "medium"
  },
  "explanation": "The function receives a and b, but tries to return a + c. Since c does not exist, Python raises NameError.",
  "fixed_code": "def add(a, b):\n    return a + b",
  "changes_made": [
    "Replaced c with b"
  ],
  "test_cases": [
    "assert add(2, 3) == 5",
    "assert add(-1, 1) == 0"
  ],
  "prevention_tips": [
    "Use meaningful variable names",
    "Run small unit tests after writing functions"
  ],
  "confidence_score": 0.95
}
```

---

## FR2: Detect Programming Language

The assistant should detect the language if the user does not provide it.

Supported languages for MVP:

| Language       | Support Level                  |
| -------------- | ------------------------------ |
| Python         | High                           |
| JavaScript     | Medium                         |
| TypeScript     | Medium                         |
| PHP            | Basic                          |
| SQL            | Basic                          |
| Shell commands | Explanation only, no execution |

---

## FR3: Parse Error Details

The assistant should identify:

| Field         | Example                   |
| ------------- | ------------------------- |
| Error type    | `NameError`               |
| Error message | `name 'c' is not defined` |
| Affected line | `1`                       |
| File name     | `main.py`                 |
| Severity      | `medium`                  |

---

## FR4: Explain the Root Cause

The assistant should explain:

1. What went wrong.
2. Why it happened.
3. Where it happened.
4. How to fix it.
5. How to avoid it next time.

---

## FR5: Generate Fixed Code

The assistant should:

1. Make minimal changes.
2. Preserve user’s original intent.
3. Avoid unnecessary rewrites.
4. Add comments only when helpful.
5. Explain what changed.

---

## FR6: Generate Test Cases

The assistant should generate at least three test cases:

| Test Type  | Example                     |
| ---------- | --------------------------- |
| Happy path | Normal valid input          |
| Edge case  | Empty, zero, null, negative |
| Error case | Invalid input               |

---

## FR7: Support Multi-Turn Debugging

The assistant should support follow-up debugging in the same thread.

Example:

```text
User:
The fixed code is now giving TypeError.

Assistant:
Based on the previous code and new error, the issue is...
```

---

## FR8: Stream Progress

The assistant should stream progress messages before producing the final answer.

Required stream events:

```text
Reading code
Detecting language
Parsing error
Classifying issue
Generating fix
Generating tests
Preparing final report
```

---

## FR9: Return Structured Output

The final response must follow the `DebugReport` schema.

---

## FR10: Safety Handling

The assistant should refuse or safely respond when the user asks to:

| Unsafe Request       | Expected Behavior                       |
| -------------------- | --------------------------------------- |
| Execute unknown code | Refuse execution, offer static analysis |
| Delete files         | Refuse                                  |
| Access secrets       | Refuse                                  |
| Run shell scripts    | Explain only, do not execute            |
| Bypass systems       | Refuse and redirect safely              |

---

# 12. Non-Functional Requirements

| Requirement                  | Target                          |
| ---------------------------- | ------------------------------- |
| First response stream        | Under 2 seconds                 |
| Structured output compliance | 100%                            |
| Safety                       | No code execution in MVP        |
| Memory                       | Thread-based debugging sessions |
| Reliability                  | Retry model/tool failures       |
| Cost control                 | Model and tool call limits      |
| Observability                | LangSmith tracing               |
| Maintainability              | Modular graph nodes and tools   |
| Testability                  | Unit tests for tools and graph  |

---

# 13. Folder Structure

```text
code-debugger-assistant-langgraph/
│
├── app/
│   ├── graph.py                 ← create_agent() entry point (langgraph dev)
│   ├── state.py                 ← DebuggerState with add_messages reducer
│   │
│   ├── tools/                   ← @tool functions with LCEL chains inside
│   │   ├── security_check.py    ← Blocks unsafe requests
│   │   ├── language_detector.py ← Detects programming language
│   │   ├── traceback_parser.py  ← Parses error/traceback
│   │   ├── bug_classifier.py    ← Classifies bug + root cause
│   │   ├── fix_strategy.py      ← Generates corrected code
│   │   ├── test_generator.py    ← Generates test cases
│   │   └── utils.py             ← Safe stream writer helper
│   │
│   ├── chains/                  ← Standalone LCEL chains for reuse
│   │   ├── debug_analysis_chain.py
│   │   ├── fix_generation_chain.py
│   │   ├── test_generation_chain.py
│   │   └── final_report_chain.py ← Compiles findings into DebugReport
│   │
│   ├── schemas/
│   │   ├── request.py           ← DebugRequest input schema
│   │   └── response.py          ← DebugReport + DebugIssue output schemas
│   │
│   ├── prompts/
│   │   ├── debugger_prompt.py   ← System prompt + all ChatPromptTemplates
│   │   ├── fix_prompt.py        ← Re-exports GENERATE_FIX_PROMPT
│   │   └── test_prompt.py       ← Re-exports TEST_GENERATOR_PROMPT
│   │
│   └── middleware/              ← @wrap_tool_call middleware
│       ├── safety.py            ← Blocks unsafe patterns
│       ├── pii_detection.py     ← Detects PII/secrets in inputs
│       ├── retry.py             ← Retries transient failures
│       ├── logging.py           ← Logs tool calls with timing
│       ├── summarization.py     ← Monitors message history length
│       └── limits.py            ← Caps total tool calls per session
│
├── tests/
│   ├── test_graph.py            ← Structural tests for graph import
│   ├── test_tools.py            ← Unit tests for security_check_tool
│   └── test_structured_output.py ← Unit tests for DebugReport schema
│
├── main.py                      ← Interactive CLI runner (single + multi-turn)
├── langgraph.json
├── requirements.txt
├── .env.example
├── README.md
└── pyproject.toml
```

> Note: The `app/nodes/` directory is intentionally omitted because the `create_agent()` architecture replaces explicit graph nodes with autonomous tool invocation. All prompts are consolidated in `debugger_prompt.py`.

---

# 14. LangGraph Configuration

`langgraph.json`

```json
{
  "dependencies": ["."],
  "graphs": {
    "code_debugger": "./app/graph.py:graph"
  },
  "env": ".env"
}
```

---

# 15. Dependencies

`requirements.txt`

```text
langchain
langchain-openai
langgraph
langgraph-cli[inmem]
langgraph-sdk
langsmith
pydantic
python-dotenv
pytest
```

Optional for custom API routes:

```text
fastapi
uvicorn
```

---

# 16. Environment Variables

`.env.example`

```text
OPENAI_API_KEY=

LANGSMITH_TRACING=true
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=code-debugger-assistant
```

---

# 17. Sample User Input

```json
{
  "language": "python",
  "code": "def divide(a, b):\n    return a / b\n\nprint(divide(10, 0))",
  "error_message": "ZeroDivisionError: division by zero",
  "expected_behavior": "Handle division safely"
}
```

---

# 18. Sample Expected Output

```json
{
  "language": "python",
  "issue": {
    "error_type": "ZeroDivisionError",
    "root_cause": "The code attempts to divide by zero when b is 0.",
    "affected_line": 2,
    "severity": "medium"
  },
  "explanation": "In Python, dividing a number by zero is not allowed. The function should check whether b is zero before performing division.",
  "fixed_code": "def divide(a, b):\n    if b == 0:\n        return None\n    return a / b\n\nprint(divide(10, 0))",
  "changes_made": [
    "Added a check for b == 0 before division",
    "Returned None when division is not possible"
  ],
  "test_cases": [
    "assert divide(10, 2) == 5",
    "assert divide(10, 0) is None",
    "assert divide(-10, 2) == -5"
  ],
  "prevention_tips": [
    "Always validate divisor values before division",
    "Add unit tests for edge cases such as zero",
    "Use meaningful error handling for invalid input"
  ],
  "confidence_score": 0.96
}
```

---

# 19. Milestone Plan

## Milestone 1: Project Setup

| Task                  | Output             |
| --------------------- | ------------------ |
| Create project folder | Basic structure    |
| Add dependencies      | `requirements.txt` |
| Add environment file  | `.env.example`     |
| Add LangGraph config  | `langgraph.json`   |

---

## Milestone 2: Define Schemas and State

| Task                   | Output             |
| ---------------------- | ------------------ |
| Create request schema  | User input model   |
| Create response schema | `DebugReport`      |
| Create graph state     | `DebuggerState`    |
| Add validation         | Basic input checks |

---

## Milestone 3: Build Tools

| Task              | Output                 |
| ----------------- | ---------------------- |
| Language detector | Detect language        |
| Traceback parser  | Extract error info     |
| Bug classifier    | Categorize bug         |
| Security checker  | Detect unsafe requests |
| Test generator    | Suggest test cases     |

---

## Milestone 4: Build LCEL Chains

| Task                  | Output              |
| --------------------- | ------------------- |
| Debug analysis chain  | Root cause analysis |
| Fix generation chain  | Corrected code      |
| Test generation chain | Test suggestions    |
| Final report chain    | Structured output   |

---

## Milestone 5: Build Agent and Middleware

| Task                   | Output                                     |
| ---------------------- | ------------------------------------------ |
| Create agent           | `create_agent()` with tools + system prompt |
| Add checkpointer       | `MemorySaver()` for short-term memory       |
| Add safety middleware  | `@wrap_tool_call` safety blocks             |
| Add logging middleware | `@wrap_tool_call` logging with timing       |
| Add call limits        | `@wrap_tool_call` tool call cap             |
| Export graph           | `graph = debug_agent` for `langgraph dev`   |

---

## Milestone 6: Streaming and Testing

| Task                  | Output            |
| --------------------- | ----------------- |
| Add streaming updates | Progress messages |
| Test graph locally    | `langgraph dev`   |
| Add unit tests        | Tools and graph   |
| Add sample requests   | README examples   |

---

# 20. Acceptance Criteria

| Criteria                 | Expected Result                          |
| ------------------------ | ---------------------------------------- |
| Project runs locally     | `langgraph dev` starts successfully      |
| Graph is available       | `code_debugger` graph is loaded          |
| User can submit code     | Code and error input accepted            |
| Language detection works | Language is detected or confirmed        |
| Error parsing works      | Error type and line number extracted     |
| Root cause is explained  | Clear beginner-friendly explanation      |
| Fixed code is generated  | Minimal corrected code returned          |
| Tests are generated      | At least 3 test cases                    |
| Structured output works  | Response follows `DebugReport`           |
| Streaming works          | Progress messages are visible            |
| Memory works             | Same thread supports follow-up debugging |
| Safety works             | Assistant does not execute unsafe code   |
| Tracing works            | Runs are visible in LangSmith            |

---

# 21. Definition of Done

The project is complete when:

1. A user can submit code and an error message.
2. The assistant returns a structured debugging report.
3. The assistant explains the root cause clearly.
4. The assistant generates fixed code.
5. The assistant suggests test cases.
6. The assistant supports streaming progress.
7. The assistant supports multi-turn debugging.
8. The assistant uses LangChain tools, messages, models, structured output, short-term memory, and middleware.
9. The assistant runs locally through LangGraph Platform development tooling.
10. The project includes a clean README with setup, run instructions, and sample requests.
