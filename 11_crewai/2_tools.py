"""
2. CrewAI Tools — Built-in tools, custom tools, and the @tool decorator
   Official docs: https://docs.crewai.com/concepts/tools

Tools give agents the ability to interact with the outside world:
  - Search the web
  - Read/write files
  - Query APIs
  - Perform calculations
  - Scrape websites

CrewAI provides:
  (a) Built-in tools   : from crewai_tools (SerperDevTool, FileReadTool, etc.)
  (b) Custom tools      : using the @tool decorator (similar to LangChain)
  (c) LangChain tools   : any LangChain tool works with CrewAI agents

This file demonstrates all three approaches.
"""

import os
import json
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Task, Crew, Process
from crewai.tools import tool            # the @tool decorator


# ═══════════════════════════════════════════════════════════════════
# 1. CUSTOM TOOLS — Using the @tool decorator
# ═══════════════════════════════════════════════════════════════════
# The @tool decorator converts a Python function into a tool
# that CrewAI agents can call. The function's docstring becomes
# the tool's description (which the LLM uses to decide when to call it).

@tool("Calculator")
def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression and return the result.
    Input should be a valid Python math expression like '2 + 3 * 4'.
    """
    try:
        # Using eval safely for math expressions
        result = eval(expression, {"__builtins__": {}}, {})
        return f"The result of {expression} = {result}"
    except Exception as e:
        return f"Error evaluating '{expression}': {e}"


@tool("WordCounter")
def word_counter(text: str) -> str:
    """
    Count the number of words, sentences, and characters in a given text.
    Useful for content analysis and editing tasks.
    """
    words = len(text.split())
    sentences = text.count('.') + text.count('!') + text.count('?')
    characters = len(text)
    return (
        f"Word count: {words}\n"
        f"Sentence count: {sentences}\n"
        f"Character count: {characters}"
    )


@tool("JSONFormatter")
def json_formatter(data: str) -> str:
    """
    Parse a JSON string and return it in a pretty-printed, readable format.
    Input should be a valid JSON string.
    """
    try:
        parsed = json.loads(data)
        return json.dumps(parsed, indent=2, ensure_ascii=False)
    except json.JSONDecodeError as e:
        return f"Invalid JSON: {e}"


# ═══════════════════════════════════════════════════════════════════
# 2. BUILT-IN TOOLS from crewai_tools (requires: pip install crewai-tools)
# ═══════════════════════════════════════════════════════════════════
# SerperDevTool  : Google search (needs SERPER_API_KEY)
# FileReadTool   : Read local files
# DirectoryReadTool : List directory contents
# WebsiteSearchTool : Scrape and search a website
# ... and many more

# We'll try to import SerperDevTool; skip if SERPER_API_KEY not set
try:
    from crewai_tools import SerperDevTool
    serper_tool = SerperDevTool()  # Uses SERPER_API_KEY from env
    search_tools = [serper_tool]
    print("✓ SerperDevTool loaded (web search enabled)")
except Exception:
    search_tools = []
    print("⚠ SerperDevTool not available (set SERPER_API_KEY for web search)")


# ═══════════════════════════════════════════════════════════════════
# 3. AGENTS WITH TOOLS
# ═══════════════════════════════════════════════════════════════════
# Assign tools to agents via the `tools` parameter.
# The agent's LLM will see the tool descriptions and decide when to use them.

math_analyst = Agent(
    role="Mathematical Analyst",
    goal="Solve mathematical problems accurately using the calculator tool",
    backstory=(
        "You are a meticulous mathematician who always uses the calculator tool "
        "to verify computations. You never do mental math — you always use tools."
    ),
    tools=[calculator],          # ← attach the custom calculator tool
    verbose=True,
    allow_delegation=False,
)

content_editor = Agent(
    role="Content Editor",
    goal="Analyze and improve written content using text analysis tools",
    backstory=(
        "You are a professional content editor who uses analytical tools "
        "to assess content quality. You provide data-driven feedback."
    ),
    tools=[word_counter],        # ← attach the word counter tool
    verbose=True,
    allow_delegation=False,
)

# If web search is available, create a researcher with search capability
if search_tools:
    web_researcher = Agent(
        role="Web Researcher",
        goal="Find the latest information about topics using web search",
        backstory="You are an expert web researcher who finds accurate, up-to-date info.",
        tools=search_tools,      # ← attach the SerperDevTool
        verbose=True,
        allow_delegation=False,
    )


# ═══════════════════════════════════════════════════════════════════
# 4. TASKS THAT USE TOOLS
# ═══════════════════════════════════════════════════════════════════

math_task = Task(
    description=(
        "Solve the following math problems using the Calculator tool:\n"
        "1. What is 15 * 27 + 89?\n"
        "2. What is 2 ** 10?\n"
        "3. What is (144 / 12) + (7 * 8)?\n"
        "Present each answer clearly."
    ),
    expected_output=(
        "A list of 3 math problems with their solutions, "
        "clearly showing the expression and result for each."
    ),
    agent=math_analyst,
)

content_task = Task(
    description=(
        "Analyze the following text using the WordCounter tool:\n\n"
        "'Artificial intelligence is reshaping how we build software. "
        "From code generation to automated testing, AI tools are becoming "
        "essential in every developer's toolkit. The future of software "
        "development is collaborative — humans and AI working together.'\n\n"
        "Provide the word count analysis and suggest improvements."
    ),
    expected_output=(
        "Word count statistics from the tool, followed by "
        "2-3 concrete suggestions to improve the text."
    ),
    agent=content_editor,
)


# ═══════════════════════════════════════════════════════════════════
# 5. RUN THE CREW
# ═══════════════════════════════════════════════════════════════════

crew = Crew(
    agents=[math_analyst, content_editor],
    tasks=[math_task, content_task],
    process=Process.sequential,
    verbose=True,
)

print("\n" + "=" * 60)
print("  STARTING TOOLS DEMO CREW")
print("=" * 60)

result = crew.kickoff()

print("\n" + "=" * 60)
print("  FINAL OUTPUT")
print("=" * 60)
print(result)
