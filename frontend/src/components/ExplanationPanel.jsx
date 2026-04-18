import React from 'react'

function ExplanationPanel({ explanation = '' }) {
  if (!explanation) {
    return (
      <div className="result-panel">
        <div className="result-title">📖 Explanation</div>
        <p style={{ color: '#94a3b8' }}>No explanation available</p>
      </div>
    )
  }

  const paragraphs = explanation.split('\n\n').filter(p => p.trim())

  return (
    <div className="result-panel">
      <div className="result-title">📖 AI Explanation</div>
      <div className="result-content">
        {paragraphs.map((para, index) => (
          <p key={index} style={{ marginBottom: 16 }}>
            {para}
          </p>
        ))}
      </div>
    </div>
  )
}

export default ExplanationPanel