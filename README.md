# AI Python Code Visualizer & Debug Mentor

A web-based AI tool that explains, improves, and visualizes Python code execution in real-time. Perfect for beginners learning Python!

## 🌟 Features

- **Beginner-Friendly Explanations** - AI-powered explanations in simple language
- **Real Execution Tracing** - Watch your code execute line-by-line with variable states
- **Improved Code** - Get suggestions for better, cleaner Python code
- **Visual Flow Diagrams** - See the logical flow of your code
- **Error Detection** - Understand and fix errors with AI help

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│   React Front   │────▶│   FastAPI       │────▶│  AI Service      │
│   (Port 5173)   │     │   (Port 8000)   │     │  (OpenRouter)    │
└─────────────────┘     └─────────────────┘     └──────────────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ Execution Engine │
                     │  (sys.settrace)  │
                     └──────────────────┘
```

## 📁 Project Structure

```
ai-python-visualizer/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── routes/
│   │   └── analyze.py       # API endpoints
│   ├── services/
│   │   └── ai_service.py   # OpenRouter integration
│   ├── execution/
│   │   └── tracer.py        # Real Python execution
│   ├── prompts/
│   │   └── templates.py     # AI prompt templates
│   └── models/
│       └── schemas.py       # Pydantic models
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   ├── components/      # UI components
│   │   └── index.css       # Styling
│   └── package.json
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- OpenRouter API key

### 1. Clone & Setup

```bash
cd ai-python-visualizer
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "OPENROUTER_API_KEY=your_api_key_here" > .env
```

Get your free API key from: https://openrouter.ai/

### 3. Start Backend

```bash
cd backend
python main.py
# Server runs on http://localhost:8000
```

### 4. Frontend Setup (new terminal)

```bash
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:5173
```

### 5. Open Browser

Navigate to **http://localhost:5173** and start coding!

## 💻 Usage

1. **Paste Python code** in the code editor
2. Click **"Analyze & Visualize"** button
3. View results in tabs:
   - 📖 **Explanation** - AI explanation of what your code does
   - 👣 **Execution Trace** - Step-by-step variable changes
   - 🔀 **Flow** - Visual flow diagram
   - ✨ **Improved** - Better version of your code

## 🔧 How It Works

### Execution Engine (`tracer.py`)

The tracer uses Python's `sys.settrace` to:
1. Execute code line-by-line
2. Capture variable states at each step
3. Collect print outputs
4. Handle errors gracefully

Security measures:
- Sandboxed globals (restricted builtins)
- 5-second timeout
- Blocked dangerous functions (open, eval, exec)
- Line count limit (1000 lines max)

### AI Service (`ai_service.py`)

Uses OpenRouter API with Claude 3 Haiku model:
1. **Explanation** - Converts code + execution trace into simple English
2. **Improvement** - Suggests better patterns and fixes errors
3. **Visualization** - Generates flow nodes and step descriptions

### API Endpoint

```
POST /api/v1/analyze

Request:
{
  "code": "print('Hello')"
}

Response:
{
  "explanation": "...",
  "fixed_code": "...",
  "execution": [{"line_number": 1, "code": "...", "variables": {...}}],
  "flow": ["Start", "Print", "End"],
  "steps": [{"step": 1, "description": "...", "variables_changed": []}],
  "key_points": [...],
  "output": ["Hello"],
  "error": null
}
```

## 🛡️ Security

| Risk | Mitigation |
|------|------------|
| File operations | Disabled `open`, `os.remove`, `shutil` |
| System commands | Blocked `subprocess`, `eval`, `exec` |
| Network calls | Disabled `urllib`, `requests` |
| Infinite loops | 5s timeout + 1000 line limit |

**Note:** This is basic sandboxing. For production, use Docker containerization.

## 🔨 Future Improvements

- [ ] Docker-based execution for true sandboxing
- [ ] Support for matplotlib visualization output
- [ ] Syntax error highlighting in editor
- [ ] Multiple AI model options (Ollama, Claude, GPT-4)
- [ ] Save/share code snippets
- [ ] Unit test generation
- [ ] Code complexity analysis
- [ ] Syntax highlighting improvements

## 📝 Example Inputs

### Example 1: Basic Loop

```python
# Calculate sum of numbers 1 to 5
total = 0
for i in range(1, 6):
    total = total + i
print(total)
```

**Output:**
- Explanation: Explains what a loop is
- Trace: Shows each iteration with `total` changing
- Flow: "Initialize → Loop → Add → Print → End"

### Example 2: Function

```python
def greet(name):
    return f"Hello, {name}!"

message = greet("Python")
print(message)
```

**Output:**
- Explanation: What functions are, parameters vs arguments
- Trace: Function call, parameter assignment, return value

### Example 3: Error Handling

```python
numbers = [1, 2, 3]
print(numbers[5])
```

**Output:**
- Explanation: What IndexError means
- Fixed code with try/except or bounds checking

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License

---

Built with ❤️ for Python learners everywhere!