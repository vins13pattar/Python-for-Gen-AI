"""
Retriever Agent — Context Retrieval

Responsibilities:
- Reads research questions from shared state
- Searches local knowledge base (markdown files) for relevant context
- Falls back to mock context if no local files match
- Sends a validated MCP-style 'context_retrieved' message
- Updates shared state with retrieved_context
"""

import logging
import uuid
import glob
from pathlib import Path

from app.config import config
from app.state.research_state import ResearchState
from app.validation.message_validator import create_message

logger = logging.getLogger(__name__)

# Keywords in knowledge docs we can match against topics
_KNOWLEDGE_FILES = {
    "mcp_overview.md": [
        "mcp", "model context protocol", "context protocol", "tools", "resources",
        "protocol", "server", "agent communication", "shared context",
    ],
    "ai_agents_overview.md": [
        "ai agent", "agent", "software development", "development workflow",
        "automation", "testing", "code", "devops", "generative ai",
    ],
}


def _load_knowledge_file(filename: str) -> str:
    """Load content from a knowledge base file."""
    path = config.KNOWLEDGE_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i : i + chunk_size]
        chunks.append(" ".join(chunk_words))
        i += chunk_size - overlap
    return chunks


def _find_relevant_files(topic: str, questions: list[dict]) -> list[str]:
    """Find knowledge files relevant to the topic and questions."""
    combined_text = f"{topic} " + " ".join(
        q["question"].lower() for q in questions
    )
    combined_text = combined_text.lower()

    relevant_files = []
    for filename, keywords in _KNOWLEDGE_FILES.items():
        if any(kw in combined_text for kw in keywords):
            relevant_files.append(filename)

    # Always include at least one file
    if not relevant_files:
        relevant_files = list(_KNOWLEDGE_FILES.keys())

    return relevant_files


def _retrieve_local_context(
    questions: list[dict], topic: str
) -> list[dict]:
    """Retrieve context from local markdown knowledge base."""
    relevant_files = _find_relevant_files(topic, questions)
    chunks: list[dict] = []
    chunk_idx = 0

    for filename in relevant_files:
        content = _load_knowledge_file(filename)
        if not content:
            logger.warning(f"Knowledge file not found or empty: {filename}")
            continue

        text_chunks = _chunk_text(content, chunk_size=100, overlap=10)

        for question_item in questions:
            q_text = question_item["question"].lower()
            # Pick the most relevant chunks (simple keyword match)
            for chunk_text in text_chunks[:3]:  # Take first 3 chunks per file
                chunk_idx += 1
                chunks.append({
                    "chunk_id": f"chunk_{chunk_idx:03d}",
                    "text": chunk_text,
                    "question": question_item["question"],
                    "source": filename,
                    "source_type": "local_markdown",
                })
            break  # One file per question for demo clarity

    return chunks


def _mock_context(questions: list[dict]) -> list[dict]:
    """Generate mock context chunks for each research question."""
    mock_data = {
        "default": [
            "AI agents are autonomous systems that perceive their environment and take actions to achieve goals. They can call tools, access APIs, and collaborate with other agents.",
            "The Model Context Protocol (MCP) provides a standard way for AI applications to connect with external tools and data sources through a unified interface.",
            "Multi-agent systems enable complex tasks to be broken into specialized subtasks, with each agent focusing on its area of expertise.",
            "Shared context stores allow multiple agents to read and write to a common knowledge base, enabling collaboration without direct communication.",
            "LangGraph provides a stateful workflow engine that manages the flow of information between AI agents using a directed graph structure.",
            "CrewAI enables role-based agent definition, where each agent has a specific role, goal, and backstory that shapes its behavior.",
        ]
    }

    chunks = []
    for i, question_item in enumerate(questions):
        question = question_item["question"]
        # Assign context chunks to each question
        ctx_texts = mock_data["default"]
        # Pick two chunks per question (cycling through available texts)
        for j in range(2):
            idx = (i * 2 + j) % len(ctx_texts)
            chunks.append({
                "chunk_id": f"chunk_{i * 2 + j + 1:03d}",
                "text": ctx_texts[idx],
                "question": question,
                "source": "mock_knowledge_base",
                "source_type": "mock",
            })

    return chunks


# ─────────────────────────────────────────────
# LangGraph node function
# ─────────────────────────────────────────────

def retriever_node(state: ResearchState) -> dict:
    """
    LangGraph node for the Retriever Agent.

    Reads: state['research_questions'], state['topic']
    Writes: state['retrieved_context'], state['agent_messages']
    """
    questions = state["research_questions"]
    topic = state["topic"]
    session_id = state["session_id"]

    logger.info(f"[Retriever Agent] Retrieving context for {len(questions)} questions")

    # Try local knowledge base first, fall back to mock
    context_chunks = _retrieve_local_context(questions, topic)

    if not context_chunks:
        logger.info("[Retriever Agent] No local context found, using mock context")
        context_chunks = _mock_context(questions)
    else:
        logger.info(f"[Retriever Agent] Found {len(context_chunks)} chunks from local knowledge base")

    if state.get("debug"):
        for chunk in context_chunks[:3]:
            logger.debug(
                f"  Chunk [{chunk['chunk_id']}] from '{chunk['source']}': "
                f"{chunk['text'][:80]}..."
            )

    # Create MCP-style message
    message = create_message(
        message_id=f"msg_{uuid.uuid4().hex[:8]}",
        session_id=session_id,
        sender_agent="retriever_agent",
        receiver_agent="embedding_agent",
        message_type="context_retrieved",
        payload={
            "chunk_count": len(context_chunks),
            "chunks": [
                {
                    "chunk_id": c["chunk_id"],
                    "source": c["source"],
                    "source_type": c["source_type"],
                }
                for c in context_chunks
            ],
        },
        metadata={
            "source_count": len(set(c["source"] for c in context_chunks)),
            "retry_count": state.get("critic_retry_count", 0),
        },
    )

    logger.info(
        f"[Retriever Agent] ✓ Retrieved {len(context_chunks)} context chunks"
    )

    return {
        "retrieved_context": context_chunks,
        "agent_messages": state["agent_messages"] + [message],
    }
