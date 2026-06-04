"""
Embedding Service — generates embeddings for text chunks.

Supports two modes:
1. Mock mode (USE_MOCK_EMBEDDINGS=true): returns random embeddings for demo
2. Real mode (USE_MOCK_EMBEDDINGS=false): uses OpenAI text-embedding API

Also provides cosine similarity search for analyst agent context retrieval.
"""

import logging
import math
import random
import uuid
from typing import Optional

from app.config import config

logger = logging.getLogger(__name__)

# Embedding dimension for mock mode
_MOCK_EMBEDDING_DIM = 384


def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _mock_embedding(text: str) -> list[float]:
    """
    Generate a deterministic-ish mock embedding vector.

    Uses text hash as a seed for reproducibility in demos.
    """
    seed = hash(text) % (2**31)
    rng = random.Random(seed)
    vec = [rng.gauss(0, 1) for _ in range(_MOCK_EMBEDDING_DIM)]
    # Normalize to unit vector
    norm = math.sqrt(sum(x * x for x in vec))
    return [x / norm for x in vec]


def _real_embedding(text: str) -> list[float]:
    """Get real embedding from OpenAI API."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        response = client.embeddings.create(
            model=config.EMBEDDING_MODEL,
            input=text,
        )
        return response.data[0].embedding
    except Exception as e:
        logger.warning(f"OpenAI embedding failed, falling back to mock: {e}")
        return _mock_embedding(text)


def get_embedding(text: str) -> list[float]:
    """
    Get an embedding vector for the given text.

    Uses mock or real embeddings based on config.USE_MOCK_EMBEDDINGS.
    """
    if config.USE_MOCK_EMBEDDINGS:
        logger.debug(f"Using mock embedding for text ({len(text)} chars)")
        return _mock_embedding(text)
    else:
        logger.debug(f"Using OpenAI embedding for text ({len(text)} chars)")
        return _real_embedding(text)


def create_embedding_record(
    chunk_id: str,
    text: str,
    metadata: Optional[dict] = None,
) -> dict:
    """
    Create a full embedding record for a context chunk.

    Returns:
        EmbeddingRecord dict with chunk_id, embedding_id, text, embedding, metadata.
    """
    embedding = get_embedding(text)
    return {
        "chunk_id": chunk_id,
        "embedding_id": f"emb_{uuid.uuid4().hex[:8]}",
        "text": text,
        "embedding": embedding,
        "metadata": metadata or {},
    }


def search_similar(
    query_text: str,
    embedding_records: list[dict],
    top_k: int = 3,
) -> list[dict]:
    """
    Find the most similar embedding records to a query text.

    Args:
        query_text: The query to embed and compare.
        embedding_records: List of EmbeddingRecord dicts with 'embedding' field.
        top_k: Number of top results to return.

    Returns:
        List of (record, similarity_score) tuples sorted by score descending.
    """
    if not embedding_records:
        return []

    query_embedding = get_embedding(query_text)

    scored: list[tuple[dict, float]] = []
    for record in embedding_records:
        if "embedding" not in record:
            continue
        score = _cosine_similarity(query_embedding, record["embedding"])
        scored.append((record, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    results = []
    for record, score in scored[:top_k]:
        result = dict(record)
        result["similarity_score"] = round(score, 4)
        results.append(result)

    return results
