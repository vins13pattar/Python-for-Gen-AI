"""
Message Validator — validates all MCP-style agent messages against JSON Schema.

Uses `jsonschema` to enforce the MCP message structure before any
message is added to shared state. All validation failures are logged.
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timezone

import jsonschema
from jsonschema import ValidationError, SchemaError

from app.config import config

logger = logging.getLogger(__name__)

# Load schema once at module import time
_SCHEMA_PATH = config.SCHEMAS_DIR / "mcp_message_schema.json"

try:
    with open(_SCHEMA_PATH, "r", encoding="utf-8") as f:
        _MCP_MESSAGE_SCHEMA = json.load(f)
except FileNotFoundError:
    raise RuntimeError(
        f"MCP message schema not found at {_SCHEMA_PATH}. "
        "Ensure app/schemas/mcp_message_schema.json exists."
    )


def validate_message(message: dict) -> bool:
    """
    Validate a message dict against the MCP message JSON Schema.

    Args:
        message: The agent message dictionary to validate.

    Returns:
        True if valid.

    Raises:
        ValidationError: If the message does not conform to the schema.
    """
    try:
        jsonschema.validate(instance=message, schema=_MCP_MESSAGE_SCHEMA)
        logger.debug(
            f"✓ Message validated: [{message.get('sender_agent')} → "
            f"{message.get('receiver_agent')}] {message.get('message_type')}"
        )
        return True

    except ValidationError as e:
        error_msg = (
            f"✗ MCP Message Validation FAILED:\n"
            f"  Message ID  : {message.get('message_id', 'UNKNOWN')}\n"
            f"  Sender      : {message.get('sender_agent', 'UNKNOWN')}\n"
            f"  Message Type: {message.get('message_type', 'UNKNOWN')}\n"
            f"  Error       : {e.message}\n"
            f"  Path        : {' → '.join(str(p) for p in e.absolute_path)}"
        )
        logger.error(error_msg)
        raise ValidationError(error_msg) from e

    except SchemaError as e:
        logger.critical(f"Schema itself is invalid: {e.message}")
        raise


def validate_tool_input(tool_name: str, input_data: dict) -> bool:
    """
    Validate MCP tool input against tool-specific schemas.

    Args:
        tool_name: The MCP tool name (e.g., 'save_context').
        input_data: The tool input dict.

    Returns:
        True if valid.

    Raises:
        ValidationError: If input is invalid.
    """
    tool_schema_path = config.SCHEMAS_DIR / "tool_input_schemas.json"

    try:
        with open(tool_schema_path, "r", encoding="utf-8") as f:
            all_schemas = json.load(f)
    except FileNotFoundError:
        logger.warning(f"Tool input schema file not found: {tool_schema_path}")
        return True  # Skip validation if schema file is missing

    # Map tool names to schema definitions
    schema_map = {
        "save_context": "SaveContextInput",
        "get_context": "GetContextInput",
        "save_embedding": "SaveEmbeddingInput",
        "search_context": "SearchContextInput",
        "log_agent_message": "LogAgentMessageInput",
    }

    schema_key = schema_map.get(tool_name)
    if not schema_key:
        logger.warning(f"No schema defined for tool: {tool_name}")
        return True

    schema = all_schemas.get("definitions", {}).get(schema_key)
    if not schema:
        logger.warning(f"Schema definition not found for: {schema_key}")
        return True

    jsonschema.validate(instance=input_data, schema=schema)
    logger.debug(f"✓ Tool input validated for: {tool_name}")
    return True


def create_message(
    message_id: str,
    session_id: str,
    sender_agent: str,
    receiver_agent: str,
    message_type: str,
    payload: dict,
    metadata: dict | None = None,
) -> dict:
    """
    Create and validate a well-formed MCP-style agent message.

    Args:
        message_id: Unique message identifier.
        session_id: Current research session ID.
        sender_agent: Name of the sending agent.
        receiver_agent: Name of the receiving agent.
        message_type: Type of message.
        payload: Message data payload.
        metadata: Optional metadata dict.

    Returns:
        Validated message dict.
    """
    message = {
        "message_id": message_id,
        "session_id": session_id,
        "sender_agent": sender_agent,
        "receiver_agent": receiver_agent,
        "message_type": message_type,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "payload": payload,
    }
    if metadata:
        message["metadata"] = metadata

    validate_message(message)
    return message
