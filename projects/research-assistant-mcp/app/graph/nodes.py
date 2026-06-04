"""
LangGraph Nodes — wraps each agent function as a LangGraph-compatible node.

Each node function:
1. Receives the current ResearchState
2. Calls the corresponding agent function
3. Returns a state update dict
4. Also logs the message to the StateStore

This module is the bridge between LangGraph's state management and the agent logic.
"""

import logging

from app.state.research_state import ResearchState
from app.state.state_store import state_store
from app.agents.planner_agent import planner_node as _planner
from app.agents.retriever_agent import retriever_node as _retriever
from app.agents.embedding_agent import embedding_node as _embedder
from app.agents.analyst_agent import analyst_node as _analyst
from app.agents.critic_agent import critic_node as _critic, should_retry
from app.agents.writer_agent import writer_node as _writer

logger = logging.getLogger(__name__)


def planner_node(state: ResearchState) -> dict:
    """LangGraph node: Research Planner Agent."""
    logger.info("═══ NODE: Planner Agent ═══")
    result = _planner(state)
    # Log new messages to state store
    new_messages = result.get("agent_messages", [])
    if new_messages:
        state_store.log_message(new_messages[-1])
    return result


def retriever_node(state: ResearchState) -> dict:
    """LangGraph node: Context Retriever Agent."""
    logger.info("═══ NODE: Retriever Agent ═══")
    result = _retriever(state)
    new_messages = result.get("agent_messages", [])
    if new_messages:
        state_store.log_message(new_messages[-1])
    return result


def embedding_node(state: ResearchState) -> dict:
    """LangGraph node: Embedding Agent."""
    logger.info("═══ NODE: Embedding Agent ═══")
    result = _embedder(state)
    new_messages = result.get("agent_messages", [])
    if new_messages:
        state_store.log_message(new_messages[-1])
    return result


def analyst_node(state: ResearchState) -> dict:
    """LangGraph node: Analyst Agent."""
    logger.info("═══ NODE: Analyst Agent ═══")
    result = _analyst(state)
    new_messages = result.get("agent_messages", [])
    if new_messages:
        state_store.log_message(new_messages[-1])
    return result


def critic_node(state: ResearchState) -> dict:
    """LangGraph node: Critic Agent."""
    logger.info("═══ NODE: Critic Agent ═══")
    result = _critic(state)
    new_messages = result.get("agent_messages", [])
    if new_messages:
        state_store.log_message(new_messages[-1])
    return result


def writer_node(state: ResearchState) -> dict:
    """LangGraph node: Writer Agent."""
    logger.info("═══ NODE: Writer Agent ═══")
    result = _writer(state)
    new_messages = result.get("agent_messages", [])
    if new_messages:
        state_store.log_message(new_messages[-1])
    return result


def route_after_critic(state: ResearchState) -> str:
    """
    Conditional routing function after the Critic Agent.

    Returns:
        "retry"  → route back to Retriever Agent
        "write"  → proceed to Writer Agent
    """
    return should_retry(state)
