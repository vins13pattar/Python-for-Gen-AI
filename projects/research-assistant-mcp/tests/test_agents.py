"""
Tests for all Agent functions.

Tests that:
1. Each agent node returns valid state updates
2. Each agent produces a valid MCP message
3. Agent messages are schema-valid
4. State fields are correctly updated
"""

import pytest
from app.state.state_store import state_store
from app.validation.message_validator import validate_message


@pytest.fixture(autouse=True)
def reset_state():
    """Reset state before each test."""
    state_store.reset()
    yield
    state_store.reset()


@pytest.fixture
def base_state():
    """Full initialized state for agent testing."""
    return state_store.initialize(
        session_id="agent_test_001",
        topic="MCP in multi-agent systems",
        debug=False,
    )


@pytest.fixture
def state_with_questions(base_state):
    """State with research questions populated."""
    state_store.update_state({
        "research_questions": [
            {"question": "What is MCP?", "priority": "high"},
            {"question": "How does MCP enable context sharing?", "priority": "high"},
            {"question": "What are the benefits of MCP?", "priority": "medium"},
        ]
    })
    return state_store.get_state()


@pytest.fixture
def state_with_context(state_with_questions):
    """State with retrieved context."""
    state_store.update_state({
        "retrieved_context": [
            {
                "chunk_id": "chunk_001",
                "text": "MCP is a protocol that allows AI apps to connect with tools and context.",
                "question": "What is MCP?",
                "source": "mcp_overview.md",
                "source_type": "local_markdown",
            },
            {
                "chunk_id": "chunk_002",
                "text": "Agents can share context through MCP tools like save_context and get_context.",
                "question": "How does MCP enable context sharing?",
                "source": "mcp_overview.md",
                "source_type": "local_markdown",
            },
        ]
    })
    return state_store.get_state()


@pytest.fixture
def state_with_embeddings(state_with_context):
    """State with embeddings."""
    state_store.update_state({
        "embeddings": [
            {
                "chunk_id": "chunk_001",
                "embedding_id": "emb_001",
                "text": "MCP is a protocol that allows AI apps to connect with tools and context.",
                "embedding": [0.1, 0.2, 0.3] * 128,  # 384-dim mock
                "metadata": {"source": "mcp_overview.md"},
            },
            {
                "chunk_id": "chunk_002",
                "embedding_id": "emb_002",
                "text": "Agents can share context through MCP tools.",
                "embedding": [0.2, 0.1, 0.4] * 128,
                "metadata": {"source": "mcp_overview.md"},
            },
        ]
    })
    return state_store.get_state()


@pytest.fixture
def state_with_findings(state_with_embeddings):
    """State with findings."""
    state_store.update_state({
        "findings": [
            {
                "finding_id": "finding_001",
                "question": "What is MCP?",
                "insight": "MCP is a standard protocol for connecting AI with tools.",
                "confidence": "high",
                "supporting_chunks": ["chunk_001"],
            },
            {
                "finding_id": "finding_002",
                "question": "How does MCP enable context sharing?",
                "insight": "Agents share context via MCP tools like save_context.",
                "confidence": "medium",
                "supporting_chunks": ["chunk_002"],
            },
        ]
    })
    return state_store.get_state()


# ─────────────────────────────────────────────
# Planner Agent Tests
# ─────────────────────────────────────────────

class TestPlannerAgent:
    def test_planner_returns_research_questions(self, base_state):
        """Planner should populate research_questions in state."""
        from app.agents.planner_agent import planner_node

        result = planner_node(base_state)

        assert "research_questions" in result
        assert len(result["research_questions"]) >= 4
        assert len(result["research_questions"]) <= 6

    def test_planner_questions_have_required_fields(self, base_state):
        """Each question should have 'question' and 'priority' fields."""
        from app.agents.planner_agent import planner_node

        result = planner_node(base_state)

        for q in result["research_questions"]:
            assert "question" in q
            assert "priority" in q
            assert q["priority"] in {"high", "medium", "low"}
            assert len(q["question"]) > 5

    def test_planner_produces_valid_mcp_message(self, base_state):
        """Planner should produce a schema-valid MCP message."""
        from app.agents.planner_agent import planner_node

        result = planner_node(base_state)
        messages = result.get("agent_messages", [])

        assert len(messages) >= 1
        last_msg = messages[-1]
        assert validate_message(last_msg) is True
        assert last_msg["message_type"] == "research_plan_created"
        assert last_msg["sender_agent"] == "planner_agent"


# ─────────────────────────────────────────────
# Retriever Agent Tests
# ─────────────────────────────────────────────

class TestRetrieverAgent:
    def test_retriever_returns_context_chunks(self, state_with_questions):
        """Retriever should populate retrieved_context."""
        from app.agents.retriever_agent import retriever_node

        result = retriever_node(state_with_questions)

        assert "retrieved_context" in result
        assert len(result["retrieved_context"]) > 0

    def test_retriever_chunks_have_required_fields(self, state_with_questions):
        """Each chunk should have chunk_id, text, question, source, source_type."""
        from app.agents.retriever_agent import retriever_node

        result = retriever_node(state_with_questions)

        for chunk in result["retrieved_context"]:
            assert "chunk_id" in chunk
            assert "text" in chunk
            assert "question" in chunk
            assert "source" in chunk
            assert "source_type" in chunk
            assert len(chunk["text"]) > 0

    def test_retriever_produces_valid_mcp_message(self, state_with_questions):
        """Retriever should produce a schema-valid MCP message."""
        from app.agents.retriever_agent import retriever_node

        result = retriever_node(state_with_questions)
        messages = result.get("agent_messages", [])

        assert len(messages) >= 1
        last_msg = messages[-1]
        assert validate_message(last_msg) is True
        assert last_msg["message_type"] == "context_retrieved"
        assert last_msg["sender_agent"] == "retriever_agent"


# ─────────────────────────────────────────────
# Embedding Agent Tests
# ─────────────────────────────────────────────

class TestEmbeddingAgent:
    def test_embedding_agent_creates_records(self, state_with_context):
        """Embedding agent should create one record per context chunk."""
        from app.agents.embedding_agent import embedding_node

        result = embedding_node(state_with_context)

        assert "embeddings" in result
        assert len(result["embeddings"]) == len(state_with_context["retrieved_context"])

    def test_embedding_records_have_required_fields(self, state_with_context):
        """Each embedding record should have required fields."""
        from app.agents.embedding_agent import embedding_node

        result = embedding_node(state_with_context)

        for record in result["embeddings"]:
            assert "chunk_id" in record
            assert "embedding_id" in record
            assert "embedding" in record
            assert isinstance(record["embedding"], list)
            assert len(record["embedding"]) > 0

    def test_embedding_agent_produces_valid_mcp_message(self, state_with_context):
        """Embedding agent should produce a schema-valid MCP message."""
        from app.agents.embedding_agent import embedding_node

        result = embedding_node(state_with_context)
        messages = result.get("agent_messages", [])

        assert len(messages) >= 1
        last_msg = messages[-1]
        assert validate_message(last_msg) is True
        assert last_msg["message_type"] == "embeddings_created"
        assert last_msg["sender_agent"] == "embedding_agent"


# ─────────────────────────────────────────────
# Analyst Agent Tests
# ─────────────────────────────────────────────

class TestAnalystAgent:
    def test_analyst_produces_findings(self, state_with_embeddings):
        """Analyst should create findings for each research question."""
        from app.agents.analyst_agent import analyst_node

        result = analyst_node(state_with_embeddings)

        assert "findings" in result
        assert len(result["findings"]) > 0

    def test_analyst_findings_have_required_fields(self, state_with_embeddings):
        """Each finding should have required fields."""
        from app.agents.analyst_agent import analyst_node

        result = analyst_node(state_with_embeddings)

        for finding in result["findings"]:
            assert "finding_id" in finding
            assert "question" in finding
            assert "insight" in finding
            assert "confidence" in finding
            assert finding["confidence"] in {"high", "medium", "low"}
            assert "supporting_chunks" in finding

    def test_analyst_produces_valid_mcp_message(self, state_with_embeddings):
        """Analyst should produce a schema-valid MCP message."""
        from app.agents.analyst_agent import analyst_node

        result = analyst_node(state_with_embeddings)
        messages = result.get("agent_messages", [])

        assert len(messages) >= 1
        last_msg = messages[-1]
        assert validate_message(last_msg) is True
        assert last_msg["message_type"] == "findings_created"
        assert last_msg["sender_agent"] == "analyst_agent"


# ─────────────────────────────────────────────
# Critic Agent Tests
# ─────────────────────────────────────────────

class TestCriticAgent:
    def test_critic_returns_critique_status(self, state_with_findings):
        """Critic should return critique_status field."""
        from app.agents.critic_agent import critic_node

        result = critic_node(state_with_findings)

        assert "critique_status" in result
        assert result["critique_status"] in {"approved", "needs_improvement"}

    def test_critic_produces_valid_mcp_message(self, state_with_findings):
        """Critic should produce a schema-valid MCP message."""
        from app.agents.critic_agent import critic_node

        result = critic_node(state_with_findings)
        messages = result.get("agent_messages", [])

        assert len(messages) >= 1
        last_msg = messages[-1]
        assert validate_message(last_msg) is True
        assert last_msg["message_type"] == "critique_created"
        assert last_msg["sender_agent"] == "critic_agent"

    def test_critic_approves_after_max_retries(self, state_with_findings):
        """Critic should force approve after MAX_CRITIC_RETRIES."""
        from app.agents.critic_agent import critic_node
        from app.config import config

        # Set retry count to max
        state_store.update_state({"critic_retry_count": config.MAX_CRITIC_RETRIES})
        state = state_store.get_state()

        result = critic_node(state)
        assert result["critique_status"] == "approved"

    def test_should_retry_returns_correct_routing(self, state_with_findings):
        """should_retry() should return 'retry' or 'write'."""
        from app.agents.critic_agent import should_retry

        # Test approved → write
        state_store.update_state({"critique_status": "approved"})
        assert should_retry(state_store.get_state()) == "write"

        # Test needs_improvement → retry (when under max retries)
        state_store.update_state({
            "critique_status": "needs_improvement",
            "critic_retry_count": 0,
        })
        assert should_retry(state_store.get_state()) == "retry"


# ─────────────────────────────────────────────
# Writer Agent Tests
# ─────────────────────────────────────────────

class TestWriterAgent:
    def test_writer_produces_final_report(self, state_with_findings):
        """Writer should produce a non-empty final report."""
        from app.agents.writer_agent import writer_node

        result = writer_node(state_with_findings)

        assert "final_report" in result
        assert len(result["final_report"]) > 100

    def test_writer_report_is_markdown(self, state_with_findings):
        """Writer report should contain Markdown headings."""
        from app.agents.writer_agent import writer_node

        result = writer_node(state_with_findings)

        assert "# " in result["final_report"]

    def test_writer_report_contains_topic(self, state_with_findings):
        """Writer report should mention the research topic."""
        from app.agents.writer_agent import writer_node

        result = writer_node(state_with_findings)
        topic = state_with_findings["topic"]

        assert topic in result["final_report"]

    def test_writer_produces_valid_mcp_message(self, state_with_findings):
        """Writer should produce a schema-valid MCP message."""
        from app.agents.writer_agent import writer_node

        result = writer_node(state_with_findings)
        messages = result.get("agent_messages", [])

        assert len(messages) >= 1
        last_msg = messages[-1]
        assert validate_message(last_msg) is True
        assert last_msg["message_type"] == "final_report_created"
        assert last_msg["sender_agent"] == "writer_agent"
