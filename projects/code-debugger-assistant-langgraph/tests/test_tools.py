"""
Unit tests for individual tools.
Tests that do NOT require an OpenAI API key are marked as pure unit tests.
Tests that call the LLM are marked with @pytest.mark.integration.
"""
import pytest
from unittest.mock import patch
from app.tools.security_check import security_check_tool


# ── security_check_tool ───────────────────────────────────────────────────────

class TestSecurityCheckTool:
    """Tests for the static security scanner — no LLM needed."""

    def test_safe_code_passes(self):
        result = security_check_tool.invoke({
            "code": "def add(a, b): return a + b",
            "expected_behavior": "Return sum",
        })
        assert "SAFE" in result

    def test_os_system_flagged(self):
        result = security_check_tool.invoke({
            "code": "import os\nos.system('rm -rf /')",
            "expected_behavior": "Delete files",
        })
        assert "BLOCKED" in result or "SECURITY_WARNING" in result

    def test_eval_flagged(self):
        result = security_check_tool.invoke({
            "code": "eval(user_input)",
            "expected_behavior": "Execute input",
        })
        assert "BLOCKED" in result or "SECURITY_WARNING" in result

    def test_subprocess_flagged(self):
        result = security_check_tool.invoke({
            "code": "import subprocess\nsubprocess.run(['ls'])",
            "expected_behavior": "List files",
        })
        assert "BLOCKED" in result or "SECURITY_WARNING" in result

    def test_expected_behavior_also_scanned(self):
        result = security_check_tool.invoke({
            "code": "def foo(): pass",
            "expected_behavior": "Run exec() on the output",
        })
        assert "BLOCKED" in result or "SECURITY_WARNING" in result

    def test_empty_inputs(self):
        result = security_check_tool.invoke({"code": "", "expected_behavior": ""})
        assert "SAFE" in result
