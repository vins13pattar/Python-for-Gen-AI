"""
1. CrewAI Basics — Agents, Tasks, Crews & Processes
   Official docs: https://docs.crewai.com

CrewAI is a multi-agent orchestration framework.
Think of it like assembling a *team* (Crew) of specialist workers (Agents),
giving each one a specific job (Task), and choosing how they coordinate
(Process: sequential or hierarchical).

Key concepts:
  - Agent   : An autonomous unit with a role, goal, and backstory.
              The backstory gives the LLM persona-level context.
  - Task    : A discrete piece of work assigned to one agent.
              Has a description, expected_output, and optional context.
  - Crew    : The team that executes tasks using a chosen process.
  - Process : sequential (one-by-one) or hierarchical (manager delegates).

This file demonstrates the simplest possible Crew:
  Researcher agent → researches a topic
  Writer agent     → writes a short article based on the research
"""

import os
from dotenv import load_dotenv

# ── Load environment variables (.env must contain OPENAI_API_KEY) ──
load_dotenv()

# ── Import core CrewAI building blocks ──────────────────────────────
from crewai import Agent, Task, Crew, Process


# ═══════════════════════════════════════════════════════════════════
# 1. DEFINE AGENTS
# ═══════════════════════════════════════════════════════════════════
# Each Agent needs:
#   - role       : job title (used in prompts to the LLM)
#   - goal       : what the agent is trying to achieve
#   - backstory  : personality / expertise context for the LLM
#   - verbose    : if True, prints internal reasoning steps
#   - llm        : (optional) override the default LLM model

researcher = Agent(
    role="Senior Research Analyst",
    goal="Find the most relevant and accurate information about a given topic",
    backstory=(
        "You are an experienced research analyst with a PhD in Computer Science. "
        "You excel at breaking down complex topics into clear, digestible insights. "
        "You always cite your reasoning and think step by step."
    ),
    verbose=True,               # print agent's reasoning to console
    allow_delegation=False,     # this agent works alone, doesn't delegate to others
    # llm="gpt-4o-mini",       # uncomment to override the default model
)

writer = Agent(
    role="Tech Content Writer",
    goal="Write engaging, well-structured articles that explain technical topics clearly",
    backstory=(
        "You are a seasoned technical writer with 10+ years of experience "
        "writing for developer audiences. You simplify complex concepts "
        "without losing accuracy. Your writing is concise and engaging."
    ),
    verbose=True,
    allow_delegation=False,
)


# ═══════════════════════════════════════════════════════════════════
# 2. DEFINE TASKS
# ═══════════════════════════════════════════════════════════════════
# Each Task needs:
#   - description      : what to do (the prompt)
#   - expected_output  : format/shape of the result (guides the LLM)
#   - agent            : which agent handles this task

research_task = Task(
    description=(
        "Research the topic: 'How AI agents are transforming software development in 2025'. "
        "Find key trends, notable tools/frameworks, and real-world use cases. "
        "Organize your findings into clear bullet points."
    ),
    expected_output=(
        "A structured research brief with:\n"
        "- 5 key trends\n"
        "- 3 notable tools/frameworks with one-line descriptions\n"
        "- 2 real-world use cases"
    ),
    agent=researcher,       # assigned to the researcher agent
)

writing_task = Task(
    description=(
        "Using the research provided, write a short blog post (300-400 words) "
        "about AI agents in software development. "
        "Make it engaging, use subheadings, and conclude with a forward-looking statement."
    ),
    expected_output="A well-formatted blog post in Markdown, 300-400 words.",
    agent=writer,           # assigned to the writer agent
    context=[research_task],  # ← THIS IS KEY: passes the output of research_task
                              #   as context to the writer, creating a pipeline
)


# ═══════════════════════════════════════════════════════════════════
# 3. ASSEMBLE & RUN THE CREW
# ═══════════════════════════════════════════════════════════════════
# Crew ties everything together:
#   - agents  : list of all agents in the team
#   - tasks   : list of tasks (order matters for sequential process)
#   - process : Process.sequential = tasks run one after another
#               Process.hierarchical = a manager agent delegates tasks
#   - verbose : if True, prints the full execution trace

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential,     # researcher first, then writer
    verbose=True,                   # show detailed execution logs
)

# kickoff() starts the crew's execution and returns the final result
# This is the main entry point — like calling .invoke() in LangChain
result = crew.kickoff()

# ── Print the final output ──────────────────────────────────────────
print("\n" + "=" * 60)
print("  FINAL OUTPUT")
print("=" * 60)
print(result)

# result.raw       → the raw string output
# result.tasks     → individual task outputs
# result.token_usage → token consumption stats
print("\n── Token Usage ──")
print(result.token_usage)
