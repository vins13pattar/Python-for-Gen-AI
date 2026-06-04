"""
MCP Server Resources — Data resources exposed via MCP protocol.

Resources are read-only data endpoints that agents can access
to inspect the current research session state.

Resources:
- research://session/{session_id}    → Full session metadata
- research://context/{session_id}    → Retrieved context chunks
- research://embeddings/{session_id} → Embedding records
- research://messages/{session_id}   → Agent message log
"""

import logging
from app.state.state_store import state_store

logger = logging.getLogger(__name__)


def get_session_resource(session_id: str) -> dict:
    """
    MCP Resource: research://session/{session_id}

    Returns the current research session metadata.
    """
    state = state_store.get_state()

    if state["session_id"] != session_id:
        raise ValueError(f"Session not found: {session_id}")

    return {
        "resource_uri": f"research://session/{session_id}",
        "session_id": state["session_id"],
        "topic": state["topic"],
        "question_count": len(state["research_questions"]),
        "context_chunk_count": len(state["retrieved_context"]),
        "embedding_count": len(state["embeddings"]),
        "finding_count": len(state["findings"]),
        "message_count": len(state["agent_messages"]),
        "critique_status": state.get("critique_status", "pending"),
        "has_final_report": bool(state.get("final_report")),
    }


def get_context_resource(session_id: str) -> dict:
    """
    MCP Resource: research://context/{session_id}

    Returns all retrieved context chunks for the session.
    """
    state = state_store.get_state()

    if state["session_id"] != session_id:
        raise ValueError(f"Session not found: {session_id}")

    return {
        "resource_uri": f"research://context/{session_id}",
        "session_id": session_id,
        "chunk_count": len(state["retrieved_context"]),
        "chunks": state["retrieved_context"],
    }


def get_embeddings_resource(session_id: str) -> dict:
    """
    MCP Resource: research://embeddings/{session_id}

    Returns all embedding records for the session (without raw vectors for brevity).
    """
    state = state_store.get_state()

    if state["session_id"] != session_id:
        raise ValueError(f"Session not found: {session_id}")

    # Return embedding metadata without full vectors (for readability)
    embedding_summary = [
        {
            "chunk_id": e["chunk_id"],
            "embedding_id": e["embedding_id"],
            "text_preview": e.get("text", "")[:100],
            "embedding_dim": len(e.get("embedding", [])),
            "metadata": e.get("metadata", {}),
        }
        for e in state["embeddings"]
    ]

    return {
        "resource_uri": f"research://embeddings/{session_id}",
        "session_id": session_id,
        "embedding_count": len(embedding_summary),
        "embeddings": embedding_summary,
    }


def get_messages_resource(session_id: str) -> dict:
    """
    MCP Resource: research://messages/{session_id}

    Returns the full agent message log for the session.
    """
    state = state_store.get_state()

    if state["session_id"] != session_id:
        raise ValueError(f"Session not found: {session_id}")

    return {
        "resource_uri": f"research://messages/{session_id}",
        "session_id": session_id,
        "message_count": len(state["agent_messages"]),
        "messages": state["agent_messages"],
    }


def list_resources(session_id: str) -> list[dict]:
    """List all available MCP resources for a session."""
    return [
        {
            "uri": f"research://session/{session_id}",
            "name": "Research Session",
            "description": "Current research session metadata and status",
            "mimeType": "application/json",
        },
        {
            "uri": f"research://context/{session_id}",
            "name": "Retrieved Context",
            "description": "All context chunks retrieved by the Retriever Agent",
            "mimeType": "application/json",
        },
        {
            "uri": f"research://embeddings/{session_id}",
            "name": "Embeddings",
            "description": "Vector embedding records for semantic search",
            "mimeType": "application/json",
        },
        {
            "uri": f"research://messages/{session_id}",
            "name": "Agent Messages",
            "description": "All MCP-style agent-to-agent messages in this session",
            "mimeType": "application/json",
        },
    ]
