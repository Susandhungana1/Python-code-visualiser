"""
API Routes for Code Analysis
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, HTTPException
from models.schemas import AnalyzeRequest, AnalyzeResponse, HealthResponse
from execution.tracer import execute_python_code
from services.ai_service import create_ai_service

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="ok", message="AI Python Visualizer API is running")


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_code(request: AnalyzeRequest):
    """
    Analyze Python code and return:
    - Explanation
    - Improved code
    - Execution trace
    - Visualization flow
    """
    try:
        execution_result = execute_python_code(request.code, timeout=5)
        
        ai_service = create_ai_service()
        analysis = ai_service.analyze_complete(request.code, execution_result)
        
        flow = analysis.get('visualization', {}).get('flow', [])
        steps = analysis.get('visualization', {}).get('steps', [])
        key_points = analysis.get('visualization', {}).get('key_points', [])
        
        return AnalyzeResponse(
            explanation=analysis.get('explanation', 'No explanation available'),
            fixed_code=analysis.get('fixed_code', request.code),
            execution=execution_result.get('execution', []),
            output=execution_result.get('output', []),
            flow=flow,
            steps=steps,
            key_points=key_points,
            error=execution_result.get('error')
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))