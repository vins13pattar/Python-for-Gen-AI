from pydantic import BaseModel, Field
from typing import Optional

class DebugRequest(BaseModel):
    language: Optional[str] = Field(default=None, description="Programming language of the code")
    code: str = Field(description="The source code to debug")
    error_message: Optional[str] = Field(default=None, description="The error message or traceback")
    expected_behavior: Optional[str] = Field(default=None, description="What the code is expected to do")
