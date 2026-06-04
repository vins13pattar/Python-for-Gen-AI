"""
Analyst Agent — Research Insight Extraction

Responsibilities:
- Reads research questions and retrieved context from shared state
- Uses semantic search over embeddings to find the most relevant chunks per question
- Extracts structured findings (insight, confidence, supporting chunks)
- Uses real LLM or mock analysis based on config
- Sends a validated MCP-style 'findings_created' message
- Updates shared state with findings
"""

import logging
import uuid

from app.config import config
from app.state.research_state import ResearchState
from app.validation.message_validator import create_message
from app.embeddings.embedding_service import search_similar

logger = logging.getLogger(__name__)


def _mock_finding(question: str, supporting_chunks: list[str]) -> dict:
    """Generate a mock finding for demo purposes."""
    # Simple keyword-based insight generation
    q_lower = question.lower()

    if "what is" in q_lower or "what are" in q_lower:
        insight = (
            f"Based on the retrieved context, this topic encompasses multiple "
            f"interconnected concepts. The definition involves understanding both "
            f"the technical foundations and practical applications. Key terms and "
            f"frameworks have been identified that define the scope."
        )
        confidence = "high"

    elif "benefit" in q_lower or "application" in q_lower:
        insight = (
            f"The primary benefits identified include improved efficiency, reduced "
            f"manual effort, better collaboration between components, and greater "
            f"scalability. Real-world applications span multiple domains including "
            f"software development, research, and enterprise automation."
        )
        confidence = "high"

    elif "risk" in q_lower or "challenge" in q_lower or "limitation" in q_lower:
        insight = (
            f"Key challenges include technical complexity, integration overhead, "
            f"potential for errors in automated outputs, and the need for human "
            f"oversight. Organizations must balance automation benefits against "
            f"reliability requirements."
        )
        confidence = "medium"

    elif "future" in q_lower or "trend" in q_lower or "outlook" in q_lower:
        insight = (
            f"The trajectory points toward greater autonomy, improved context "
            f"understanding, and tighter integration with development workflows. "
            f"Emerging patterns suggest multi-agent systems will become standard "
            f"infrastructure for complex AI applications."
        )
        confidence = "medium"

    elif "compare" in q_lower or "alternative" in q_lower:
        insight = (
            f"Compared to alternatives, the approach under study offers superior "
            f"standardization and interoperability. Existing solutions often lack "
            f"the structured communication layer that this approach provides, "
            f"resulting in tighter coupling between components."
        )
        confidence = "medium"

    else:
        insight = (
            f"Analysis of the retrieved context reveals several important patterns. "
            f"The evidence suggests a clear relationship between the components "
            f"described, with practical implications for implementation. Further "
            f"investigation of the supporting materials confirms the core thesis."
        )
        confidence = "low"

    return {
        "finding_id": f"finding_{uuid.uuid4().hex[:6]}",
        "question": question,
        "insight": insight,
        "confidence": confidence,
        "supporting_chunks": supporting_chunks,
    }


def _llm_finding(
    question: str,
    context_texts: list[str],
    supporting_chunks: list[str],
) -> dict:
    """Generate a finding using OpenAI LLM."""
    try:
        from openai import OpenAI
        import json as _json

        client = OpenAI(api_key=config.OPENAI_API_KEY)

        context_block = "\n\n".join(
            f"[Context {i+1}]: {text}" for i, text in enumerate(context_texts[:4])
        )

        prompt = f"""You are a research analyst. Given the following research question and context, extract a key insight.

Research Question: {question}

Context:
{context_block}

Provide a JSON response with:
- "insight": A clear, 2-3 sentence insight that directly answers the question
- "confidence": "high", "medium", or "low" based on context quality

Return only valid JSON."""

        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        parsed = _json.loads(response.choices[0].message.content)

        return {
            "finding_id": f"finding_{uuid.uuid4().hex[:6]}",
            "question": question,
            "insight": parsed.get("insight", "Insight extraction failed."),
            "confidence": parsed.get("confidence", "low"),
            "supporting_chunks": supporting_chunks,
        }

    except Exception as e:
        logger.warning(f"LLM analyst failed for question '{question[:50]}...': {e}")
        return _mock_finding(question, supporting_chunks)


# ─────────────────────────────────────────────
# LangGraph node function
# ─────────────────────────────────────────────

def analyst_node(state: ResearchState) -> dict:
    """
    LangGraph node for the Analyst Agent.

    Reads: state['research_questions'], state['retrieved_context'], state['embeddings']
    Writes: state['findings'], state['agent_messages']
    """
    questions = state["research_questions"]
    context_chunks = state["retrieved_context"]
    embeddings = state["embeddings"]
    session_id = state["session_id"]

    logger.info(
        f"[Analyst Agent] Analyzing {len(questions)} questions "
        f"with {len(context_chunks)} context chunks"
    )

    findings = []

    for question_item in questions:
        question = question_item["question"]

        # Use semantic search to find relevant chunks for this question
        similar_records = search_similar(
            query_text=question,
            embedding_records=embeddings,
            top_k=3,
        )

        supporting_chunk_ids = [r["chunk_id"] for r in similar_records]
        context_texts = [r["text"] for r in similar_records]

        # Fall back to direct context matching if no embeddings
        if not context_texts and context_chunks:
            relevant = [
                c for c in context_chunks if c.get("question") == question
            ][:3]
            context_texts = [c["text"] for c in relevant]
            supporting_chunk_ids = [c["chunk_id"] for c in relevant]

        if state.get("debug"):
            logger.debug(
                f"  Analyzing: '{question[:60]}...' "
                f"| {len(supporting_chunk_ids)} supporting chunks"
            )

        # Generate finding
        if config.USE_MOCK_LLM:
            finding = _mock_finding(question, supporting_chunk_ids)
        else:
            finding = _llm_finding(question, context_texts, supporting_chunk_ids)

        findings.append(finding)
        logger.info(
            f"[Analyst Agent]   ✓ Finding [{finding['confidence']}]: "
            f"{question[:50]}..."
        )

    logger.info(f"[Analyst Agent] ✓ Generated {len(findings)} findings")

    # Create MCP-style message
    message = create_message(
        message_id=f"msg_{uuid.uuid4().hex[:8]}",
        session_id=session_id,
        sender_agent="analyst_agent",
        receiver_agent="critic_agent",
        message_type="findings_created",
        payload={
            "finding_count": len(findings),
            "findings": [
                {
                    "finding_id": f["finding_id"],
                    "question": f["question"],
                    "confidence": f["confidence"],
                }
                for f in findings
            ],
        },
        metadata={
            "high_confidence_count": sum(
                1 for f in findings if f["confidence"] == "high"
            ),
            "low_confidence_count": sum(
                1 for f in findings if f["confidence"] == "low"
            ),
        },
    )

    return {
        "findings": findings,
        "agent_messages": state["agent_messages"] + [message],
    }
