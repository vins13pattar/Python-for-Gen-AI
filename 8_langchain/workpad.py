from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
import operator, json
from langgraph.checkpoint.memory import MemorySaver
# from langgraph.checkpoint.sqlite import SQLiteSaver
from dotenv import load_dotenv
load_dotenv()

# ── Memory ──────────────────────────────────────────────────────────
# Use memory saver for in-memory checkpointing for dev/test environment
checkpointer = MemorySaver()

# Use SQLite saver for persistent checkpointing for production environment
# checkpointer = SQLiteSaver(sqlite_uri="sqlite:///checkpoints.db")

# ── Conversation history ──────────────────────────────────────────────────────────

config = {"configurable": {"thread_id": "user-1234"}}

# ── Tools ──────────────────────────────────────────────────────────
@tool
def search(query: str) -> str:
    """Search the web for information."""
    # In real code, call an actual search API
    return f"Search results for '{query}': Python was created by Guido van Rossum in 1991."

@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to a specified recipient with a subject and body."""
    # pause and ask the human before proceeding
    human_input = interrupt({
        "question": "Are you sure you want to proceed sending email?",
    })

    print(human_input)

    if human_input["approved"]:
        # proceed with the sending email
        print(f"Sending email to {to} with subject '{subject}'...")
        print(f"Body: {body}")
        return f"Email sent successfully to {to}"
    else:
        return {"status": "declined"}

tools = [search, calculator, send_email]
tools_by_name = {t.name: t for t in tools}

# ── State ──────────────────────────────────────────────────────────
class State(TypedDict):
    messages: Annotated[list, operator.add]

# ── Nodes ──────────────────────────────────────────────────────────
llm = ChatOpenAI(model="gpt-4o").bind_tools(tools)   # attach tools to LLM

def agent_node(state: State) -> dict:
    """Call the LLM with the current message history."""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def tool_node(state: State) -> dict:
    """Execute any tool calls the agent requested."""
    last_msg = state["messages"][-1]
    results = []
    for tc in last_msg.tool_calls:
        tool_fn = tools_by_name[tc["name"]]
        output = tool_fn.invoke(tc["args"])
        results.append(
            ToolMessage(
                content=str(output),
                tool_call_id=tc["id"]
            )
        )
    return {"messages": results}

# ── Routing ────────────────────────────────────────────────────────
def route(state: State) -> str:
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tools"
    return END   # no tool calls → we're done


# ── Graph ──────────────────────────────────────────────────────────
builder = StateGraph(State)
builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node)

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", route)
builder.add_edge("tools", "agent")   # always loop back

app = builder.compile(checkpointer=checkpointer)

# ── Run ────────────────────────────────────────────────────────────
result = app.invoke(
    {
        "messages": [HumanMessage("Please send an email to vinay.kumar@oracle.com with subject 'Test' and body 'Test email'")],
    },
    config=config
)

for msg in result["messages"]:
    print(f"[{type(msg).__name__}]: {msg.content[:120]}")

#--- Snapshot --------------
snapshot = app.get_state(config)
print("Snapshot:", snapshot)
print("Next node:", snapshot.next)
print("Values", snapshot.values["messages"])


#--- List all checkpoints ---------
for s in app.get_state_history(config):
    print("Config: ",s.config)
    print("Created At: ", s.created_at)
    print("Next Node: ", s.next)
    print("Values: ", s.values)
    print("\n")