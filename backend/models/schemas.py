"""
Pydantic Models for API Request/Response Validation
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class AnalyzeRequest(BaseModel):
    """Request model for code analysis"""
    code: str = Field(..., min_length=1, max_length=10000, description="Python code to analyze")


class ExecutionStep(BaseModel):
    """Single step in code execution"""
    line_number: int
    code: str
    variables: Dict[str, Any]


class VisualizationStep(BaseModel):
    """Visualization step description"""
    step: int
    description: str
    variables_changed: List[str]


class AnalyzeResponse(BaseModel):
    """Response model for code analysis"""
    explanation: str = Field(..., description="Beginner-friendly explanation")
    fixed_code: str = Field(..., description="Improved version of code")
    execution: List[ExecutionStep] = Field(default_factory=list, description="Execution trace")
    output: List[str] = Field(default_factory=list, description="Code output")
    flow: List[str] = Field(default_factory=list, description="Logical execution flow")
    steps: List[VisualizationStep] = Field(default_factory=list, description="Visualization steps")
    key_points: List[str] = Field(default_factory=list, description="Key learning points")
    error: Optional[str] = Field(None, description="Error message if any")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str