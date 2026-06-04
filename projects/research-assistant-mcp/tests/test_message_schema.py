"""
Tests for MCP Message Schema Validation.

Tests that:
1. Valid messages pass validation
2. Missing required fields raise ValidationError
3. Invalid field types raise ValidationError
4. Invalid enum values raise ValidationError
5. The create_message() helper produces valid messages
"""

import pytest
from datetime import datetime, timezone
from jsonschema import ValidationError

from app.validation.message_validator import validate_message, create_message


# ─────────────────────────────────────────────
# Valid message fixture
# ─────────────────────────────────────────────

@pytest.fixture
def valid_message():
    """A fully valid MCP-style message."""
    return {
        "message_id": "msg_001",
        "session_id": "research_001",
        "sender_agent": "planner_agent",
        "receiver_agent": "retriever_agent",
        "message_type": "research_plan_created",
        "timestamp": "2026-05-28T10:00:00Z",
        "payload": {
            "topic": "MCP in multi-agent systems",
            "questions": ["What is MCP?", "How does MCP support shared context?"],
        },
        "metadata": {
            "priority": "high",
            "requires_response": True,
        },
    }


# ─────────────────────────────────────────────
# Valid message tests
# ─────────────────────────────────────────────

class TestValidMessages:
    """Tests that valid messages pass schema validation."""

    def test_valid_complete_message(self, valid_message):
        """A complete, fully-formed message should pass validation."""
        assert validate_message(valid_message) is True

    def test_valid_message_without_metadata(self, valid_message):
        """Metadata is optional — message should pass without it."""
        del valid_message["metadata"]
        assert validate_message(valid_message) is True

    def test_valid_all_sender_agents(self):
        """All allowed sender_agent values should pass."""
        allowed_senders = [
            "planner_agent",
            "retriever_agent",
            "embedding_agent",
            "analyst_agent",
            "critic_agent",
            "writer_agent",
            "system",
        ]
        for sender in allowed_senders:
            msg = {
                "message_id": "msg_test",
                "session_id": "sess_001",
                "sender_agent": sender,
                "receiver_agent": "broadcast",
                "message_type": "status_update",
                "timestamp": "2026-05-28T10:00:00Z",
                "payload": {},
            }
            assert validate_message(msg) is True, f"Failed for sender: {sender}"

    def test_valid_all_message_types(self):
        """All allowed message_type values should pass."""
        allowed_types = [
            "research_plan_created",
            "context_retrieved",
            "embeddings_created",
            "findings_created",
            "critique_created",
            "final_report_created",
            "error",
            "status_update",
        ]
        for msg_type in allowed_types:
            msg = {
                "message_id": "msg_test",
                "session_id": "sess_001",
                "sender_agent": "planner_agent",
                "receiver_agent": "retriever_agent",
                "message_type": msg_type,
                "timestamp": "2026-05-28T10:00:00Z",
                "payload": {},
            }
            assert validate_message(msg) is True, f"Failed for type: {msg_type}"

    def test_valid_planner_to_retriever_message(self):
        """Test the exact example from the PRD."""
        message = {
            "message_id": "msg_001",
            "session_id": "research_001",
            "sender_agent": "planner_agent",
            "receiver_agent": "retriever_agent",
            "message_type": "research_plan_created",
            "timestamp": "2026-05-28T10:00:00Z",
            "payload": {
                "questions": ["What is MCP?"]
            },
        }
        validate_message(message)
        assert message["message_type"] == "research_plan_created"


# ─────────────────────────────────────────────
# Invalid message tests
# ─────────────────────────────────────────────

class TestInvalidMessages:
    """Tests that invalid messages raise ValidationError."""

    def test_missing_message_id(self, valid_message):
        """Missing message_id should raise ValidationError."""
        del valid_message["message_id"]
        with pytest.raises(ValidationError):
            validate_message(valid_message)

    def test_missing_session_id(self, valid_message):
        """Missing session_id should raise ValidationError."""
        del valid_message["session_id"]
        with pytest.raises(ValidationError):
            validate_message(valid_message)

    def test_missing_sender_agent(self, valid_message):
        """Missing sender_agent should raise ValidationError."""
        del valid_message["sender_agent"]
        with pytest.raises(ValidationError):
            validate_message(valid_message)

    def test_missing_receiver_agent(self, valid_message):
        """Missing receiver_agent should raise ValidationError."""
        del valid_message["receiver_agent"]
        with pytest.raises(ValidationError):
            validate_message(valid_message)

    def test_missing_message_type(self, valid_message):
        """Missing message_type should raise ValidationError."""
        del valid_message["message_type"]
        with pytest.raises(ValidationError):
            validate_message(valid_message)

    def test_missing_timestamp(self, valid_message):
        """Missing timestamp should raise ValidationError."""
        del valid_message["timestamp"]
        with pytest.raises(ValidationError):
            validate_message(valid_message)

    def test_missing_payload(self, valid_message):
        """Missing payload should raise ValidationError."""
        del valid_message["payload"]
        with pytest.raises(ValidationError):
            validate_message(valid_message)

    def test_invalid_sender_agent_value(self, valid_message):
        """An invalid sender_agent enum value should raise ValidationError."""
        valid_message["sender_agent"] = "unknown_agent"
        with pytest.raises(ValidationError):
            validate_message(valid_message)

    def test_invalid_message_type_value(self, valid_message):
        """An invalid message_type enum value should raise ValidationError."""
        valid_message["message_type"] = "made_up_type"
        with pytest.raises(ValidationError):
            validate_message(valid_message)

    def test_payload_must_be_object(self, valid_message):
        """payload must be an object, not a string."""
        valid_message["payload"] = "not an object"
        with pytest.raises(ValidationError):
            validate_message(valid_message)

    def test_empty_message_id(self, valid_message):
        """Empty string message_id should raise ValidationError."""
        valid_message["message_id"] = ""
        with pytest.raises(ValidationError):
            validate_message(valid_message)

    def test_empty_dict_fails_required_fields(self):
        """Empty dict should fail — all required fields missing."""
        with pytest.raises(ValidationError):
            validate_message({})


# ─────────────────────────────────────────────
# create_message() helper tests
# ─────────────────────────────────────────────

class TestCreateMessage:
    """Tests for the create_message() convenience function."""

    def test_create_message_returns_valid_dict(self):
        """create_message should return a valid, validated message."""
        msg = create_message(
            message_id="msg_test_001",
            session_id="sess_test",
            sender_agent="planner_agent",
            receiver_agent="retriever_agent",
            message_type="research_plan_created",
            payload={"questions": ["What is MCP?"]},
        )
        assert msg["message_id"] == "msg_test_001"
        assert msg["sender_agent"] == "planner_agent"
        assert msg["message_type"] == "research_plan_created"
        assert "timestamp" in msg

    def test_create_message_timestamp_format(self):
        """Timestamp should be ISO 8601 format ending with Z."""
        msg = create_message(
            message_id="msg_ts",
            session_id="sess_001",
            sender_agent="writer_agent",
            receiver_agent="system",
            message_type="final_report_created",
            payload={"word_count": 1000},
        )
        assert msg["timestamp"].endswith("Z")

    def test_create_message_with_metadata(self):
        """create_message with metadata should include it in output."""
        msg = create_message(
            message_id="msg_meta",
            session_id="sess_001",
            sender_agent="critic_agent",
            receiver_agent="writer_agent",
            message_type="critique_created",
            payload={"status": "approved"},
            metadata={"priority": "high", "requires_response": False},
        )
        assert msg["metadata"]["priority"] == "high"
        assert msg["metadata"]["requires_response"] is False
