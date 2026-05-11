"""
Code Debugger Assistant — LangGraph graph entry point.

This module builds a LangChain agent using create_agent() and exposes it
as `graph` so that `langgraph dev` can discover and serve it.

Architecture (per PRD §8 and §9):
  - create_agent() with 6 tools
  - Middleware: safety, PII detection, retry, logging, summarization, call-limits
  - response_format=DebugReport for structured output

Note: The checkpointer is NOT set here because LangGraph Platform provides
its own persistence. For local runs (main.py), the checkpointer is added
at invocation time.
"""
from langchain.agents import create_agent

from app.schemas.response import DebugReport
from app.prompts.debugger_prompt import DEBUGGER_SYSTEM_PROMPT

# Tools
from app.tools.security_check import security_check_tool
from app.tools.language_detector import detect_language_tool
from app.tools.traceback_parser import traceback_parser_tool
from app.tools.bug_classifier import bug_classifier_tool
from app.tools.fix_strategy import fix_strategy_tool
from app.tools.test_generator import test_case_generator_tool

# Middleware
from app.middleware.safety import safety_middleware
from app.middleware.pii_detection import pii_detection_middleware
from app.middleware.retry import retry_middleware
from app.middleware.logging import logging_middleware
from app.middleware.summarization import summarization_middleware
from app.middleware.limits import limits_middleware

# ── Agent ────────────────────────────────────────────────────────────────────

debug_agent = create_agent(
    model="openai:gpt-4.1-mini",
    tools=[
        security_check_tool,
        detect_language_tool,
        traceback_parser_tool,
        bug_classifier_tool,
        fix_strategy_tool,
        test_case_generator_tool,
    ],
    system_prompt=DEBUGGER_SYSTEM_PROMPT,
    middleware=[
        safety_middleware,
        pii_detection_middleware,
        retry_middleware,
        logging_middleware,
        summarization_middleware,
        limits_middleware,
    ],
    response_format=DebugReport,
)

# Expose as `graph` for `langgraph dev` (langgraph.json points here)
graph = debug_agent
