import React from 'react'

function FlowDiagram({ flow = [], steps = [], keyPoints = [] }) {
  return (
    <div className="result-panel">
      <div className="result-title">🔀 Execution Flow</div>
      
      {flow.length > 0 && (
        <div style={{ marginBottom: 20 }}>
          <div style={{ marginBottom: 12, color: '#94a3b8', fontSize: '0.9rem' }}>Flow:</div>
          <div className="flow-diagram">
            {flow.map((item, index) => (
              <React.Fragment key={index}>
                <div className="flow-node">{item}</div>
                {index < flow.length - 1 && <span className="flow-arrow">→</span>}
              </React.Fragment>
            ))}
          </div>
        </div>
      )}

      {steps.length > 0 && (
        <div style={{ marginBottom: 20 }}>
          <div style={{ marginBottom: 12, color: '#94a3b8', fontSize: '0.9rem' }}>Detailed Steps:</div>
          <div className="execution-trace">
            {steps.map((step, index) => (
              <div key={index} className="trace-step">
                <div className="trace-line">{step.step}</div>
                <div>
                  <div className="trace-code">{step.description}</div>
                  {step.variables_changed && step.variables_changed.length > 0 && (
                    <div className="trace-variables">
                      {step.variables_changed.map((v, i) => (
                        <span key={i} className="variable-tag">{v}</span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {keyPoints.length > 0 && (
        <div>
          <div style={{ marginBottom: 12, color: '#94a3b8', fontSize: '0.9rem' }}>🎯 Key Learning Points:</div>
          <div className="key-points">
            {keyPoints.map((point, index) => (
              <span key={index} className="key-point">{point}</span>
            ))}
          </div>
        </div>
      )}

      {flow.length === 0 && steps.length === 0 && keyPoints.length === 0 && (
        <p style={{ color: '#94a3b8' }}>No flow visualization available</p>
      )}
    </div>
  )
}

export default FlowDiagram