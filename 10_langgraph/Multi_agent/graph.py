# graph.py
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from state import MultiAgentState
from agents.supervisor import supervisor_node
from agents.researcher import researcher_node
from agents.writer import writer_node
from agents.reviewer import reviewer_node


# ── Routing function ───────────────────────────────────────────────

def route_from_supervisor(state: MultiAgentState) -> str:
    """
    Called after supervisor_node runs.
    Maps the supervisor's decision to the next node name.
    """
    next_agent = state.get("next_agent", "DONE")

    routing_map = {
        "researcher": "researcher",
        "writer":     "writer",
        "reviewer":   "reviewer",
        "DONE":       END,
    }

    destination = routing_map.get(next_agent, END)
    print(f"[router] supervisor said '{next_agent}' → going to '{destination}'")
    return destination


# ── Build the graph ────────────────────────────────────────────────

def build_graph():
    builder = StateGraph(MultiAgentState)

    # Register all nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("researcher", researcher_node)
    builder.add_node("writer",     writer_node)
    builder.add_node("reviewer",   reviewer_node)

    # Entry point: always start at supervisor
    builder.add_edge(START, "supervisor")

    # Supervisor decides who goes next (conditional)
    builder.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "researcher": "researcher",
            "writer":     "writer",
            "reviewer":   "reviewer",
            END:          END,
        },
    )

    # After each specialist finishes, always return to supervisor
    builder.add_edge("researcher", "supervisor")
    builder.add_edge("writer",     "supervisor")
    builder.add_edge("reviewer",   "supervisor")

    return builder.compile(checkpointer=MemorySaver())


# ── Visualise the graph (optional) ────────────────────────────────

def print_graph_structure(app):
    """Print a text representation of the compiled graph."""
    print("\nGraph nodes:", list(app.get_graph().nodes.keys()))
    print("Graph edges:")
    for edge in app.get_graph().edges:
        print(f"  {edge.source} → {edge.target}")