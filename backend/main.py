"""
Python Code Visualizer - Vercel Serverless Function
"""
import os

api_key = os.environ.get('OPENROUTER_API_KEY', '')

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

HTML_CONTENT = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python Code Visualizer</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; padding: 30px 0; border-bottom: 1px solid #1e293b; margin-bottom: 30px; }
        .header h1 { font-size: 2.5rem; color: #38bdf8; margin-bottom: 10px; }
        .header p { color: #94a3b8; font-size: 1.1rem; }
        .main-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
        @media (max-width: 1024px) { .main-grid { grid-template-columns: 1fr; } }
        .panel { background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }
        .panel-title { font-size: 1.1rem; font-weight: 600; color: #f1f5f9; margin-bottom: 16px; }
        textarea { width: 100%; height: 400px; background: #0f172a; color: #e2e8f0; border: 1px solid #334155; border-radius: 8px; padding: 16px; font-family: monospace; font-size: 14px; resize: vertical; }
        .btn { width: 100%; padding: 16px; font-size: 1.1rem; font-weight: 600; background: linear-gradient(135deg, #0ea5e9, #3b82f6); color: white; border: none; border-radius: 8px; cursor: pointer; margin-top: 16px; }
        .btn:hover { transform: translateY(-2px); }
        .btn:disabled { opacity: 0.5; }
        .tabs { display: flex; gap: 8px; margin-bottom: 16px; border-bottom: 1px solid #334155; padding-bottom: 8px; flex-wrap: wrap; }
        .tab { padding: 8px 16px; background: transparent; border: none; color: #94a3b8; cursor: pointer; border-radius: 6px; font-size: 0.9rem; }
        .tab.active { background: #334155; color: #38bdf8; }
        .result-content { color: #cbd5e1; line-height: 1.7; white-space: pre-wrap; }
        .code-block { background: #0f172a; padding: 16px; border-radius: 8px; font-family: monospace; font-size: 0.9rem; overflow-x: auto; color: #a5b4fc; white-space: pre-wrap; }
        .error { background: #450a0a; border: 1px solid #dc2626; color: #fca5a5; padding: 16px; border-radius: 8px; }
        .loading { text-align: center; padding: 40px; color: #94a3b8; }
        .trace-step { padding: 8px; margin-bottom: 4px; background: #0f172a; border-radius: 4px; }
        .trace-step-num { color: #38bdf8; font-weight: bold; }
        .trace-var { color: #7dd3fc; font-size: 0.85rem; }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>Python Code Visualizer</h1>
            <p>Paste your Python code and see how it executes</p>
        </header>
        <div class="main-grid">
            <div class="panel">
                <div class="panel-title">Python Code</div>
                <textarea id="codeEditor" spellcheck="false">x = 1
y = 2
print(x + y)</textarea>
                <button class="btn" id="analyzeBtn" onclick="analyzeCode()">Analyze</button>
            </div>
            <div class="panel">
                <div class="panel-title">Results</div>
                <div id="results">
                    <div class="loading"><p>Click Analyze to see results</p></div>
                </div>
            </div>
        </div>
    </div>
<script>
    let currentResult = null;
    let currentTab = 'explanation';
    
    function analyzeCode() {
        var btn = document.getElementById('analyzeBtn');
        var results = document.getElementById('results');
        var code = document.getElementById('codeEditor').value;
        
        btn.disabled = true;
        btn.innerHTML = 'Loading...';
        results.innerHTML = '<p>Loading...</p>';
        
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/api/v1/analyze', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                btn.disabled = false;
                btn.innerHTML = 'Analyze';
                
                if (xhr.status === 200) {
                    currentResult = JSON.parse(xhr.responseText);
                    showResults();
                } else {
                    results.innerHTML = '<p class="error">Error: ' + xhr.status + '</p>';
                }
            }
        };
        
        xhr.send(JSON.stringify({code: code}));
    }
    
    function showResults() {
        var results = document.getElementById('results');
        if (!currentResult) return;
        
        var html = '<div class="tabs">';
        html += '<button class="tab ' + (currentTab==='explanation'?'active':'') + '" onclick="currentTab=\'explanation\';showResults()">Explanation</button>';
        html += '<button class="tab ' + (currentTab==='trace'?'active':'') + '" onclick="currentTab=\'trace\';showResults()">Trace</button>';
        html += '<button class="tab ' + (currentTab==='flow'?'active':'') + '" onclick="currentTab=\'flow\';showResults()">Flow</button>';
        html += '<button class="tab ' + (currentTab==='improved'?'active':'') + '" onclick="currentTab=\'improved\';showResults()">Improved</button>';
        html += '</div>';
        
        if (currentTab === 'explanation') {
            html += '<div class="result-content">' + currentResult.explanation + '</div>';
        } else if (currentTab === 'trace') {
            html += '<div class="code-block">';
            if (currentResult.output && currentResult.output.length > 0) {
                html += 'Output: ' + currentResult.output.join(', ') + '\n\n';
            }
            if (currentResult.execution) {
                for (var i = 0; i < currentResult.execution.length; i++) {
                    var s = currentResult.execution[i];
                    html += 'Step ' + s.step + ': L' + s.line_number + ' ' + s.code;
                    if (s.variables && Object.keys(s.variables).length > 0) {
                        var vars = [];
                        for (var k in s.variables) {
                            vars.push(k + '=' + s.variables[k]);
                        }
                        html += '\n  variables: ' + vars.join(', ');
                    }
                    html += '\n';
                }
            }
            html += '</div>';
        } else if (currentTab === 'flow') {
            html += '<div class="result-content">' + (currentResult.flow ? currentResult.flow.join(' → ') : 'No flow') + '</div>';
        } else if (currentTab === 'improved') {
            html += '<pre class="code-block">' + currentResult.fixed_code + '</pre>';
        }
        
        results.innerHTML = html;
    }
    </script>
</body>
</html>'''

app = FastAPI(title="Python Code Visualizer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    code: str

def execute_code(code: str) -> dict:
    import sys
    output = []
    error = None
    steps = []
    step_counter = [0]
    
    def tracing(frame, event, arg):
        if event == 'line':
            filename = frame.f_code.co_filename
            if filename == '<string>':
                lineno = frame.f_lineno
                step_counter[0] += 1
                lines = frame.f_globals.get('_source_lines', [])
                code_line = lines[lineno - 1] if 0 <= lineno - 1 < len(lines) else f"Line {lineno}"
                local_vars = {}
                for k, v in frame.f_locals.items():
                    if not k.startswith('__') and k not in ['_source_lines']:
                        try:
                            local_vars[k] = repr(v)[:50]
                        except:
                            local_vars[k] = f"<{type(v).__name__}>"
                steps.append({'step': step_counter[0], 'line_number': lineno, 'code': code_line, 'variables': local_vars})
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
    if not api_key or api_key == 'your_openrouter_api_key_here':
        lines = [l for l in code.strip().split('\n') if l.strip()]
        return {
            'explanation': f"This Python code has {len(lines)} lines.\n\n" + '\n'.join([f"- Line {i+1}: {l}" for i, l in enumerate(lines)]),
            'fixed_code': f"# Improved version\n\n{code}",
            'flow': ['Start'] + [f'Step {i+1}' for i in range(len(lines))] + ['End'],
            'steps': [{'step': i+1, 'description': l.strip()} for i, l in enumerate(lines)],
            'key_points': ['Code executes line by line', 'Variables store values']
        }
    
    import json
    prompt = f"Analyze this Python code. Return JSON with: explanation, fixed_code, flow (array), steps (array), key_points (array).\n\nCode: {code[:500]}\nExecution: {str(execution_result.get('execution', []))[:500]}"
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
    return HTMLResponse(content=HTML_CONTENT, media_type="text/html")

@app.post("/api/v1/analyze")
async def analyze(request: AnalyzeRequest):
    exec_result = execute_code(request.code)
    ai_result = call_ai(request.code, exec_result, api_key)
    return JSONResponse(content={
        "explanation": ai_result.get('explanation', 'No explanation'),
        "fixed_code": ai_result.get('fixed_code', request.code),
        "execution": exec_result.get('execution', []),
        "output": exec_result.get('output', []),
        "flow": ai_result.get('flow', []),
        "steps": ai_result.get('steps', []),
        "key_points": ai_result.get('key_points', []),
        "error": exec_result.get('error')
    })

handler = app