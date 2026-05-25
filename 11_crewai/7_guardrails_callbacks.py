"""
7. CrewAI Guardrails, Callbacks & Structured Output
   Official docs: https://docs.crewai.com/concepts/tasks#structured-output
                   https://docs.crewai.com/concepts/tasks#callbacks

This file covers three advanced features:

  (a) Structured Output : Force tasks to return Pydantic models instead of strings.
      This is essential for downstream processing (APIs, databases, pipelines).

  (b) Task Callbacks    : Functions called after a task completes.
      Useful for logging, metrics, notifications, or side effects.

  (c) Guardrails       : Validation functions that run on task output.
      If validation fails, the agent is asked to retry.
      Prevents bad outputs from propagating through the pipeline.

These features turn CrewAI from a toy into a production-ready tool.
"""

import os
from typing import List
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Task, Crew, Process
from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════
# 1. STRUCTURED OUTPUT — Pydantic models for task results
# ═══════════════════════════════════════════════════════════════════
# Instead of raw strings, tasks can return structured Pydantic objects.
# This guarantees a specific shape and enables downstream type safety.

class TrendItem(BaseModel):
    """A single technology trend."""
    name: str = Field(description="Name of the trend")
    description: str = Field(description="One-line description of the trend")
    impact_score: int = Field(
        description="Impact score from 1-10",
        ge=1, le=10  # ← Pydantic validation: must be between 1 and 10
    )


class TrendReport(BaseModel):
    """A structured report containing multiple trends."""
    title: str = Field(description="Report title")
    trends: List[TrendItem] = Field(description="List of identified trends")
    summary: str = Field(description="Executive summary in 2-3 sentences")
    total_trends: int = Field(description="Total number of trends identified")


# ═══════════════════════════════════════════════════════════════════
# 2. CALLBACK FUNCTIONS — Called after task completion
# ═══════════════════════════════════════════════════════════════════
# Callbacks receive the task output and can perform side effects:
#   - Logging to a file or monitoring service
#   - Sending notifications (Slack, email)
#   - Updating a database
#   - Computing metrics

def log_task_completion(output):
    """
    Callback: Log task completion details.
    Called automatically after the task finishes.
    
    Args:
        output: The TaskOutput object from the completed task
    """
    print("\n" + "─" * 40)
    print("📋 CALLBACK: Task completed!")
    print(f"   Description: {output.description[:60]}...")
    print(f"   Agent: {output.agent}")
    print(f"   Output length: {len(str(output.raw))} chars")
    print("─" * 40)


def metrics_callback(output):
    """
    Callback: Compute and display metrics on the output.
    In production, you'd send these to a monitoring dashboard.
    """
    raw_output = str(output.raw)
    word_count = len(raw_output.split())
    sentence_count = raw_output.count('.') + raw_output.count('!') + raw_output.count('?')

    print("\n" + "─" * 40)
    print("📊 METRICS CALLBACK:")
    print(f"   Words: {word_count}")
    print(f"   Sentences: {sentence_count}")
    print(f"   Avg words/sentence: {word_count / max(sentence_count, 1):.1f}")
    print("─" * 40)


# ═══════════════════════════════════════════════════════════════════
# 3. GUARDRAIL FUNCTIONS — Validate output before accepting
# ═══════════════════════════════════════════════════════════════════
# Guardrails are validation functions that check the task output.
# Return (True, output) if valid, or (False, "error message") to retry.
# The agent will see the error message and try to fix its output.

def validate_trend_count(output) -> tuple:
    """
    Guardrail: Ensure the report contains at least 3 trends.
    If not, the agent is asked to retry with feedback.
    
    Args:
        output: The TaskOutput object
    
    Returns:
        (True, output) if valid
        (False, error_message) if invalid — agent will retry
    """
    try:
        # Try to parse the structured output
        if hasattr(output, 'pydantic') and output.pydantic:
            report = output.pydantic
            if len(report.trends) >= 3:
                print("✅ Guardrail passed: Found enough trends")
                return (True, output)
            else:
                return (
                    False,
                    f"Found only {len(report.trends)} trends. "
                    "Please provide at least 3 trends. Add more trends to your report."
                )
        # Fallback: check raw output
        raw = str(output.raw)
        if len(raw) > 200:
            return (True, output)
        return (False, "Output is too short. Please provide a more detailed report.")
    except Exception as e:
        return (False, f"Validation error: {e}. Please try again.")


def validate_no_placeholder(output) -> tuple:
    """
    Guardrail: Reject outputs that contain placeholder text.
    Common with LLMs that generate "[insert here]" type content.
    """
    raw = str(output.raw).lower()
    placeholders = ["[insert", "[todo", "[placeholder", "lorem ipsum", "[your"]

    for placeholder in placeholders:
        if placeholder in raw:
            return (
                False,
                f"Output contains placeholder text: '{placeholder}'. "
                "Please replace all placeholders with actual content."
            )

    print("✅ Guardrail passed: No placeholders found")
    return (True, output)


# ═══════════════════════════════════════════════════════════════════
# 4. AGENTS
# ═══════════════════════════════════════════════════════════════════

trend_analyst = Agent(
    role="Technology Trend Analyst",
    goal="Identify and analyze the most impactful technology trends",
    backstory=(
        "You are a renowned technology analyst who has correctly predicted "
        "major tech shifts for over a decade. You provide data-driven "
        "analysis with clear impact assessments."
    ),
    verbose=True,
    allow_delegation=False,
)

report_writer = Agent(
    role="Executive Report Writer",
    goal="Produce clear, actionable executive reports",
    backstory=(
        "You are a professional report writer who creates polished "
        "executive summaries. You always write real content — never "
        "use placeholders or filler text."
    ),
    verbose=True,
    allow_delegation=False,
)


# ═══════════════════════════════════════════════════════════════════
# 5. TASKS WITH STRUCTURED OUTPUT, CALLBACKS & GUARDRAILS
# ═══════════════════════════════════════════════════════════════════

trend_analysis_task = Task(
    description=(
        "Identify the top 5 technology trends for 2025-2026. "
        "For each trend, provide a name, one-line description, and "
        "an impact score from 1-10. "
        "Also provide an executive summary."
    ),
    expected_output=(
        "A structured trend report with a title, 5 trends "
        "(each with name, description, impact_score), "
        "a summary, and total_trends count."
    ),
    agent=trend_analyst,
    output_pydantic=TrendReport,      # ← STRUCTURED OUTPUT!
    # The agent's output will be parsed into a TrendReport Pydantic model.
    # If parsing fails, the agent is asked to fix its output.

    callback=log_task_completion,      # ← CALLBACK: runs after completion
    guardrail=validate_trend_count,    # ← GUARDRAIL: validates output
)

executive_summary_task = Task(
    description=(
        "Based on the trend analysis, write a compelling executive summary "
        "(200-300 words) suitable for a board presentation. "
        "Highlight the top 3 trends and their business implications. "
        "Do NOT use any placeholder text — write real, substantive content."
    ),
    expected_output=(
        "A polished executive summary in Markdown, 200-300 words, "
        "with specific insights and recommendations."
    ),
    agent=report_writer,
    context=[trend_analysis_task],
    callback=metrics_callback,         # ← CALLBACK: compute metrics
    guardrail=validate_no_placeholder, # ← GUARDRAIL: no placeholders
)


# ═══════════════════════════════════════════════════════════════════
# 6. RUN THE CREW
# ═══════════════════════════════════════════════════════════════════

crew = Crew(
    agents=[trend_analyst, report_writer],
    tasks=[trend_analysis_task, executive_summary_task],
    process=Process.sequential,
    verbose=True,
)

print("═" * 60)
print("  GUARDRAILS & STRUCTURED OUTPUT DEMO")
print("  Features: Pydantic output, callbacks, guardrails")
print("═" * 60)

result = crew.kickoff()

# ═══════════════════════════════════════════════════════════════════
# 7. ACCESS STRUCTURED OUTPUT
# ═══════════════════════════════════════════════════════════════════

print("\n" + "═" * 60)
print("  STRUCTURED OUTPUT — Accessing Pydantic Model")
print("═" * 60)

# The first task's output is a TrendReport Pydantic model
if trend_analysis_task.output and hasattr(trend_analysis_task.output, 'pydantic'):
    report: TrendReport = trend_analysis_task.output.pydantic
    if report:
        print(f"\n  Report Title: {report.title}")
        print(f"  Total Trends: {report.total_trends}")
        print(f"\n  Trends:")
        for i, trend in enumerate(report.trends, 1):
            print(f"    {i}. {trend.name} (Impact: {trend.impact_score}/10)")
            print(f"       {trend.description}")
        print(f"\n  Summary: {report.summary}")
    else:
        print("  (Structured output not available — showing raw)")
        print(f"  {trend_analysis_task.output.raw[:300]}...")
else:
    print("  Raw output:")
    print(f"  {result}")

print("\n" + "═" * 60)
print("  EXECUTIVE SUMMARY")
print("═" * 60)
print(result)
