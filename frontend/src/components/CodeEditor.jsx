/* === CodeEditor.jsx === */
import Editor from '@monaco-editor/react';
import { useRef } from 'react';

export default function CodeEditor({ language, code, onCodeChange, onRun, children, onCursorChange }) {
  const editorRef = useRef(null);

  return (
    <div style={{ height: '100%', width: '100%', display: 'flex', flexDirection: 'column', position: 'relative' }}>
      {/* Toolbar with Run button removed */}
      <div style={{ flex: 1, height: 0, width: '100%', position: 'relative' }}>
        <Editor
          height="100%"
          width="100%"
          language={language}
          theme="vs-dark"
          value={code}
          onChange={onCodeChange}
          onMount={(editor) => {
            editorRef.current = editor;
            setTimeout(() => editor.layout(), 50);
            // Listen for cursor changes
            editor.onDidChangeCursorPosition(() => {
              const pos = editor.getPosition();
              onCursorChange && onCursorChange({ line: pos.lineNumber, column: pos.column });
            });
            // Set initial position
            const pos = editor.getPosition();
            onCursorChange && onCursorChange({ line: pos.lineNumber, column: pos.column });
          }}
          options={{ fontSize: 14, minimap: { enabled: false } }}
        />
      </div>
    </div>
  );
}
