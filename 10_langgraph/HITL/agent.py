import json
import operator
from typing import TypedDict, Annotated

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from tools import all_tools, tools_by_name

from dotenv import load_dotenv
load_dotenv()


# ── 1. State ───────────────────────────────────────────────────────
class EmailAgentState(TypedDict):
    messages:        Annotated[list, operator.add]
    pending_email:   dict | None      # draft waiting for approval
    human_approved:  bool | None      # True / False / None (not decided yet)
    edit_request:    str              # human's edit instructions (optional)
    outcome:         str              # final summary


# ── 2. LLM ────────────────────────────────────────────────────────
llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
llm_with_tools = llm.bind_tools(all_tools)


# ── 3. Nodes ───────────────────────────────────────────────────────

def agent_node(state: EmailAgentState) -> dict:
    """
    Agent decides what to do next.
    On first run: composes the email.
    After an edit request: rewrites based on feedback.
    """
    print("\n[agent] Thinking...")

    # If a previous draft was rejected with edit notes, inject them
    messages = list(state["messages"])
    if state.get("edit_request") and state.get("pending_email"):
        messages.append(
            HumanMessage(
                f"Please rewrite the email with these changes: "
                f"{state['edit_request']}\n\n"
                f"Previous draft:\n{json.dumps(state['pending_email'], indent=2)}"
            )
        )
    # Inject a system message to guide the LLM
    system_msg = SystemMessage(
        content="You are an email assistant. First, use compose_email to draft the email. "
                "Then, you MUST immediately call send_email with the drafted content. "
                "The system will automatically pause and ask for human review before actually sending."
    )
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages.insert(0, system_msg)

    response = llm_with_tools.invoke(messages)
    return {"messages": [response], "edit_request": ""}


def tool_executor_node(state: EmailAgentState) -> dict:
    """
    Runs safe tools immediately (compose_email).
    Intercepts send_email — captures the payload but does NOT send.
    The graph will be interrupted before human_review if send is pending.
    """
    last_msg = state["messages"][-1]
    tool_results = []
    pending = None

    for tc in last_msg.tool_calls:
        name = tc["name"]
        args = tc["args"]

        if name == "send_email":
            # Don't send yet — capture and pause
            pending = args
            tool_results.append(
                ToolMessage(
                    content=(
                        "[PENDING HUMAN APPROVAL] "
                        f"send_email called with: {json.dumps(args)}"
                    ),
                    tool_call_id=tc["id"],
                )
            )
            print(f"[tools] send_email intercepted — awaiting approval.")

        else:
            print(f"[tools] Running {name}...")
            output = tools_by_name[name].invoke(args)
            tool_results.append(
                ToolMessage(content=str(output), tool_call_id=tc["id"])
            )

            # If compose_email was called, extract the draft for state
            if name == "compose_email":
                try:
                    parsed = json.loads(output)
                    pending_draft = parsed.get("draft")
                    print(f"[tools] Draft composed for: {pending_draft.get('to')}")
                except Exception:
                    pending_draft = None

                return {
                    "messages": tool_results,
                    "pending_email": pending_draft,
                }

    return {
        "messages": tool_results,
        **({"pending_email": pending} if pending else {}),
    }


def human_review_node(state: EmailAgentState) -> dict:
    """
    Reached only after update_state() injects human_approved.

    - True  → call send_email for real
    - False + edit_request → loop back to agent to rewrite
    - False (no edits)     → cancel
    """
    approved = state.get("human_approved")
    draft    = state.get("pending_email", {})
    edits    = state.get("edit_request", "")

    if approved is True:
        print("\n[human_review] Approved — sending email...")
        result = tools_by_name["send_email"].invoke({
            "to":      draft["to"],
            "subject": draft["subject"],
            "body":    draft["body"],
        })
        return {
            "outcome":  result,
            "messages": [SystemMessage(content=result)],
            # Clear pending state
            "pending_email":  None,
            "human_approved": None,
        }

    elif approved is False and edits:
        print(f"\n[human_review] Edit requested: {edits}")
        # Signal the router to go back to agent for rewriting
        return {
            "outcome":        "",
            "human_approved": None,   # reset so next cycle works
            "edit_request":   edits,
        }

    else:
        msg = "❌ Email cancelled by user. Nothing was sent."
        print(f"\n[human_review] {msg}")
        return {
            "outcome":        msg,
            "messages":       [SystemMessage(content=msg)],
            "pending_email":  None,
            "human_approved": None,
        }


def summarise_node(state: EmailAgentState) -> dict:
    """Wraps up with a brief summary."""
    print("\n[summarise] Generating summary...")
    summary = llm.invoke(
        state["messages"]
        + [HumanMessage("Summarise what happened in one short sentence. Explicitly state whether the email was actually sent or if it was cancelled by the user.")]
    )
    return {"messages": [summary]}


# ── 4. Routing ─────────────────────────────────────────────────────

def route_after_agent(state: EmailAgentState) -> str:
    last = state["messages"][-1]
    if getattr(last, "tool_calls", None):
        return "tools"
    return "summarise"


def route_after_tools(state: EmailAgentState) -> str:
    last = state["messages"][-1]
    # send_email was intercepted → go to approval gate
    if isinstance(last, ToolMessage) and "PENDING HUMAN APPROVAL" in last.content:
        return "human_review"
    # More tool calls needed → loop
    if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
        return "agent"
    # compose_email done, now agent should decide to send
    return "agent"


def route_after_review(state: EmailAgentState) -> str:
    # Edit was requested → rewrite loop
    if state.get("edit_request"):
        return "agent"
    # Done (sent or cancelled)
    return "summarise"


# ── 5. Build ───────────────────────────────────────────────────────

def build_graph():
    builder = StateGraph(EmailAgentState)

    builder.add_node("agent",         agent_node)
    builder.add_node("tools",         tool_executor_node)
    builder.add_node("human_review",  human_review_node)
    builder.add_node("summarise",     summarise_node)

    builder.add_edge(START, "agent")

    builder.add_conditional_edges("agent",        route_after_agent,  {"tools": "tools", "summarise": "summarise"})
    builder.add_conditional_edges("tools",        route_after_tools,  {"human_review": "human_review", "agent": "agent"})
    builder.add_conditional_edges("human_review", route_after_review, {"agent": "agent", "summarise": "summarise"})

    builder.add_edge("summarise", END)

    return builder.compile(
        checkpointer=MemorySaver(),
        interrupt_before=["human_review"],   # ← HITL pause point
    )