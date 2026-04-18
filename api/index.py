"""
Python Code Visualizer - Vercel Serverless Function
"""
import os

api_key = os.environ.get('OPENROUTER_API_KEY', '')

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    code: str


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
    
    output = []
    error = None
    steps = []
    seen_lines = set()
    
    def tracing(frame, event, arg):
        if event == 'line':
            filename = frame.f_code.co_filename
            if filename == '<string>':
                lineno = frame.f_lineno
                if lineno in seen_lines:
                    return tracing
                seen_lines.add(lineno)
                
                lines = frame.f_globals.get('_source_lines', [])
                code_line = lines[lineno - 1] if 0 <= lineno - 1 < len(lines) else f"Line {lineno}"
                
                local_vars = {}
                for k, v in frame.f_locals.items():
                    if not k.startswith('__') and k not in ['_source_lines']:
                        try:
                            local_vars[k] = repr(v)[:50]
                        except:
                            local_vars[k] = f"<{type(v).__name__}>"
                
                steps.append({'line_number': lineno, 'code': code_line, 'variables': local_vars})
        return tracing
    
    safe_globals = {
        '__builtins__': {
            'print': lambda *args: output.append(' '.join(str(a) for a in args)),
            'len': len, 'range': range, 'str': str, 'int': int, 'float': float,
            'bool': bool, 'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
            'abs': abs, 'min': min, 'max': max, 'sum': sum, 'sorted': sorted,
            'enumerate': enumerate, 'zip': zip, 'map': map, 'filter': filter,
            'type': type, 'isinstance': isinstance, 'input': lambda *a: 'blocked',
            'open': lambda *a: 'blocked', 'eval': lambda *a: 'blocked',
            'exec': lambda *a: 'blocked', '__import__': lambda *a: 'blocked',
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
    
    return {'execution': steps, 'output': output, 'error': error}


def call_ai(code: str, execution_result: dict, api_key: str) -> dict:
    """Call OpenRouter AI"""
    if not api_key or api_key == 'your_openrouter_api_key_here':
        lines = [l for l in code.strip().split('\n') if l.strip()]
        return {
            'explanation': f"This Python code has {len(lines)} lines.\n\n" + '\n'.join([f"- Line {i+1}: {l}" for i, l in enumerate(lines)]),
            'fixed_code': f"# Improved version\n\n{code}",
            'flow': ['Start'] + [f'Step {i+1}' for i in range(len(lines))] + ['End'],
            'steps': [{'step': i+1, 'description': l.strip(), 'variables_changed': []} for i, l in enumerate(lines)],
            'key_points': ['Code executes line by line', 'Variables store values', 'Functions organize code']
        }
    
    import json
    prompt = f"""Analyze this Python code. Return JSON with:
- explanation (beginner-friendly)
- fixed_code (improved version)
- flow (array of steps)
- steps (array with step, description, variables_changed)
- key_points (array)

Code: {code[:500]}
Execution: {str(execution_result.get('execution', []))[:500]}"""

    try:
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "openrouter/auto", "messages": [
                {"role": "system", "content": "You are a Python tutor. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ], "temperature": 0.7, "max_tokens": 2000},
            timeout=30.0
        )
        content = response.json()['choices'][0]['message']['content']
        try:
            return json.loads(content)
        except:
            start, end = content.find('{'), content.rfind('}')
            return json.loads(content[start:end+1]) if start >= 0 else {'error': 'Parse failed'}
    except Exception as e:
        return {'error': str(e)}


@app.get("/")
async def root():
    return {"status": "ok", "message": "Python Code Visualizer"}


@app.post("/api/v1/analyze")
async def analyze(request: AnalyzeRequest):
    exec_result = execute_code(request.code)
    ai_result = call_ai(request.code, exec_result, api_key)
    
    return {
        "explanation": ai_result.get('explanation', 'No explanation'),
        "fixed_code": ai_result.get('fixed_code', request.code),
        "execution": exec_result.get('execution', []),
        "output": exec_result.get('output', []),
        "flow": ai_result.get('flow', []),
        "steps": ai_result.get('steps', []),
        "key_points": ai_result.get('key_points', []),
        "error": exec_result.get('error')
    }


# Vercel entry point
handler = app