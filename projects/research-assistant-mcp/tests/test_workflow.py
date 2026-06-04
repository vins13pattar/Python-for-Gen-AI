"""
Tests for LangGraph Workflow.

Tests that:
1. Workflow builds and compiles without errors
2. Full end-to-end run completes successfully
3. Final report is generated
4. Agent messages are produced
5. Conditional critic routing works
"""

import pytest
from app.state.state_store import state_store


@pytest.fixture(autouse=True)
def reset_state():
    """Reset state before each test."""
    state_store.reset()
    yield
    state_store.reset()


class TestWorkflowBuild:
    """Tests for workflow construction."""

    def test_workflow_builds_without_error(self):
        """build_workflow() should not raise any errors."""
        from app.graph.workflow import build_workflow
        workflow = build_workflow()
        assert workflow is not None

    def test_workflow_is_compiled(self):
        """The returned workflow should be a compiled LangGraph graph."""
        from app.graph.workflow import build_workflow
        workflow = build_workflow()
        # Compiled graphs have an invoke method
        assert hasattr(workflow, "invoke")
        assert hasattr(workflow, "stream")

    def test_get_workflow_caches_instance(self):
        """get_workflow() should return the same instance on repeated calls."""
        from app.graph import workflow as wf_module
        wf_module._compiled_workflow = None  # Reset cache

        from app.graph.workflow import get_workflow
        w1 = get_workflow()
        w2 = get_workflow()
        assert w1 is w2


class TestWorkflowEndToEnd:
    """End-to-end workflow tests."""

    def test_full_workflow_runs_to_completion(self):
        """The full workflow should run start to end without errors."""
        from app.graph.workflow import get_workflow

        state_store.initialize(
            session_id="workflow_test_001",
            topic="MCP in multi-agent systems",
            debug=False,
        )
        initial_state = state_store.get_state()

        workflow = get_workflow()
        final_state = workflow.invoke(initial_state)

        assert final_state is not None

    def test_workflow_produces_research_questions(self):
        """After workflow, research_questions should be populated."""
        from app.graph.workflow import get_workflow

        state_store.initialize(
            session_id="workflow_test_002",
            topic="LangGraph stateful workflows",
            debug=False,
        )
        initial_state = state_store.get_state()

        workflow = get_workflow()
        final_state = workflow.invoke(initial_state)

        assert len(final_state.get("research_questions", [])) > 0

    def test_workflow_produces_final_report(self):
        """After workflow, final_report should be a non-empty string."""
        from app.graph.workflow import get_workflow

        state_store.initialize(
            session_id="workflow_test_003",
            topic="CrewAI role-based agents",
            debug=False,
        )
        initial_state = state_store.get_state()

        workflow = get_workflow()
        final_state = workflow.invoke(initial_state)

        assert "final_report" in final_state
        assert len(final_state["final_report"]) > 100

    def test_workflow_produces_agent_messages(self):
        """After workflow, agent_messages should contain entries from each agent."""
        from app.graph.workflow import get_workflow

        state_store.initialize(
            session_id="workflow_test_004",
            topic="Multi-agent collaboration",
            debug=False,
        )
        initial_state = state_store.get_state()

        workflow = get_workflow()
        final_state = workflow.invoke(initial_state)

        messages = final_state.get("agent_messages", [])
        assert len(messages) >= 6  # At least one message per agent

        # Check we have messages from all key agents
        senders = {m["sender_agent"] for m in messages}
        assert "planner_agent" in senders
        assert "retriever_agent" in senders
        assert "embedding_agent" in senders
        assert "analyst_agent" in senders
        assert "critic_agent" in senders
        assert "writer_agent" in senders

    def test_workflow_all_messages_are_schema_valid(self):
        """All agent messages produced by the workflow should be schema-valid."""
        from app.graph.workflow import get_workflow
        from app.validation.message_validator import validate_message

        state_store.initialize(
            session_id="workflow_test_005",
            topic="Shared context in AI systems",
            debug=False,
        )
        initial_state = state_store.get_state()

        workflow = get_workflow()
        final_state = workflow.invoke(initial_state)

        for i, msg in enumerate(final_state.get("agent_messages", [])):
            assert validate_message(msg) is True, (
                f"Message {i} ({msg.get('message_type')}) failed validation"
            )

    def test_workflow_produces_embeddings(self):
        """After workflow, embeddings should be populated."""
        from app.graph.workflow import get_workflow

        state_store.initialize(
            session_id="workflow_test_006",
            topic="Vector embeddings for semantic search",
            debug=False,
        )
        initial_state = state_store.get_state()

        workflow = get_workflow()
        final_state = workflow.invoke(initial_state)

        assert len(final_state.get("embeddings", [])) > 0

    def test_workflow_produces_findings(self):
        """After workflow, findings should be populated."""
        from app.graph.workflow import get_workflow

        state_store.initialize(
            session_id="workflow_test_007",
            topic="AI in education",
            debug=False,
        )
        initial_state = state_store.get_state()

        workflow = get_workflow()
        final_state = workflow.invoke(initial_state)

        assert len(final_state.get("findings", [])) > 0


class TestWorkflowConditionalRouting:
    """Tests for conditional critic routing."""

    def test_critique_status_is_set(self):
        """After critic runs, critique_status should be 'approved' or 'needs_improvement'."""
        from app.graph.workflow import get_workflow

        state_store.initialize(
            session_id="routing_test_001",
            topic="MCP routing test",
            debug=False,
        )
        initial_state = state_store.get_state()

        workflow = get_workflow()
        final_state = workflow.invoke(initial_state)

        assert final_state.get("critique_status") in {"approved", "needs_improvement"}

    def test_critic_retry_count_is_tracked(self):
        """critic_retry_count should reflect the number of retry loops."""
        from app.graph.workflow import get_workflow

        state_store.initialize(
            session_id="routing_test_002",
            topic="Retry loop testing",
            debug=False,
        )
        initial_state = state_store.get_state()

        workflow = get_workflow()
        final_state = workflow.invoke(initial_state)

        # Should be ≥ 0 and ≤ MAX_CRITIC_RETRIES + 1
        from app.config import config
        assert 0 <= final_state.get("critic_retry_count", 0) <= config.MAX_CRITIC_RETRIES + 1
