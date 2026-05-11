import random
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
import deepagents.middleware.subagents

# Monkey-patch to exclude non-serializable shell resources from subagent state
deepagents.middleware.subagents._EXCLUDED_STATE_KEYS.add("shell_session_resources")

from dotenv import load_dotenv
load_dotenv()

# Middleware imports
from langchain.agents.middleware import (
    SummarizationMiddleware,
    HumanInTheLoopMiddleware,
    ModelCallLimitMiddleware,
    ToolCallLimitMiddleware,
    ModelFallbackMiddleware,
    PIIMiddleware,
    TodoListMiddleware,
    LLMToolSelectorMiddleware,
    ToolRetryMiddleware,
    ModelRetryMiddleware,
    LLMToolEmulator,
    ContextEditingMiddleware,
    ClearToolUsesEdit,
    ShellToolMiddleware,
    FilesystemFileSearchMiddleware,
    HostExecutionPolicy,
)

from deepagents.middleware.filesystem import FilesystemMiddleware
from deepagents.middleware.subagents import SubAgentMiddleware
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

# -----------------------------
# 🧰 TOOLS
# -----------------------------

@tool
def search_docs(query: str) -> str:
    """Search for documents based on the query."""
    print("searching docs for: ", query, flush=True)
    return f"[DOC RESULT] Info about {query}"


@tool
def create_ticket(issue: str) -> str:
    """Create a ticket for the given issue."""
    print("Creating ticket for: ", issue, flush=True)
    if random.random() < 0.5:
        print("Temporary API failure", flush=True)
        raise Exception("Temporary API failure")
    print("Ticket created: ", issue, flush=True)
    return f"Ticket created: {issue}"


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to the specified recipient."""
    print("Sending email to: ", to, flush=True)
    return f"Email sent to {to}"


@tool
def get_weather(city: str) -> str:
    """Get the weather for the specified city."""
    print("Getting weather for: ", city, flush=True)
    return f"Weather in {city}: 30°C Sunny"


# -----------------------------
# 🧠 STATE + STORAGE
# -----------------------------

checkpointer = InMemorySaver()
store = InMemoryStore()

# -----------------------------
# 🤖 SUBAGENT
# -----------------------------

weather_subagent = {
    "name": "weather_agent",
    "description": "Handles weather queries",
    "system_prompt": "Use get_weather tool",
    "tools": [get_weather],
    "model": "gpt-4o-mini",
    "stream": False,
}

# -----------------------------
# 🚀 MAIN AGENT (PRODUCTION)
# -----------------------------

agent = create_agent(
    model="gpt-4o-mini",
    tools=[search_docs, create_ticket, send_email],
    system_prompt="You are a helpful assistant. Always be concise. Use weather_subagent to get weather report of a city.",
    checkpointer=checkpointer,
    store=store,

    middleware=[

        # -------------------------
        # 🧠 CONTEXT MANAGEMENT
        # -------------------------
        # SummarizationMiddleware(
        #     model="gpt-4o-mini",
        #     trigger=("messages", 6),
        #     keep=("messages", 3),
        # ),

        # ContextEditingMiddleware(
        #     edits=[
        #         ClearToolUsesEdit(trigger=2000, keep=2)
        #     ]
        # ),

        # -------------------------
        # 🔐 SECURITY
        # -------------------------
        PIIMiddleware("email", strategy="redact"),

        # -------------------------
        # 📋 PLANNING
        # -------------------------
        TodoListMiddleware(),

        # -------------------------
        # 🔁 RELIABILITY
        # -------------------------
        ToolRetryMiddleware(max_retries=3),
        ModelRetryMiddleware(max_retries=2),

        # -------------------------
        # 🔄 FALLBACK
        # -------------------------
        ModelFallbackMiddleware("gpt-4o-mini"),

        # -------------------------
        # 💸 LIMITS
        # -------------------------
        # ModelCallLimitMiddleware(run_limit=10, exit_behavior="end"),
        # ToolCallLimitMiddleware(run_limit=10),

        # -------------------------
        # 🖥️ SHELL TOOL
        # -------------------------
        ShellToolMiddleware(
            workspace_root="/tmp/workspace",
            execution_policy=HostExecutionPolicy(),
        ),

        # -------------------------
        # 📂 FILE SEARCH
        # -------------------------
        FilesystemFileSearchMiddleware(
            root_path="/tmp/workspace"
        ),

        # -------------------------
        # 🧠 FILESYSTEM MEMORY
        # -------------------------
        FilesystemMiddleware(
            backend=CompositeBackend(
                default=StateBackend(),
                routes={"/memories/": StoreBackend()}
            )
        ),

        # -------------------------
        # 🤖 SUBAGENTS
        # -------------------------
        SubAgentMiddleware(
            subagents=[weather_subagent],
            backend=StoreBackend()
        ),

        # -------------------------
        # 🧠 TOOL SELECTION
        # -------------------------
        # LLMToolSelectorMiddleware(
        #     model="gpt-4o-mini",
        #     max_tools=2,
        # ),
    ]
)

# -----------------------------
# ▶️ RUN DEMO
# -----------------------------

thread = {"configurable": {"thread_id": "demo"}}

response = agent.invoke({
        "messages": [
            HumanMessage(
                content="Create a ticket for issue login. Do search docs for the solution and send an email. What's the weather in San Francisco?"
            )
        ]
    },
    config=thread
    )
print("\n=== PRODUCTION AGENT ===\n")
print(response)

# response2 = agent.invoke(
#     {
#         "messages": [
#             HumanMessage(
#                 content="What's the weather in San Francisco?"
#             )
#         ]
#     },
#     config=thread
# )

# print("\n=== PRODUCTION AGENT ===\n")
# print(response2)