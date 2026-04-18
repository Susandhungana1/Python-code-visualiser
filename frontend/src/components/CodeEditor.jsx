import React from 'react'
import Editor from '@monaco-editor/react'

function CodeEditor({ value, onChange }) {
  return (
    <Editor
      height="100%"
      defaultLanguage="python"
      value={value}
      onChange={onChange}
      theme="vs-dark"
      options={{
        minimap: { enabled: false },
        fontSize: 14,
        lineNumbers: 'on',
        scrollBeyondLastLine: false,
        automaticLayout: true,
        tabSize: 4,
        wordWrap: 'on',
        padding: { top: 16 }
      }}
    />
  )
}

export default CodeEditor