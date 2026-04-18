import React, { useState } from 'react'
import CodeEditor from './components/CodeEditor'
import ExecutionTrace from './components/ExecutionTrace'
import FlowDiagram from './components/FlowDiagram'
import ExplanationPanel from './components/ExplanationPanel'

function App() {
  const [code, setCode] = useState(`# Try your Python code here!
# Example: Calculate factorial

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

result = factorial(5)
print(f"Factorial of 5 is: {result}")`)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('explanation')

  const analyzeCode = async () => {
    setLoading(true)
    setError(null)
    setResult(null)
    
    try {
      const response = await fetch('/api/v1/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      })
      
      if (!response.ok) {
        throw new Error('Analysis failed')
      }
      
      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <header className="header">
        <h1>🤖 AI Python Visualizer</h1>
        <p>Paste your Python code and see how it executes step-by-step</p>
      </header>

      <div className="main-grid">
        <div className="panel">
          <div className="panel-header">
            <span className="panel-title">📝 Python Code</span>
          </div>
          <div className="editor-container">
            <CodeEditor value={code} onChange={setCode} />
          </div>
          <button 
            className="analyze-btn" 
            onClick={analyzeCode}
            disabled={loading}
          >
            {loading ? 'Analyzing...' : '🚀 Analyze & Visualize'}
          </button>
        </div>

        <div className="panel">
          <div className="panel-header">
            <span className="panel-title">🎯 Visualization</span>
          </div>
          
          {!result && !error && !loading && (
            <div className="loading">
              <p>Click "Analyze" to see your code's execution flow</p>
            </div>
          )}

          {loading && (
            <div className="loading">
              <div className="loading-spinner"></div>
              <p>Executing and analyzing your code...</p>
            </div>
          )}

          {error && (
            <div className="error-display">
              <div className="error-title">❌ Error</div>
              <p>{error}</p>
            </div>
          )}

          {result && (
            <div className="results-section">
              <div className="tabs">
                <button 
                  className={`tab ${activeTab === 'explanation' ? 'active' : ''}`}
                  onClick={() => setActiveTab('explanation')}
                >
                  📖 Explanation
                </button>
                <button 
                  className={`tab ${activeTab === 'trace' ? 'active' : ''}`}
                  onClick={() => setActiveTab('trace')}
                >
                  👣 Execution Trace
                </button>
                <button 
                  className={`tab ${activeTab === 'flow' ? 'active' : ''}`}
                  onClick={() => setActiveTab('flow')}
                >
                  🔀 Flow
                </button>
                <button 
                  className={`tab ${activeTab === 'improved' ? 'active' : ''}`}
                  onClick={() => setActiveTab('improved')}
                >
                  ✨ Improved
                </button>
              </div>

              {activeTab === 'explanation' && (
                <ExplanationPanel explanation={result.explanation} />
              )}

              {activeTab === 'trace' && (
                <ExecutionTrace 
                  execution={result.execution} 
                  output={result.output}
                  error={result.error}
                />
              )}

              {activeTab === 'flow' && (
                <FlowDiagram 
                  flow={result.flow} 
                  steps={result.steps}
                  keyPoints={result.key_points}
                />
              )}

              {activeTab === 'improved' && (
                <div className="result-panel">
                  <div className="result-title">✨ Improved Code</div>
                  <pre className="code-block">{result.fixed_code}</pre>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App