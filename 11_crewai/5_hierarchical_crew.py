"""
5. CrewAI Hierarchical Process — Manager Agent Orchestration
   Official docs: https://docs.crewai.com/concepts/processes

CrewAI supports two execution processes:

  1. Process.sequential   (default)
     → Tasks execute one after another, in the order defined.
     → Simple, predictable, easy to debug.

  2. Process.hierarchical
     → A *manager agent* is automatically created (or you provide one).
     → The manager reads ALL tasks, decides which agent handles what,
       reviews results, and can re-assign if unsatisfied.
     → More flexible, better for complex workflows where task order
       isn't fixed or where agents need to collaborate dynamically.

This file demonstrates Process.hierarchical with a team of specialists.
"""

import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Task, Crew, Process


# ═══════════════════════════════════════════════════════════════════
# 1. SPECIALIST AGENTS
# ═══════════════════════════════════════════════════════════════════
# In hierarchical mode, the manager will delegate to these agents.
# The manager decides WHO does WHAT based on roles and goals.

frontend_developer = Agent(
    role="Senior Frontend Developer",
    goal="Design and implement beautiful, responsive user interfaces",
    backstory=(
        "You are a frontend expert with deep knowledge of React, TypeScript, "
        "and modern CSS. You focus on user experience, accessibility, and "
        "performance. You write clean, maintainable component code."
    ),
    verbose=True,
    allow_delegation=False,
)

backend_developer = Agent(
    role="Senior Backend Developer",
    goal="Design robust, scalable APIs and backend systems",
    backstory=(
        "You are a backend specialist with expertise in Python, FastAPI, "
        "PostgreSQL, and microservices architecture. You prioritize "
        "security, performance, and clean API design."
    ),
    verbose=True,
    allow_delegation=False,
)

qa_engineer = Agent(
    role="QA Engineer",
    goal="Ensure software quality through comprehensive testing strategies",
    backstory=(
        "You are a quality assurance engineer who writes thorough test plans. "
        "You think about edge cases, security vulnerabilities, and performance "
        "bottlenecks. You ensure nothing ships without proper validation."
    ),
    verbose=True,
    allow_delegation=False,
)

tech_lead = Agent(
    role="Technical Lead",
    goal="Provide architectural guidance and ensure technical excellence",
    backstory=(
        "You are a senior technical lead with 15+ years of experience. "
        "You make architectural decisions, review code designs, and ensure "
        "the team follows best practices. You see the big picture."
    ),
    verbose=True,
    allow_delegation=True,  # The tech lead CAN delegate
)


# ═══════════════════════════════════════════════════════════════════
# 2. TASKS (order doesn't matter in hierarchical — manager decides)
# ═══════════════════════════════════════════════════════════════════
# NOTE: In hierarchical mode, you can assign agents to tasks, but
# the manager may override the assignment if it thinks another agent
# is better suited. You can also leave agent=None.

design_api_task = Task(
    description=(
        "Design a REST API for a task management application. "
        "Include endpoints for: CRUD operations on tasks, user authentication, "
        "task assignment, and status updates. "
        "Use OpenAPI/Swagger-style documentation format."
    ),
    expected_output=(
        "A complete API specification with:\n"
        "- At least 8 endpoints (method, path, request/response)\n"
        "- Authentication approach\n"
        "- Error handling strategy"
    ),
    agent=backend_developer,    # Suggested agent, manager may override
)

design_ui_task = Task(
    description=(
        "Design the component structure for a task management dashboard. "
        "Include: task list view, task detail modal, creation form, "
        "status filters, and user assignment dropdown. "
        "Describe the component hierarchy and key props."
    ),
    expected_output=(
        "A component architecture document with:\n"
        "- Component tree / hierarchy\n"
        "- Key props for each component\n"
        "- State management approach"
    ),
    agent=frontend_developer,
)

testing_strategy_task = Task(
    description=(
        "Create a comprehensive testing strategy for the task management app. "
        "Cover unit tests, integration tests, and end-to-end tests. "
        "Identify critical test scenarios and edge cases."
    ),
    expected_output=(
        "A test plan with:\n"
        "- Unit test cases (at least 10)\n"
        "- Integration test scenarios (at least 5)\n"
        "- E2E test flows (at least 3)\n"
        "- Edge cases and security tests"
    ),
    agent=qa_engineer,
)

architecture_review_task = Task(
    description=(
        "Review the API design, UI component architecture, and testing strategy. "
        "Identify potential issues, suggest improvements, and provide "
        "an overall architecture assessment. "
        "Ensure consistency across all three deliverables."
    ),
    expected_output=(
        "An architecture review document with:\n"
        "- Assessment of each deliverable\n"
        "- Identified issues or gaps\n"
        "- Improvement recommendations\n"
        "- Overall architecture verdict"
    ),
    agent=tech_lead,
    context=[design_api_task, design_ui_task, testing_strategy_task],
)


# ═══════════════════════════════════════════════════════════════════
# 3. HIERARCHICAL CREW
# ═══════════════════════════════════════════════════════════════════
# Process.hierarchical creates an internal "manager" agent that:
#   - Reads all tasks
#   - Decides execution order
#   - Delegates to the most appropriate agent
#   - Can ask agents to redo work
#   - Synthesizes the final output
#
# manager_llm: specify a powerful model for the manager
# (the manager needs good reasoning to coordinate effectively)

crew = Crew(
    agents=[frontend_developer, backend_developer, qa_engineer, tech_lead],
    tasks=[design_api_task, design_ui_task, testing_strategy_task, architecture_review_task],
    process=Process.hierarchical,       # ← Hierarchical mode!
    manager_llm="gpt-4o",              # ← Model for the auto-created manager
    verbose=True,
    # manager_agent=my_custom_manager,  # Alternative: provide your own manager agent
)


# ═══════════════════════════════════════════════════════════════════
# 4. RUN
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  HIERARCHICAL CREW — Software Architecture Team")
print("  Manager will coordinate: Backend, Frontend, QA, Tech Lead")
print("=" * 60)

result = crew.kickoff()

print("\n" + "=" * 60)
print("  FINAL ARCHITECTURE REVIEW")
print("=" * 60)
print(result)
