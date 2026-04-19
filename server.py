#!/usr/bin/env python3
"""Python Code Visualizer Server"""
import os
import json
import httpx
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = int(os.environ.get('PORT', 8000))
API_KEY = os.environ.get('OPENROUTER_API_KEY', '')

HTML = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Python Code Visualizer</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh}
.container{max-width:1200px;margin:0 auto;padding:20px}
.header{text-align:center;padding:30px 0;border-bottom:1px solid #1e293b}
.header h1{font-size:2rem;color:#38bdf8;margin-bottom:10px}
.header p{color:#94a3b8}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}
@media(max-width:768px){.grid{grid-template-columns:1fr}}
.panel{background:#1e293b;border-radius:12px;padding:20px}
.panel h2{color:#f1f5f9;font-size:1.1rem;margin-bottom:16px}
textarea{width:100%;height:350px;background:#0f172a;color:#e2e8f0;border:1px solid #334155;border-radius:8px;padding:12px;font-family:monospace;font-size:14px}
.btn{width:100%;padding:14px;background:#0ea5e9;color:white;border:none;border-radius:8px;font-size:1rem;cursor:pointer;margin-top:12px}
.btn:hover{background:#0284c7}
.tabs{display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap}
.tab{padding:8px 14px;background:transparent;border:none;color:#94a3b8;cursor:pointer;border-radius:6px}
.tab.active{background:#334155;color:#38bdf8}
.result{color:#cbd5e1;line-height:1.7;white-space:pre-wrap}
.code-block{background:#0f172a;padding:12px;border-radius:8px;font-family:monospace;font-size:0.85rem;color:#a5b4fc;white-space:pre-wrap}
.error{background:#450a0a;border:1px solid #dc2626;color:#fca5a5;padding:12px;border-radius:8px}
.loading{text-align:center;padding:40px;color:#94a3b8}
</style>
</head>
<body>
<div class="container">
<header class="header">
<h1>Python Code Visualizer</h1>
<p>See how your Python code executes step by step</p>
</header>
<div class="grid">
<div class="panel">
<h2>Python Code</h2>
<textarea id="code">x = 1
y = 2
print(x + y)</textarea>
<button class="btn" id="btn" onclick="runAnalyze()">Analyze</button>
</div>
<div class="panel">
<h2>Results</h2>
<div id="results"><p style="color:#94a3b8">Click Analyze to see results</p></div>
</div>
</div>
</div>
<script>
var currentTab = 'explanation';
var resultData = null;

function runAnalyze() {
    var btn = document.getElementById('btn');
    var results = document.getElementById('results');
    var code = document.getElementById('code').value;
    btn.disabled = true;
    btn.textContent = 'Analyzing...';
    results.innerHTML = '<p class="loading">Loading...</p>';
    
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/v1/analyze', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    
    xhr.onload = function() {
        btn.disabled = false;
        btn.textContent = 'Analyze';
        if (xhr.status === 200) {
            try {
                resultData = JSON.parse(xhr.responseText);
                renderResults();
            } catch(e) {
                results.innerHTML = '<p class="error">Parse error: ' + e.message + '</p>';
            }
        } else {
            results.innerHTML = '<p class="error">Error: ' + xhr.status + '</p>';
        }
    };
    
    xhr.onerror = function() {
        btn.disabled = false;
        btn.textContent = 'Analyze';
        results.innerHTML = '<p class="error">Connection error</p>';
    };
    
    xhr.send(JSON.stringify({code: code}));
}

function renderResults() {
    var results = document.getElementById('results');
    if (!resultData) return;
    
    var html = '<div class="tabs">';
    var tabs = ['explanation', 'trace', 'flow', 'improved'];
    for (var i = 0; i < tabs.length; i++) {
        var t = tabs[i];
        var active = currentTab === t ? 'active' : '';
        html += '<button class="tab ' + active + '" data-tab="' + t + '">' + t.charAt(0).toUpperCase() + t.slice(1) + '</button>';
    }
    html += '</div>';
    
    // Add click handlers for tabs
    setTimeout(function() {
        var tabButtons = document.querySelectorAll('.tab');
        for (var j = 0; j < tabButtons.length; j++) {
            tabButtons[j].onclick = function() {
                currentTab = this.getAttribute('data-tab');
                renderResults();
            };
        }
    }, 0);
    
    if (currentTab === 'explanation') {
        html += '<div class="result">' + (resultData.explanation || 'No explanation') + '</div>';
    } else if (currentTab === 'trace') {
        html += '<div class="code-block">';
        if (resultData.output && resultData.output.length) {
            html += 'Output: ' + resultData.output.join(', ');
            html += '<br><br>';
        }
        if (resultData.execution) {
            for (var j = 0; j < resultData.execution.length; j++) {
                var s = resultData.execution[j];
                html += 'Step ' + s.step + ': L' + s.line_number + ' ' + s.code;
                if (s.variables) {
                    var vs = [];
                    for (var k in s.variables) {
                        vs.push(k + '=' + s.variables[k]);
                    }
                    if (vs.length) html += '<br>  => ' + vs.join(', ');
                }
                html += '<br>';
            }
        }
        html += '</div>';
    } else if (currentTab === 'flow') {
        html += '<div class="result">' + (resultData.flow ? resultData.flow.join(' -> ') : 'No flow') + '</div>';
    } else if (currentTab === 'improved') {
        html += '<pre class="code-block">' + resultData.fixed_code + '</pre>';
    }
    
    results.innerHTML = html;
}
</script>
</body>
</html>'''

def execute_code(code):
    import sys
    output, steps, step_counter = [], [], [0]
    
    def tracing(frame, event, arg):
        if event == 'line' and frame.f_code.co_filename == '<string>':
            step_counter[0] += 1
            lines = frame.f_globals.get('_source_lines', [])
            lineno = frame.f_lineno
            code_line = lines[lineno - 1] if 0 <= lineno - 1 < len(lines) else 'Line ' + str(lineno)
            local_vars = {k: repr(v)[:50] for k, v in frame.f_locals.items() if not k.startswith('__') and k != '_source_lines'}
            steps.append({'step': step_counter[0], 'line_number': lineno, 'code': code_line, 'variables': local_vars})
        return tracing
    
    safe_globals = {'__builtins__': {
        'print': lambda *a: output.append(' '.join(str(x) for x in a)),
        'len': len, 'range': range, 'str': str, 'int': int, 'float': float, 'bool': bool, 'list': list,
        'dict': dict, 'tuple': tuple, 'set': set, 'abs': abs, 'min': min, 'max': max, 'sum': sum,
        'sorted': sorted, 'enumerate': enumerate, 'zip': zip, 'map': map, 'filter': filter, 'type': type,
        'isinstance': isinstance, 'input': lambda *a: 'blocked', 'open': lambda *a: 'blocked',
        'eval': lambda *a: 'blocked', 'exec': lambda *a: 'blocked'
    }, '_source_lines': code.split('\n')}
    
    try:
        old = sys.gettrace()
        sys.settrace(tracing)
        exec(compile(code, '<string>', 'exec'), safe_globals)
        sys.settrace(old)
    except Exception as e:
        return {'execution': steps, 'output': output, 'error': str(e)}
    
    return {'execution': steps, 'output': output, 'error': None}

def call_ai(code, result):
    if not API_KEY or len(API_KEY) < 20:
        lines = [l for l in code.strip().split('\n') if l.strip()]
        return {'explanation': 'Code has ' + str(len(lines)) + ' lines.\n\n' + '\n'.join('- ' + l for l in lines),
                'fixed_code': code, 'flow': ['Start'] + ['Step ' + str(i+1) for i in range(len(lines))] + ['End'],
                'key_points': ['Lines execute in order', 'Variables store values']}
    
    prompt = 'Explain this Python code. Return JSON: explanation, fixed_code, flow=[], key_points=[]\nCode: ' + code[:500]
    try:
        r = httpx.post('https://openrouter.ai/api/v1/chat/completions',
            headers={'Authorization': 'Bearer ' + API_KEY, 'Content-Type': 'application/json'},
            json={'model': 'openrouter/auto', 'messages': [
                {'role': 'system', 'content': 'Python tutor. Return valid JSON.'},
                {'role': 'user', 'content': prompt}
            ], 'temperature': 0.7, 'max_tokens': 2000}, timeout=30)
        return json.loads(r.json()['choices'][0]['message']['content'])
    except Exception as e:
        return {'explanation': str(e), 'fixed_code': code, 'flow': [], 'key_points': []}

class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/v1/analyze':
            length = int(self.headers['Content-Length'])
            body = self.rfile.read(length).decode('utf-8')
            code = json.loads(body).get('code', '')
            
            exec_result = execute_code(code)
            ai_result = call_ai(code, exec_result)
            
            response = json.dumps({
                'explanation': ai_result.get('explanation', 'No explanation'),
                'fixed_code': ai_result.get('fixed_code', code),
                'execution': exec_result.get('execution', []),
                'output': exec_result.get('output', []),
                'flow': ai_result.get('flow', []),
                'key_points': ai_result.get('key_points', []),
                'error': exec_result.get('error')
            })
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response.encode())
        else:
            self.send_error(404)
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode())
        else:
            self.send_error(404)

print('Starting server on http://localhost:' + str(PORT))
HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()