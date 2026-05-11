from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
import operator, json
from dotenv import load_dotenv
load_dotenv()

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

tools = [search, calculator]
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

app = builder.compile()

# ── Run ────────────────────────────────────────────────────────────
result = app.invoke({
    "messages": [HumanMessage("Who created Python and what is 15 * 7?")]
})

for msg in result["messages"]:
    print(f"[{type(msg).__name__}]: {msg.content[:120]}")