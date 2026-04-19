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

# Embedded HTML - simpler than reading from file
HTML_CONTENT = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python Code Visualizer</title>
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs/loader.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; padding: 30px 0; border-bottom: 1px solid #1e293b; margin-bottom: 30px; }
        .header h1 { font-size: 2.5rem; color: #38bdf8; margin-bottom: 10px; }
        .header p { color: #94a3b8; font-size: 1.1rem; }
        .main-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
        @media (max-width: 1024px) { .main-grid { grid-template-columns: 1fr; } }
        .panel { background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }
        .panel-title { font-size: 1.1rem; font-weight: 600; color: #f1f5f9; margin-bottom: 16px; }
        .editor-container { height: 400px; border-radius: 8px; overflow: hidden; border: 1px solid #334155; }
        .analyze-btn { width: 100%; padding: 16px; font-size: 1.1rem; font-weight: 600; background: linear-gradient(135deg, #0ea5e9, #3b82f6); color: white; border: none; border-radius: 8px; cursor: pointer; margin-top: 16px; }
        .analyze-btn:hover { transform: translateY(-2px); }
        .analyze-btn:disabled { opacity: 0.5; }
        .result-panel { background: #1e293b; border-radius: 12px; padding: 20px; margin-top: 20px; border: 1px solid #334155; }
        .result-title { font-size: 1.2rem; font-weight: 600; color: #38bdf8; margin-bottom: 12px; }
        .result-content { color: #cbd5e1; line-height: 1.7; }
        .code-block { background: #0f172a; padding: 16px; border-radius: 8px; font-family: monospace; font-size: 0.9rem; overflow-x: auto; color: #a5b4fc; }
        .tabs { display: flex; gap: 8px; margin-bottom: 16px; border-bottom: 1px solid #334155; padding-bottom: 8px; }
        .tab { padding: 8px 16px; background: transparent; border: none; color: #94a3b8; cursor: pointer; border-radius: 6px; font-size: 0.9rem; }
        .tab.active { background: #334155; color: #38bdf8; }
        .error-display { background: #450a0a; border: 1px solid #dc2626; color: #fca5a5; padding: 16px; border-radius: 8px; }
        .loading { text-align: center; padding: 40px; color: #94a3b8; }
    </style>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        import { useState, useEffect, useRef } = React;
        const App = () => {
            const [code, setCode] = useState("x = 1\\ny = 2\\nprint(x + y)");
            const [loading, setLoading] = useState(false);
            const [result, setResult] = useState(null);
            const [error, setError] = useState(null);
            const [activeTab, setActiveTab] = useState("explanation");
            const editorRef = useRef(null);
            
            useEffect(() => {
                require.config({ paths: { vs: "https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs" } });
                require(["vs/editor/editor.main"], function() {
                    if (!editorRef.current) {
                        editorRef.current = monaco.editor.create(document.getElementById("editor"), {
                            value: code, language: "python", theme: "vs-dark", fontSize: 14, minimap: { enabled: false },
                            automaticLayout: true, wordWrap: "on"
                        });
                        editorRef.current.onDidChangeModelContent(() => setCode(editorRef.current.getValue()));
                    }
                });
            }, []);
            
            const analyzeCode = async () => {
                setLoading(true); setError(null); setResult(null);
                try {
                    const res = await fetch("/api/v1/analyze", {
                        method: "POST", headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ code })
                    });
                    if (!res.ok) throw new Error("Failed");
                    setResult(await res.json());
                } catch (e) { setError(e.message); }
                finally { setLoading(false); }
            };
            
            return (
                <div className="container">
                    <header className="header"><h1>Python Code Visualizer</h1><p>Paste your Python code and see how it executes</p></header>
                    <div className="main-grid">
                        <div className="panel">
                            <div className="panel-title">Python Code</div>
                            <div className="editor-container" id="editor"></div>
                            <button className="analyze-btn" onClick={analyzeCode} disabled={loading}>
                                {loading ? "Analyzing..." : "Analyze"}
                            </button>
                        </div>
                        <div className="panel">
                            <div className="panel-title">Results</div>
                            {!result && !error && !loading && <div className="loading"><p>Click Analyze to see results</p></div>}
                            {loading && <div className="loading"><p>Loading...</p></div>}
                            {error && <div className="error-display">{error}</div>}
                            {result && (
                                <div>
                                    <div className="tabs">
                                        <button className={"tab " + (activeTab==="explanation"?"active":"")} onClick={()=>setActiveTab("explanation")}>Explanation</button>
                                        <button className={"tab " + (activeTab==="trace"?"active":"")} onClick={()=>setActiveTab("trace")}>Trace</button>
                                        <button className={"tab " + (activeTab==="flow"?"active":"")} onClick={()=>setActiveTab("flow")}>Flow</button>
                                        <button className={"tab " + (activeTab==="improved"?"active":"")} onClick={()=>setActiveTab("improved")}>Improved</button>
                                    </div>
                                    {activeTab==="explanation" && <div className="result-content">{result.explanation}</div>}
                                    {activeTab==="trace" && <div className="result-panel">
                                        <pre style={{background:'#0f172a', padding:10, borderRadius:4, overflow:'auto'}}>
Output: {result.output ? result.output.join(', ') : 'none'}

{result.execution.map(function(s) { return 'Step ' + s.step + ': L' + s.line_number + ' ' + s.code + '\n'; }).join('')}
                                        </pre>
                                    </div>}</div>}
                                    {activeTab==="flow" && <div className="result-content">{result.flow?.join(" → ")}</div>}
                                    {activeTab==="improved" && <pre className="code-block">{result.fixed_code}</pre>}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            );
        }
        ReactDOM.createRoot(document.getElementById("root")).render(<App/>);
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
    """Execute Python code with tracing"""
    import sys
    
    output = []
    error = None
    steps = []
    step_counter = [0]  # Use list to allow modification in closure
    
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
    """Serve the HTML frontend"""
    return HTMLResponse(content=HTML_CONTENT, media_type="text/html")


@app.get("/index.html")
async def index_html():
    """Serve index.html"""
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