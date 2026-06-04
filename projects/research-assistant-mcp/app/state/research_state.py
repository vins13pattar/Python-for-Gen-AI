"""
Shared Research State definition using TypedDict.

This is the central data structure passed between all LangGraph nodes.
Every agent reads from and writes to this state.
"""

from typing import TypedDict, Annotated
import operator


class ResearchQuestion(TypedDict):
    """A single research question with priority."""
    question: str
    priority: str  # "high", "medium", "low"


class ContextChunk(TypedDict):
    """A retrieved context chunk."""
    chunk_id: str
    text: str
    question: str
    source: str
    source_type: str  # "local_markdown", "mock", "web"


class EmbeddingRecord(TypedDict):
    """An embedding vector record for a context chunk."""
    chunk_id: str
    embedding_id: str
    text: str
    embedding: list[float]
    metadata: dict


class Finding(TypedDict):
    """A research finding extracted by the Analyst Agent."""
    finding_id: str
    question: str
    insight: str
    confidence: str  # "high", "medium", "low"
    supporting_chunks: list[str]  # chunk_ids


class AgentMessage(TypedDict):
    """An MCP-style agent-to-agent message."""
    message_id: str
    session_id: str
    sender_agent: str
    receiver_agent: str
    message_type: str
    timestamp: str
    payload: dict
    metadata: dict


class ResearchState(TypedDict):
    """
    The shared state object passed between all LangGraph nodes.

    All agents read from and write to this state.
    LangGraph handles merging using list concatenation for list fields.
    """

    # Session metadata
    session_id: str
    topic: str

    # Research planning
    research_questions: list[ResearchQuestion]

    # Context retrieval
    retrieved_context: list[ContextChunk]

    # Embeddings
    embeddings: list[EmbeddingRecord]

    # Analysis
    findings: list[Finding]

    # Critique
    critique: list[str]
    critique_status: str  # "approved" | "needs_improvement"
    critic_retry_count: int

    # Agent communication log
    agent_messages: list[AgentMessage]

    # Final output
    final_report: str

    # Debug flag
    debug: bool
