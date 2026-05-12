from pydantic import BaseModel, Field
from typing import List, Optional

class DebugIssue(BaseModel):
    error_type: str = Field(description="Type of error")
    root_cause: str = Field(description="Main reason for the issue")
    affected_line: Optional[int] = Field(default=None)
    severity: str = Field(description="low, medium, high, or critical")

class DebugReport(BaseModel):
    language: str
    issue: DebugIssue
    explanation: str
    fixed_code: str
    changes_made: List[str]
    test_cases: List[str] = Field(description="List of complete, runnable unit test functions as code strings")
    prevention_tips: List[str]
    confidence_score: float
