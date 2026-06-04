"""
MCP Server Tools — Callable tools exposed via MCP protocol.

These tools provide the shared context layer that all agents use
to read and write research state. They implement the MCP tool
interface using fastmcp.

Tools:
- save_context      → store a retrieved context chunk
- get_context       → retrieve context for a session
- save_embedding    → store an embedding record
- search_context    → semantic search over context
- log_agent_message → log an agent-to-agent message
"""

import logging
from app.state.state_store import state_store
from app.validation.message_validator import validate_message, validate_tool_input
from app.embeddings.embedding_service import search_similar

logger = logging.getLogger(__name__)


def save_context(session_id: str, chunk: dict) -> dict:
    """
    MCP Tool: Save a retrieved context chunk to shared state.

    Args:
        session_id: The research session ID.
        chunk: A context chunk dict with chunk_id, text, source, etc.

    Returns:
        Success response dict.
    """
    validate_tool_input("save_context", {"session_id": session_id, "chunk": chunk})

    state = state_store.get_state()
    if state["session_id"] != session_id:
        raise ValueError(f"Session mismatch: {session_id} != {state['session_id']}")

    state["retrieved_context"].append(chunk)
    logger.debug(f"[MCP Tool] save_context: stored chunk {chunk.get('chunk_id')}")

    return {
        "success": True,
        "chunk_id": chunk.get("chunk_id"),
        "session_id": session_id,
    }


def get_context(session_id: str, question: str | None = None) -> dict:
    """
    MCP Tool: Retrieve context chunks from shared state.

    Args:
        session_id: The research session ID.
        question: Optional filter — return only chunks for this question.

    Returns:
        Dict with list of matching context chunks.
    """
    validate_tool_input("get_context", {"session_id": session_id})

    state = state_store.get_state()
    if state["session_id"] != session_id:
        raise ValueError(f"Session mismatch: {session_id}")

    chunks = state["retrieved_context"]
    if question:
        chunks = [c for c in chunks if c.get("question") == question]

    logger.debug(f"[MCP Tool] get_context: returning {len(chunks)} chunks")
    return {
        "session_id": session_id,
        "chunk_count": len(chunks),
        "chunks": chunks,
    }


def save_embedding(session_id: str, embedding_record: dict) -> dict:
    """
    MCP Tool: Store an embedding record to shared state.

    Args:
        session_id: The research session ID.
        embedding_record: An EmbeddingRecord dict.

    Returns:
        Success response dict.
    """
    validate_tool_input(
        "save_embedding",
        {"session_id": session_id, "embedding_record": embedding_record},
    )

    state = state_store.get_state()
    state["embeddings"].append(embedding_record)
    logger.debug(
        f"[MCP Tool] save_embedding: stored {embedding_record.get('embedding_id')}"
    )

    return {
        "success": True,
        "embedding_id": embedding_record.get("embedding_id"),
        "chunk_id": embedding_record.get("chunk_id"),
    }


def search_context(session_id: str, query: str, top_k: int = 3) -> dict:
    """
    MCP Tool: Semantic search over stored embeddings.

    Args:
        session_id: The research session ID.
        query: The search query text.
        top_k: Number of top results to return (default 3).

    Returns:
        Dict with list of matching context chunks ranked by similarity.
    """
    validate_tool_input(
        "search_context",
        {"session_id": session_id, "query": query, "top_k": top_k},
    )

    state = state_store.get_state()
    embeddings = state["embeddings"]

    if not embeddings:
        logger.warning("[MCP Tool] search_context: no embeddings available yet")
        return {"session_id": session_id, "query": query, "results": []}

    similar = search_similar(query, embeddings, top_k=top_k)
    logger.debug(f"[MCP Tool] search_context: found {len(similar)} results for '{query[:30]}...'")

    return {
        "session_id": session_id,
        "query": query,
        "result_count": len(similar),
        "results": similar,
    }


def log_agent_message(session_id: str, message: dict) -> dict:
    """
    MCP Tool: Log a validated agent message to shared state.

    Args:
        session_id: The research session ID.
        message: An MCP-style agent message dict.

    Returns:
        Success response dict.
    """
    validate_tool_input(
        "log_agent_message",
        {"session_id": session_id, "message": message},
    )

    # Validate the message against MCP schema
    validate_message(message)

    state_store.log_message(message)
    logger.debug(
        f"[MCP Tool] log_agent_message: [{message.get('sender_agent')} → "
        f"{message.get('receiver_agent')}] {message.get('message_type')}"
    )

    return {
        "success": True,
        "message_id": message.get("message_id"),
        "logged": True,
    }
