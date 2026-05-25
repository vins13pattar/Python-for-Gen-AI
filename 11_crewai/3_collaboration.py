"""
3. CrewAI Collaboration — Delegation, Context Sharing & Memory
   Official docs: https://docs.crewai.com/concepts/collaboration

Agent collaboration is what makes CrewAI powerful.
Instead of isolated agents, you build *teams* that share context and delegate.

Key collaboration features:
  (a) Context passing : Task.context=[other_task] passes output downstream
  (b) Delegation      : allow_delegation=True lets an agent ask another for help
  (c) Memory          : Crew-level memory so agents remember past interactions
      - Short-term  : within the current execution
      - Long-term   : persists across executions (uses embeddings)
      - Entity      : remembers facts about specific entities (people, companies)

This file demonstrates a 3-agent team where:
  Researcher → gathers info
  Analyst    → analyzes findings (receives researcher context)
  Writer     → writes final report (receives both contexts)
"""

import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Task, Crew, Process


# ═══════════════════════════════════════════════════════════════════
# 1. AGENTS WITH DELEGATION
# ═══════════════════════════════════════════════════════════════════
# allow_delegation=True means this agent CAN ask other agents for help.
# The agent's LLM decides when to delegate based on the task complexity.

researcher = Agent(
    role="Market Researcher",
    goal="Gather comprehensive data about market trends in AI",
    backstory=(
        "You are a market research specialist who excels at identifying "
        "emerging trends and collecting data from multiple perspectives. "
        "You provide raw data and facts, not opinions."
    ),
    verbose=True,
    allow_delegation=False,   # Researcher works independently
)

analyst = Agent(
    role="Data Analyst",
    goal="Analyze research data and extract actionable insights",
    backstory=(
        "You are a senior data analyst with expertise in trend analysis. "
        "You take raw research data, identify patterns, and produce "
        "clear analytical summaries with supporting evidence."
    ),
    verbose=True,
    allow_delegation=True,    # ← Can delegate to researcher if needed!
    # When the analyst encounters something it can't answer,
    # it can ask the researcher to help. The LLM decides when.
)

writer = Agent(
    role="Report Writer",
    goal="Produce polished, executive-ready reports",
    backstory=(
        "You are an expert business writer who transforms analytical "
        "insights into clear, compelling executive summaries. "
        "You focus on actionable recommendations."
    ),
    verbose=True,
    allow_delegation=True,    # ← Can ask analyst or researcher for more detail
)


# ═══════════════════════════════════════════════════════════════════
# 2. TASKS WITH CONTEXT CHAINING
# ═══════════════════════════════════════════════════════════════════
# context=[task1, task2] passes the outputs of task1 and task2
# as additional context when this task executes.
# This is how you create a data pipeline between agents.

research_task = Task(
    description=(
        "Research the current state of AI agents in enterprise software. "
        "Cover: market size, key players (at least 5), adoption rates, "
        "and common use cases. Focus on 2024-2025 data."
    ),
    expected_output=(
        "A detailed research brief with:\n"
        "- Market size and growth rate\n"
        "- Top 5 key players with brief descriptions\n"
        "- Adoption statistics\n"
        "- Top 5 use cases"
    ),
    agent=researcher,
)

analysis_task = Task(
    description=(
        "Analyze the research data provided and identify:\n"
        "1. The top 3 growth opportunities\n"
        "2. The biggest challenges/risks\n"
        "3. A SWOT analysis for companies adopting AI agents\n"
        "Support each point with data from the research."
    ),
    expected_output=(
        "An analytical report with:\n"
        "- 3 growth opportunities (with data backing)\n"
        "- 3 key risks/challenges\n"
        "- SWOT analysis table"
    ),
    agent=analyst,
    context=[research_task],   # ← receives output from research_task
)

report_task = Task(
    description=(
        "Write an executive summary report that combines the research "
        "and analysis into a clear, 500-word business brief. "
        "Include an executive summary, key findings, and 3 recommendations. "
        "Make it suitable for a C-level audience."
    ),
    expected_output=(
        "A professional executive summary in Markdown format with:\n"
        "- Executive Summary (2-3 sentences)\n"
        "- Key Findings section\n"
        "- Recommendations (3 actionable items)\n"
        "- Approximately 500 words"
    ),
    agent=writer,
    context=[research_task, analysis_task],  # ← receives BOTH outputs
    # The writer sees the full picture: raw research + analysis
)


# ═══════════════════════════════════════════════════════════════════
# 3. CREW WITH MEMORY
# ═══════════════════════════════════════════════════════════════════
# memory=True enables the crew's shared memory system.
# This allows agents to:
#   - Remember what other agents said (short-term)
#   - Build persistent knowledge (long-term, requires embeddings)
#   - Track entities mentioned in conversations (entity memory)

crew = Crew(
    agents=[researcher, analyst, writer],
    tasks=[research_task, analysis_task, report_task],
    process=Process.sequential,
    verbose=True,
    memory=True,                  # ← Enable shared memory
    # memory_config={            # Optional: configure memory backend
    #     "provider": "mem0",    # Use Mem0 for long-term memory
    # },
)


# ═══════════════════════════════════════════════════════════════════
# 4. RUN THE CREW
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  STARTING COLLABORATION DEMO")
print("  Researcher → Analyst → Writer (with context chaining)")
print("=" * 60)

result = crew.kickoff()

print("\n" + "=" * 60)
print("  FINAL EXECUTIVE REPORT")
print("=" * 60)
print(result)

# ═══════════════════════════════════════════════════════════════════
# 5. INSPECT INDIVIDUAL TASK OUTPUTS
# ═══════════════════════════════════════════════════════════════════
# Each task's output is accessible after execution

print("\n" + "─" * 60)
print("  INDIVIDUAL TASK OUTPUTS")
print("─" * 60)

for i, task in enumerate([research_task, analysis_task, report_task]):
    print(f"\n── Task {i+1}: {task.description[:50]}...")
    if task.output:
        print(f"   Output preview: {str(task.output)[:200]}...")
