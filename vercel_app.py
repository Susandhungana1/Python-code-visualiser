"""
Python Code Visualizer - Backend for Vercel
"""
import os
import sys

# Get API key from environment variable
api_key = os.environ.get('OPENROUTER_API_KEY', '')

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    code: str


app = FastApi()

app = FastAPI(title="Python Code Visualizer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def execute_code(code: str) -> dict:
    """Execute Python code with tracing"""
    import sys
    
    execution_steps = []
    output = []
    error = None
    
    class Tracer:
        def __init__(self):
            self.steps = []
        
        def trace_calls(self, frame, event, arg):
            if event == 'line':
                filename = frame.f_code.co_filename
                if filename == '<string>':
                    lineno = frame.f_lineno
                    lines = frame.f_globals.get('_source_lines', [])
                    code_line = lines[lineno - 1] if 0 <= lineno - 1 < len(lines) else f"Line {lineno}"
                    
                    local_vars = {}
                    for k, v in frame.f_locals.items():
                        if not k.startswith('__') and k not in ['_source_lines']:
                            try:
                                local_vars[k] = repr(v)[:100]
                            except:
                                local_vars[k] = f"<{type(v).__name__}>"
                    
                    self.steps.append({
                        'line_number': lineno,
                        'code': code_line,
                        'variables': local_vars
                    })
            return self.tracing
    
    def tracing(frame, event, arg):
        return tracer.trace_calls(frame, event, arg)
    
    tracer = Tracer()
    safe_globals = {
        '__builtins__': {
            'print': lambda *args: output.append(' '.join(str(a) for a in args)),
            'len': len, 'range': range, 'str': str, 'int': int, 'float': float,
            'bool': bool, 'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
            'abs': abs, 'min': min, 'max': max, 'sum': sum, 'sorted': sorted,
            'enumerate': enumerate, 'zip': zip, 'map': map, 'filter': filter,
            'type': type, 'isinstance': isinstance, 'input': lambda *a: 'input blocked',
            'open': lambda *a: 'open blocked', 'eval': lambda *a: 'eval blocked',
            'exec': lambda *a: 'exec blocked', '__import__': lambda *a: 'import blocked',
        },
        '_source_lines': code.split('\n'),
    }
    
    try:
        old_trace = sys.gettrace()
        sys.settrace(tracing)
        compiled = compile(code, '<string>', 'exec')
        exec(compiled, safe_globals)
        sys.settrace(old_trace)
    except Exception as e:
        error = f"{type(e).__name__}: {str(e)}"
    
    filtered = []
    seen = set()
    for step in tracer.steps:
        if step['line_number'] not in seen:
            seen.add(step['line_number'])
            filtered.append(step)
    
    return {'execution': filtered, 'output': output, 'error': error}


def call_ai(code: str, execution_result: dict, api_key: str) -> dict:
    """Call OpenRouter AI API"""
    if not api_key or api_key == 'your_openrouter_api_key_here':
        lines = code.strip().split('\n')
        return {
            'explanation': f"This Python code has {len(lines)} lines.\n\n" + '\n'.join([f"Line {i+1}: {line}" for i, line in enumerate(lines) if line.strip()]),
            'fixed_code': f"# Improved version\n\n{code}",
            'flow': ['Start'] + [f'Step {i+1}' for i in range(len(lines))] + ['End'],
            'steps': [{'step': i+1, 'description': line.strip(), 'variables_changed': []} for i, line in enumerate(lines) if line.strip()],
            'key_points': ['Code executes line by line', 'Variables store values', 'Functions organize code']
        }
    
    execution_info = str(execution_result.get('execution', []))[:1000]
    
    prompt = f"""Analyze this Python code and provide:
1. A beginner-friendly explanation
2. Improved version of the code
3. Execution flow as JSON

Code:
```{code}```

Execution trace: {execution_info}

Provide JSON with: explanation, fixed_code, flow (array), steps (array with step, description, variables_changed), key_points (array)"""

    try:
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openrouter/auto",
                "messages": [
                    {"role": "system", "content": "You are a Python tutor. Provide explanations in simple language. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            },
            timeout=30.0
        )
        
        content = response.json()['choices'][0]['message']['content']
        
        import json
        try:
            return json.loads(content)
        except:
            start, end = content.find('{'), content.rfind('}')
            if start >= 0 and end > start:
                return json.loads(content[start:end+1])
            return {'error': 'Failed to parse AI response'}
    except Exception as e:
        return {'error': str(e)}


@app.get("/")
async def root():
    return {"status": "ok", "message": "Python Code Visualizer API"}


@app.post("/api/v1/analyze")
async def analyze(request: AnalyzeRequest):
    execution_result = execute_code(request.code)
    ai_result = call_ai(request.code, execution_result, api_key)
    
    return {
        "explanation": ai_result.get('explanation', 'No explanation available'),
        "fixed_code": ai_result.get('fixed_code', request.code),
        "execution": execution_result.get('execution', []),
        "output": execution_result.get('output', []),
        "flow": ai_result.get('flow', []),
        "steps": ai_result.get('steps', []),
        "key_points": ai_result.get('key_points', []),
        "error": execution_result.get('error')
    }


# Vercel entry point
handler = app