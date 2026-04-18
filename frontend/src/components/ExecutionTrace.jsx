import React from 'react'

function ExecutionTrace({ execution = [], output = [], error = null }) {
  if (error) {
    return (
      <div className="result-panel">
        <div className="result-title">❌ Execution Error</div>
        <div className="error-display">
          <p>{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="result-panel">
      <div className="result-title">👣 Step-by-Step Execution</div>
      
      {output.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <div style={{ marginBottom: 8, color: '#94a3b8', fontSize: '0.9rem' }}>📤 Output:</div>
          <div className="output-display">
            {output.map((line, i) => (
              <div key={i}>{line}</div>
            ))}
          </div>
        </div>
      )}

      {execution.length === 0 ? (
        <p style={{ color: '#94a3b8' }}>No execution steps captured</p>
      ) : (
        <div className="execution-trace">
          {execution.map((step, index) => (
            <div key={index} className="trace-step">
              <div className="trace-line">L{step.line_number}</div>
              <div>
                <div className="trace-code">{step.code}</div>
                {step.variables && Object.keys(step.variables).length > 0 && (
                  <div className="trace-variables">
                    {Object.entries(step.variables).map(([key, value]) => (
                      <span key={key} className="variable-tag">
                        {key} = {JSON.stringify(value)}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ExecutionTrace