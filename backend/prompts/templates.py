"""
Prompt Templates for AI Code Analysis
Structured prompts for explanation, improvement, and visualization
"""
from typing import Dict, Any, Optional


EXPLANATION_PROMPT = """You are a patient Python tutor for beginners. Explain the following code in simple, easy-to-understand language.

Focus on:
- What each part does (in plain English)
- Why it's useful
- How a beginner should think about it

Code:
```{code}```

Execution trace (how the code ran):
{execution_info}

Provide a clear, beginner-friendly explanation."""


IMPROVEMENT_PROMPT = """You are a Python expert. Analyze the following code and provide an improved version.

Code:
```{code}```

Error (if any): {error}

Provide:
1. What issues exist (briefly)
2. The improved code with comments
3. Key improvements explained simply"""


VISUALIZATION_PROMPT = """Generate a JSON visualization of how this Python code executes.

Code:
```{code}```

Execution trace:
{execution_info}

Generate a JSON object with this structure:
{{
  "flow": ["step1", "step2", ...],  // Logical flow of execution
  "steps": [
    {{"step": 1, "description": "...", "variables_changed": ["x", "y"]}},
    ...
  ],
  "key_points": ["point1", "point2"]  // Important concepts to highlight
}}

Provide ONLY valid JSON, no additional text."""


def create_explanation_prompt(code: str, execution_result: Optional[Dict] = None) -> str:
    """Create explanation prompt with code and execution data"""
    execution_info = ""
    if execution_result:
        steps = execution_result.get('execution', [])
        if steps:
            execution_info = "\nThe code was executed and these variables changed:\n"
            for step in steps[:10]:
                execution_info += f"- Line {step.get('line_number')}: {step.get('variables', {})}\n"
    
    return EXPLANATION_PROMPT.format(code=code, execution_info=execution_info)


def create_improvement_prompt(code: str, error: Optional[str] = None) -> str:
    """Create improvement prompt with code and error"""
    error_str = error if error else "No errors"
    return IMPROVEMENT_PROMPT.format(code=code, error=error_str)


def create_visualization_prompt(code: str, execution_result: Dict) -> str:
    """Create visualization prompt with code and execution data"""
    execution_info = str(execution_result.get('execution', []))[:1500]
    return VISUALIZATION_PROMPT.format(code=code, execution_info=execution_info)