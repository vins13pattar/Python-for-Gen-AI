"""
4. MCP Prompts — Reusable Prompt Templates Exposed by Servers

Official docs: https://modelcontextprotocol.io/docs/concepts/prompts

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT ARE MCP PROMPTS?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Prompts are pre-defined, reusable message templates that the SERVER
exposes to clients (and ultimately to the LLM or user).

Think of prompts as "slash commands" or "prompt macros":
  /summarize → fills in the summarization prompt template
  /code-review → fills in the code review prompt template

Prompts vs Tools vs Resources:
  Tools     → execute actions (write/compute)
  Resources → read data (files/DB)
  Prompts   → provide structured message sequences to the LLM

Prompt message types:
  role: "user"      → simulates user input
  role: "assistant" → simulates prior LLM output
  role: "system"    → system-level instructions

Prompt content types:
  TextContent       → plain text
  ImageContent      → base64 image
  EmbeddedResource  → reference to a resource URI

Use cases for MCP Prompts:
  - Slash commands in chat UIs (e.g., /explain, /summarize)
  - Complex multi-turn conversation starters
  - Domain-specific system prompts (code review, analysis)
  - Few-shot example sequences for consistent LLM behavior

This example covers:
  ① Simple prompt with no arguments
  ② Prompt with required arguments
  ③ Prompt with optional arguments and defaults
  ④ Multi-turn prompt (user + assistant messages)
  ⑤ Prompt embedding a resource reference
  ⑥ Listing and getting prompts from client side
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import asyncio
import json
import os
import sys

SERVER_CODE = '''
"""MCP Prompts demo server."""
from mcp.server.fastmcp import FastMCP
from mcp.types import (
    GetPromptResult, PromptMessage, TextContent,
    EmbeddedResource, TextResourceContents
)

mcp = FastMCP("PromptsDemoServer")


# ─────────────────────────────────────────────────────────────────────────
# ① SIMPLE PROMPT — no arguments, static template
# ─────────────────────────────────────────────────────────────────────────
@mcp.prompt()
def python_expert_persona() -> str:
    """
    A system prompt that configures the LLM as a Python expert.
    Use this at the start of any Python coding conversation.
    """
    return (
        "You are an expert Python developer with 15+ years of experience. "
        "You write clean, idiomatic, well-documented Python code. "
        "You follow PEP 8 style guidelines and modern best practices. "
        "Always explain your code choices and suggest improvements."
    )


# ─────────────────────────────────────────────────────────────────────────
# ② PROMPT WITH REQUIRED ARGUMENTS
# ─────────────────────────────────────────────────────────────────────────
@mcp.prompt()
def summarize_text(text: str, target_length: str) -> str:
    """
    Summarize a given text to the specified target length.

    Args:
        text: The content to summarize.
        target_length: Desired summary length: 'brief', 'medium', or 'detailed'.
    """
    length_guides = {
        "brief":    "1-2 sentences",
        "medium":   "1 short paragraph (3-5 sentences)",
        "detailed": "2-3 paragraphs with key points"
    }
    guide = length_guides.get(target_length, "1 paragraph")

    return (
        f"Please summarize the following text in {guide}. "
        f"Preserve the key information and main ideas.\\n\\n"
        f"Text to summarize:\\n```\\n{text}\\n```"
    )


# ─────────────────────────────────────────────────────────────────────────
# ③ PROMPT WITH OPTIONAL ARGUMENTS
# ─────────────────────────────────────────────────────────────────────────
@mcp.prompt()
def code_review(
    code: str,
    language: str = "python",
    focus: str = "all"
) -> str:
    """
    Perform a code review on the provided code.

    Args:
        code: The source code to review.
        language: Programming language (default: python).
        focus: Review focus area — 'security', 'performance', 'readability', or 'all'.
    """
    focus_instructions = {
        "security":    "Focus specifically on security vulnerabilities and risks.",
        "performance": "Focus specifically on performance bottlenecks and optimizations.",
        "readability": "Focus specifically on code clarity and maintainability.",
        "all":         "Provide a comprehensive review covering security, performance, and readability."
    }
    instructions = focus_instructions.get(focus, focus_instructions["all"])

    return (
        f"You are a senior {language} developer conducting a code review.\\n\\n"
        f"{instructions}\\n\\n"
        f"For each issue found, provide:\\n"
        f"  - Severity: Critical | High | Medium | Low\\n"
        f"  - Description of the issue\\n"
        f"  - Suggested fix with code example\\n\\n"
        f"Code to review ({language}):\\n"
        f"```{language}\\n{code}\\n```"
    )


# ─────────────────────────────────────────────────────────────────────────
# ④ MULTI-TURN PROMPT — returns list of messages (user + assistant turns)
#
# FastMCP prompts returning a list create a full conversation scaffold.
# This is useful for few-shot examples or simulating prior context.
# ─────────────────────────────────────────────────────────────────────────
@mcp.prompt()
def explain_concept(concept: str) -> list[dict]:
    """
    Multi-turn few-shot prompt for explaining technical concepts clearly.
    Includes example turns to guide the LLM's explanation style.

    Args:
        concept: The technical concept to explain.
    """
    return [
        {
            "role": "user",
            "content": "Can you explain what an API is?"
        },
        {
            "role": "assistant",
            "content": (
                "An API (Application Programming Interface) is like a waiter in a restaurant. "
                "You (the client) don't go into the kitchen yourself — instead, you tell the waiter "
                "what you want, they take your order to the kitchen (server), and bring back your food (response). "
                "In tech terms, an API defines the rules for how software components talk to each other."
            )
        },
        {
            "role": "user",
            "content": f"Can you explain what {concept} is in the same simple, analogy-based style?"
        }
    ]


# ─────────────────────────────────────────────────────────────────────────
# ⑤ DEBUGGING ASSISTANT PROMPT — production-grade multi-turn template
# ─────────────────────────────────────────────────────────────────────────
@mcp.prompt()
def debug_error(error_message: str, code_context: str, language: str = "python") -> list[dict]:
    """
    Structured debugging assistant prompt.

    Args:
        error_message: The error/exception message.
        code_context: The relevant code snippet where the error occurs.
        language: Programming language (default: python).
    """
    return [
        {
            "role": "user",
            "content": (
                f"I'm getting the following error in my {language} code:\\n\\n"
                f"**Error:**\\n```\\n{error_message}\\n```\\n\\n"
                f"**Code:**\\n```{language}\\n{code_context}\\n```\\n\\n"
                f"Please help me debug this. Explain:\\n"
                f"1. What is causing this error?\\n"
                f"2. How to fix it?\\n"
                f"3. How to prevent similar errors in the future?"
            )
        }
    ]


if __name__ == "__main__":
    mcp.run()
'''

async def run_prompts_demo():
    server_file = os.path.join(os.path.dirname(__file__), "_temp_server_prompts.py")
    with open(server_file, "w") as f:
        f.write(SERVER_CODE)

    print("=" * 65)
    print("  MCP PROMPTS DEMO")
    print("=" * 65)
    print()

    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_file],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✅ Connected to PromptsDemoServer\n")

                # ── ⑥ List all prompts ─────────────────────────────────────
                print("━━━ ⑥ list_prompts() — Discover prompt templates ━━━━━")
                prompts_result = await session.list_prompts()
                print(f"📝 Server exposes {len(prompts_result.prompts)} prompt(s):\n")
                for p in prompts_result.prompts:
                    print(f"   📌 Name: {p.name}")
                    print(f"      Desc: {p.description}")
                    if p.arguments:
                        args_str = ", ".join(
                            f"{a.name}{'?' if not a.required else ''}"
                            for a in p.arguments
                        )
                        print(f"      Args: ({args_str})")
                    print()

                # ── ① Simple prompt ────────────────────────────────────────
                print("━━━ ① Simple Prompt: python_expert_persona ━━━━━━━━━━━")
                result = await session.get_prompt("python_expert_persona", arguments={})
                print(f"   Messages: {len(result.messages)}")
                print(f"   [system] {result.messages[0].content.text[:100]}...\n")

                # ── ② Required args ────────────────────────────────────────
                print("━━━ ② Required Args: summarize_text ━━━━━━━━━━━━━━━━━━")
                sample_text = (
                    "The Model Context Protocol (MCP) is an open standard that enables "
                    "seamless integration between LLM applications and external data sources. "
                    "It provides a standardized way to connect AI models to tools, files, "
                    "databases, and APIs through a unified protocol layer."
                )
                result = await session.get_prompt(
                    "summarize_text",
                    arguments={"text": sample_text, "target_length": "brief"}
                )
                print(f"   Generated prompt:\n   {result.messages[0].content.text[:200]}...\n")

                # ── ③ Optional args ────────────────────────────────────────
                print("━━━ ③ Optional Args: code_review ━━━━━━━━━━━━━━━━━━━━━")
                sample_code = "password = 'admin123'\nresult = eval(user_input)"
                result = await session.get_prompt(
                    "code_review",
                    arguments={
                        "code": sample_code,
                        "language": "python",
                        "focus": "security"   # optional override
                    }
                )
                print(f"   Generated prompt:\n   {result.messages[0].content.text[:200]}...\n")

                # ── ④ Multi-turn prompt ────────────────────────────────────
                print("━━━ ④ Multi-turn: explain_concept ━━━━━━━━━━━━━━━━━━━━")
                result = await session.get_prompt(
                    "explain_concept",
                    arguments={"concept": "Model Context Protocol (MCP)"}
                )
                print(f"   Message count: {len(result.messages)} turns")
                for msg in result.messages:
                    role = msg.role
                    text = msg.content.text[:80] + "..." if len(msg.content.text) > 80 else msg.content.text
                    print(f"   [{role:9}] {text}")
                print()

                # ── ⑤ Debug assistant prompt ───────────────────────────────
                print("━━━ ⑤ Debug Prompt: debug_error ━━━━━━━━━━━━━━━━━━━━━━")
                result = await session.get_prompt(
                    "debug_error",
                    arguments={
                        "error_message": "KeyError: 'user_id'\n  File app.py, line 42",
                        "code_context": "def get_user(data):\n    return data['user_id']",
                    }
                )
                print(f"   Messages: {len(result.messages)}")
                print(f"   [{result.messages[0].role}] {result.messages[0].content.text[:150]}...\n")

    finally:
        if os.path.exists(server_file):
            os.remove(server_file)

    print("=" * 65)
    print("  KEY TAKEAWAYS — MCP Prompts")
    print("=" * 65)
    print("""
  ① @mcp.prompt() decorator registers a prompt template
  ② Returning str → single user message
  ③ Returning list[dict] → multi-turn conversation scaffold
  ④ Arguments become prompt variables (required or optional)
  ⑤ Prompt descriptions guide UI/agent on when to use them
  ⑥ session.list_prompts() → discover all templates + args
  ⑦ session.get_prompt(name, arguments) → render the template
  ⑧ Use prompts for: slash commands, few-shot examples, personas
    """)


if __name__ == "__main__":
    print("\n📝 MCP Prompts Example")
    print("   Demonstrates: static, parameterized, and multi-turn prompt templates\n")
    asyncio.run(run_prompts_demo())
