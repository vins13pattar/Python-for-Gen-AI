"""
Unit tests for Pydantic schemas (DebugReport, DebugIssue).
No LLM or API key needed.
"""
import pytest
from app.schemas.response import DebugReport, DebugIssue


class TestDebugIssueSchema:
    def test_basic_construction(self):
        issue = DebugIssue(
            error_type="NameError",
            root_cause="Variable c is not defined",
            affected_line=1,
            severity="medium",
        )
        assert issue.error_type == "NameError"
        assert issue.severity == "medium"

    def test_affected_line_optional(self):
        issue = DebugIssue(
            error_type="LogicError",
            root_cause="Wrong condition",
            severity="low",
        )
        assert issue.affected_line is None

    def test_missing_required_field_raises(self):
        with pytest.raises(Exception):
            DebugIssue(root_cause="Missing error_type", severity="low")


class TestDebugReportSchema:
    def _make_issue(self):
        return DebugIssue(
            error_type="ZeroDivisionError",
            root_cause="Division by zero when b=0",
            affected_line=2,
            severity="high",
        )

    def test_valid_report(self):
        report = DebugReport(
            language="python",
            issue=self._make_issue(),
            explanation="b cannot be zero",
            fixed_code="def divide(a, b):\n    if b == 0: return None\n    return a / b",
            changes_made=["Added zero check"],
            test_cases=["assert divide(10,2)==5", "assert divide(10,0) is None"],
            prevention_tips=["Validate divisor before division"],
            confidence_score=0.95,
        )
        assert report.language == "python"
        assert len(report.test_cases) == 2
        assert 0.0 <= report.confidence_score <= 1.0

    def test_model_dump_is_json_serializable(self):
        import json
        report = DebugReport(
            language="javascript",
            issue=self._make_issue(),
            explanation="Some explanation",
            fixed_code="const x = 1;",
            changes_made=[],
            test_cases=[],
            prevention_tips=[],
            confidence_score=0.8,
        )
        dumped = report.model_dump()
        # Should not raise
        serialized = json.dumps(dumped)
        assert "javascript" in serialized

    def test_missing_language_raises(self):
        with pytest.raises(Exception):
            DebugReport(
                issue=self._make_issue(),
                explanation="x",
                fixed_code="x",
                changes_made=[],
                test_cases=[],
                prevention_tips=[],
                confidence_score=0.9,
            )
