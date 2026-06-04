"""
Embedding Agent — Vector Embedding Generation

Responsibilities:
- Reads retrieved context chunks from shared state
- Generates embedding vectors for each chunk
- Uses real OpenAI embeddings or mock embeddings based on config
- Sends a validated MCP-style 'embeddings_created' message
- Updates shared state with embeddings
"""

import logging
import uuid

from app.config import config
from app.state.research_state import ResearchState
from app.validation.message_validator import create_message
from app.embeddings.embedding_service import create_embedding_record

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# LangGraph node function
# ─────────────────────────────────────────────

def embedding_node(state: ResearchState) -> dict:
    """
    LangGraph node for the Embedding Agent.

    Reads: state['retrieved_context']
    Writes: state['embeddings'], state['agent_messages']
    """
    context_chunks = state["retrieved_context"]
    session_id = state["session_id"]

    logger.info(
        f"[Embedding Agent] Creating embeddings for {len(context_chunks)} chunks "
        f"({'mock' if config.USE_MOCK_EMBEDDINGS else 'OpenAI'})"
    )

    embedding_records = []

    for chunk in context_chunks:
        try:
            record = create_embedding_record(
                chunk_id=chunk["chunk_id"],
                text=chunk["text"],
                metadata={
                    "source": chunk.get("source", "unknown"),
                    "source_type": chunk.get("source_type", "unknown"),
                    "question": chunk.get("question", ""),
                },
            )
            embedding_records.append(record)

            if state.get("debug"):
                logger.debug(
                    f"  Embedded [{chunk['chunk_id']}]: "
                    f"dim={len(record['embedding'])}, "
                    f"id={record['embedding_id']}"
                )

        except Exception as e:
            logger.warning(
                f"[Embedding Agent] Failed to embed chunk {chunk['chunk_id']}: {e}"
            )
            # Add mock embedding as fallback
            from app.embeddings.embedding_service import _mock_embedding
            embedding_records.append({
                "chunk_id": chunk["chunk_id"],
                "embedding_id": f"emb_{uuid.uuid4().hex[:8]}",
                "text": chunk["text"],
                "embedding": _mock_embedding(chunk["text"]),
                "metadata": {"fallback": True},
            })

    logger.info(f"[Embedding Agent] ✓ Created {len(embedding_records)} embeddings")

    # Create MCP-style message
    message = create_message(
        message_id=f"msg_{uuid.uuid4().hex[:8]}",
        session_id=session_id,
        sender_agent="embedding_agent",
        receiver_agent="analyst_agent",
        message_type="embeddings_created",
        payload={
            "embedding_count": len(embedding_records),
            "embedding_records": [
                {
                    "chunk_id": r["chunk_id"],
                    "embedding_id": r["embedding_id"],
                }
                for r in embedding_records
            ],
        },
        metadata={
            "embedding_model": (
                config.EMBEDDING_MODEL if not config.USE_MOCK_EMBEDDINGS else "mock"
            ),
            "embedding_dim": (
                len(embedding_records[0]["embedding"])
                if embedding_records
                else 0
            ),
        },
    )

    return {
        "embeddings": embedding_records,
        "agent_messages": state["agent_messages"] + [message],
    }
