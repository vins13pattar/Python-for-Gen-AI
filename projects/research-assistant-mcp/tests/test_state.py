"""
Tests for Shared Research State.

Tests that:
1. State initializes with correct structure
2. State updates persist
3. State export produces valid JSON
4. StateStore singleton pattern works
"""

import pytest
import json
import uuid

from app.state.research_state import ResearchState
from app.state.state_store import StateStore, state_store


@pytest.fixture(autouse=True)
def reset_state():
    """Reset state store before each test."""
    state_store.reset()
    yield
    state_store.reset()


@pytest.fixture
def initialized_state():
    """Initialize a fresh state for testing."""
    return state_store.initialize(
        session_id="test_session_001",
        topic="Test Research Topic",
        debug=False,
    )


class TestStateInitialization:
    """Tests for state initialization."""

    def test_state_initializes_with_session_id(self, initialized_state):
        """Session ID should match what was passed to initialize()."""
        assert initialized_state["session_id"] == "test_session_001"

    def test_state_initializes_with_topic(self, initialized_state):
        """Topic should match what was passed."""
        assert initialized_state["topic"] == "Test Research Topic"

    def test_state_initializes_empty_lists(self, initialized_state):
        """All list fields should start empty."""
        assert initialized_state["research_questions"] == []
        assert initialized_state["retrieved_context"] == []
        assert initialized_state["embeddings"] == []
        assert initialized_state["findings"] == []
        assert initialized_state["critique"] == []
        assert initialized_state["agent_messages"] == []

    def test_state_initializes_empty_report(self, initialized_state):
        """Final report should start as empty string."""
        assert initialized_state["final_report"] == ""

    def test_state_initializes_critique_status(self, initialized_state):
        """Critique status should start as 'pending'."""
        assert initialized_state["critique_status"] == "pending"

    def test_state_initializes_retry_count_zero(self, initialized_state):
        """Critic retry count should start at 0."""
        assert initialized_state["critic_retry_count"] == 0

    def test_cannot_get_state_before_init(self):
        """Getting state before initialization should raise RuntimeError."""
        with pytest.raises(RuntimeError, match="not initialized"):
            state_store.get_state()


class TestStateUpdates:
    """Tests for state update operations."""

    def test_update_research_questions(self, initialized_state):
        """Research questions can be added to state."""
        questions = [{"question": "What is MCP?", "priority": "high"}]
        state_store.update_state({"research_questions": questions})

        updated = state_store.get_state()
        assert len(updated["research_questions"]) == 1
        assert updated["research_questions"][0]["question"] == "What is MCP?"

    def test_update_critique_status(self, initialized_state):
        """Critique status can be updated."""
        state_store.update_state({"critique_status": "approved"})
        state = state_store.get_state()
        assert state["critique_status"] == "approved"

    def test_update_final_report(self, initialized_state):
        """Final report can be set."""
        state_store.update_state({"final_report": "# My Report\n\nContent here."})
        state = state_store.get_state()
        assert state["final_report"].startswith("# My Report")

    def test_log_message_appends_to_state(self, initialized_state):
        """log_message() should append to agent_messages."""
        message = {
            "message_id": "msg_001",
            "session_id": "test_session_001",
            "sender_agent": "planner_agent",
            "receiver_agent": "retriever_agent",
            "message_type": "research_plan_created",
            "timestamp": "2026-05-28T10:00:00Z",
            "payload": {"questions": []},
        }
        state_store.log_message(message)
        state = state_store.get_state()
        assert len(state["agent_messages"]) == 1
        assert state["agent_messages"][0]["message_id"] == "msg_001"

    def test_log_multiple_messages(self, initialized_state):
        """Multiple messages can be logged."""
        for i in range(5):
            state_store.log_message({
                "message_id": f"msg_{i:03d}",
                "session_id": "test_session_001",
                "sender_agent": "planner_agent",
                "receiver_agent": "retriever_agent",
                "message_type": "research_plan_created",
                "timestamp": "2026-05-28T10:00:00Z",
                "payload": {},
            })

        state = state_store.get_state()
        assert len(state["agent_messages"]) == 5


class TestStateSingleton:
    """Tests for StateStore singleton pattern."""

    def test_state_store_is_singleton(self):
        """StateStore() always returns the same instance."""
        store1 = StateStore()
        store2 = StateStore()
        assert store1 is store2

    def test_global_state_store_is_singleton(self):
        """Global state_store instance is the same as new StateStore()."""
        new_store = StateStore()
        assert new_store is state_store

    def test_state_persists_across_get_calls(self, initialized_state):
        """State should be consistent across multiple get_state() calls."""
        state_store.update_state({"topic": "Updated Topic"})
        state1 = state_store.get_state()
        state2 = state_store.get_state()
        assert state1["topic"] == state2["topic"] == "Updated Topic"


class TestStateExport:
    """Tests for state export to JSON."""

    def test_state_export_creates_files(self, initialized_state, tmp_path, monkeypatch):
        """export_all() should create JSON output files."""
        from app.config import config
        monkeypatch.setattr(config, "OUTPUTS_DIR", tmp_path)

        state_store.update_state({"final_report": "# Test Report"})
        exported = state_store.export_all()

        assert "research_state" in exported
        assert exported["research_state"].exists()

        assert "agent_messages" in exported
        assert exported["agent_messages"].exists()

        assert "embeddings" in exported
        assert exported["embeddings"].exists()

    def test_exported_state_is_valid_json(self, initialized_state, tmp_path, monkeypatch):
        """Exported research_state.json should be parseable JSON."""
        from app.config import config
        monkeypatch.setattr(config, "OUTPUTS_DIR", tmp_path)

        exported = state_store.export_all()
        state_path = exported["research_state"]

        with open(state_path) as f:
            parsed = json.load(f)

        assert parsed["session_id"] == "test_session_001"
        assert parsed["topic"] == "Test Research Topic"

    def test_exported_messages_is_valid_json(self, initialized_state, tmp_path, monkeypatch):
        """Exported agent_messages.json should be a valid JSON array."""
        from app.config import config
        monkeypatch.setattr(config, "OUTPUTS_DIR", tmp_path)

        state_store.log_message({
            "message_id": "msg_export_test",
            "session_id": "test_session_001",
            "sender_agent": "planner_agent",
            "receiver_agent": "retriever_agent",
            "message_type": "research_plan_created",
            "timestamp": "2026-05-28T10:00:00Z",
            "payload": {},
        })

        exported = state_store.export_all()
        with open(exported["agent_messages"]) as f:
            messages = json.load(f)

        assert isinstance(messages, list)
        assert len(messages) == 1
        assert messages[0]["message_id"] == "msg_export_test"
