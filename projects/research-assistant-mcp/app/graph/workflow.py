"""
LangGraph Workflow — Stateful Research Assistant Pipeline

Defines the StateGraph connecting all agent nodes with:
- Sequential execution: Planner → Retriever → Embedding → Analyst → Critic
- Conditional routing: Critic → Writer (approved) OR Critic → Retriever (retry)
- Shared ResearchState passed through every node

Graph Structure:
    START
      ↓
    Planner
      ↓
    Retriever
      ↓
    Embedding
      ↓
    Analyst
      ↓
    Critic
      ↓ (conditional)
      ├── needs_improvement → Retriever (retry loop)
      └── approved → Writer → END
"""

import logging
from langgraph.graph import StateGraph, END, START

from app.state.research_state import ResearchState
from app.graph.nodes import (
    planner_node,
    retriever_node,
    embedding_node,
    analyst_node,
    critic_node,
    writer_node,
    route_after_critic,
)

logger = logging.getLogger(__name__)

# Node name constants
NODE_PLANNER = "planner"
NODE_RETRIEVER = "retriever"
NODE_EMBEDDING = "embedding"
NODE_ANALYST = "analyst"
NODE_CRITIC = "critic"
NODE_WRITER = "writer"


def build_workflow():
    """
    Build and compile the LangGraph StateGraph.

    Returns:
        A compiled LangGraph runnable (CompiledGraph).
    """
    logger.info("Building LangGraph research workflow...")

    # Initialize the state graph with our ResearchState schema
    graph = StateGraph(ResearchState)

    # ── Add Nodes ────────────────────────────────────────────────────────────
    graph.add_node(NODE_PLANNER, planner_node)
    graph.add_node(NODE_RETRIEVER, retriever_node)
    graph.add_node(NODE_EMBEDDING, embedding_node)
    graph.add_node(NODE_ANALYST, analyst_node)
    graph.add_node(NODE_CRITIC, critic_node)
    graph.add_node(NODE_WRITER, writer_node)

    # ── Add Sequential Edges ─────────────────────────────────────────────────
    graph.add_edge(START, NODE_PLANNER)
    graph.add_edge(NODE_PLANNER, NODE_RETRIEVER)
    graph.add_edge(NODE_RETRIEVER, NODE_EMBEDDING)
    graph.add_edge(NODE_EMBEDDING, NODE_ANALYST)
    graph.add_edge(NODE_ANALYST, NODE_CRITIC)

    # ── Add Conditional Edge (Critic Decision) ────────────────────────────────
    graph.add_conditional_edges(
        NODE_CRITIC,
        route_after_critic,
        {
            "retry": NODE_RETRIEVER,   # Loop back for more context
            "write": NODE_WRITER,      # Proceed to final report
        },
    )

    # ── Writer → END ──────────────────────────────────────────────────────────
    graph.add_edge(NODE_WRITER, END)

    # Compile the graph
    compiled = graph.compile()
    logger.info("✓ LangGraph workflow compiled successfully")
    logger.info(
        f"  Nodes: {[NODE_PLANNER, NODE_RETRIEVER, NODE_EMBEDDING, NODE_ANALYST, NODE_CRITIC, NODE_WRITER]}"
    )
    logger.info(f"  Conditional routing: critic → {{retry: retriever, write: writer}}")

    return compiled


def get_workflow():
    """Return a cached compiled workflow (build once per process)."""
    global _compiled_workflow
    if _compiled_workflow is None:
        _compiled_workflow = build_workflow()
    return _compiled_workflow


_compiled_workflow = None
