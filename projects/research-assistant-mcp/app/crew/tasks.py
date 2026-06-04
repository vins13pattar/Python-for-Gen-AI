"""
CrewAI Tasks — Task definitions mapped to each agent role.

Each task has:
- A description explaining what the agent must do
- An expected output description
- An assigned agent

Tasks are connected to form a research pipeline that mirrors the LangGraph workflow.
"""

import logging

logger = logging.getLogger(__name__)


def get_task_definitions(topic: str) -> list[dict]:
    """
    Return task definitions for all CrewAI agents.

    Args:
        topic: The research topic provided by the user.

    Returns:
        List of task configuration dicts, ordered by execution sequence.
    """
    return [
        {
            "agent_role": "research_planner",
            "name": "Plan Research",
            "description": (
                f"You have been given the research topic: '{topic}'.\n\n"
                "Your task is to:\n"
                "1. Analyze the topic and identify the key dimensions to investigate.\n"
                "2. Generate exactly 5-6 focused research questions that cover:\n"
                "   - Definition and core concepts\n"
                "   - Benefits and applications\n"
                "   - Risks and limitations\n"
                "   - Comparisons with alternatives\n"
                "   - Future outlook\n"
                "3. Assign a priority (high/medium/low) to each question.\n"
                "4. Return the questions as a structured JSON list.\n\n"
                "Format each question as: {\"question\": \"...\", \"priority\": \"high|medium|low\"}"
            ),
            "expected_output": (
                "A JSON array of 5-6 research question objects, each with 'question' "
                "and 'priority' fields. Questions must be specific, answerable, and "
                "cover all key dimensions of the topic."
            ),
        },
        {
            "agent_role": "context_retriever",
            "name": "Retrieve Context",
            "description": (
                "Using the research questions from the Planner, search the available "
                "knowledge sources for relevant context.\n\n"
                "For each research question:\n"
                "1. Identify the most relevant documents or text chunks.\n"
                "2. Extract 2-3 focused passages per question.\n"
                "3. Record the source type (local_markdown, web, mock).\n"
                "4. Structure each chunk with: chunk_id, text, question, source, source_type.\n\n"
                "If no specific context is available, synthesize the best available "
                "general knowledge about the topic."
            ),
            "expected_output": (
                "A list of context chunks (dicts) with fields: chunk_id, text, "
                "question, source, source_type. At least 2 chunks per research question."
            ),
        },
        {
            "agent_role": "embedding_specialist",
            "name": "Create Embeddings",
            "description": (
                "Take all retrieved context chunks and convert them to embedding vectors.\n\n"
                "For each chunk:\n"
                "1. Generate an embedding vector (real or mock depending on config).\n"
                "2. Create an embedding record with: chunk_id, embedding_id, text, "
                "embedding (vector), metadata.\n"
                "3. Ensure the embedding dimension is consistent across all records.\n\n"
                "These embeddings will be used by the Analyst for semantic search."
            ),
            "expected_output": (
                "A list of embedding records, each with: chunk_id, embedding_id, "
                "text, embedding (list of floats), and metadata dict."
            ),
        },
        {
            "agent_role": "research_analyst",
            "name": "Analyze and Extract Findings",
            "description": (
                "Using the context chunks and embeddings, extract key insights for each "
                "research question.\n\n"
                "For each question:\n"
                "1. Use semantic search to find the most relevant context chunks.\n"
                "2. Synthesize the context into a clear, substantive insight (2-3 sentences).\n"
                "3. Assess your confidence: high (strong evidence), medium (partial), "
                "low (limited evidence).\n"
                "4. Record which chunk IDs support your finding.\n\n"
                "Structure each finding as: finding_id, question, insight, confidence, "
                "supporting_chunks."
            ),
            "expected_output": (
                "A list of finding objects with: finding_id, question, insight "
                "(2-3 sentence summary), confidence (high/medium/low), and "
                "supporting_chunks (list of chunk IDs)."
            ),
        },
        {
            "agent_role": "research_critic",
            "name": "Review and Critique Findings",
            "description": (
                "Critically evaluate the research findings for quality, completeness, "
                "and accuracy.\n\n"
                "Check for:\n"
                "1. Are all research questions answered?\n"
                "2. Is the evidence (supporting chunks) sufficient?\n"
                "3. Are there any weak, vague, or unsupported findings?\n"
                "4. Is there proper coverage of risks/challenges?\n"
                "5. Are there any repetitive or redundant findings?\n\n"
                "Decision: Return 'approved' if findings are sufficient, or "
                "'needs_improvement' with specific issues listed."
            ),
            "expected_output": (
                "A critique dict with: status ('approved' or 'needs_improvement'), "
                "issues (list of specific problems), recommended_next_action "
                "('write_report' or 'retrieve_more_context'), and overall_quality."
            ),
        },
        {
            "agent_role": "research_writer",
            "name": "Write Final Research Report",
            "description": (
                f"Write a comprehensive Markdown research report on '{topic}'.\n\n"
                "The report must include these sections:\n"
                "1. Title and metadata (session ID, date, quality assessment)\n"
                "2. Executive Summary (2-3 paragraphs)\n"
                "3. Research Questions (all questions with priorities)\n"
                "4. Key Findings (one subsection per finding, with confidence level)\n"
                "5. MCP Usage Explanation (how agents used MCP in this session)\n"
                "6. Agent Collaboration Flow (ASCII diagram)\n"
                "7. Limitations (from critic feedback + general demo limitations)\n"
                "8. Conclusion\n\n"
                "Use the findings and critic feedback to write a polished, professional report."
            ),
            "expected_output": (
                "A complete Markdown document with all 8 sections, properly formatted "
                "with headings, bullet points, tables, and code blocks where appropriate. "
                "Minimum 800 words. Must incorporate all key findings."
            ),
        },
    ]


def convert_crewai_output_to_mcp_message(
    task_name: str,
    agent_role: str,
    output: str,
    session_id: str,
) -> dict:
    """
    Convert a CrewAI task output to an MCP-style message.

    This bridges the CrewAI execution model with the MCP message protocol,
    ensuring all agent outputs are properly structured and validated.

    Args:
        task_name: The name of the CrewAI task.
        agent_role: The CrewAI agent role that produced the output.
        output: The raw output string from the CrewAI task.
        session_id: Current research session ID.

    Returns:
        MCP-style message dict (not yet validated — call validate_message on it).
    """
    import uuid
    from datetime import datetime, timezone

    # Map agent roles to sender_agent names used in MCP schema
    role_to_agent = {
        "research_planner": "planner_agent",
        "context_retriever": "retriever_agent",
        "embedding_specialist": "embedding_agent",
        "research_analyst": "analyst_agent",
        "research_critic": "critic_agent",
        "research_writer": "writer_agent",
    }

    # Map agent roles to message types
    role_to_message_type = {
        "research_planner": "research_plan_created",
        "context_retriever": "context_retrieved",
        "embedding_specialist": "embeddings_created",
        "research_analyst": "findings_created",
        "research_critic": "critique_created",
        "research_writer": "final_report_created",
    }

    sender = role_to_agent.get(agent_role, "system")
    msg_type = role_to_message_type.get(agent_role, "status_update")

    return {
        "message_id": f"msg_{uuid.uuid4().hex[:8]}",
        "session_id": session_id,
        "sender_agent": sender,
        "receiver_agent": "broadcast",
        "message_type": msg_type,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "payload": {
            "task_name": task_name,
            "output_summary": output[:500] if output else "",
            "output_length": len(output) if output else 0,
        },
        "metadata": {
            "source": "crewai",
            "priority": "medium",
        },
    }
