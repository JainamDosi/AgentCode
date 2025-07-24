import { useState, useEffect, useRef } from 'react';
import Split from 'react-split';
import CodeEditor from './components/CodeEditor';
import Output from './components/Output';
import FileExplorer from './components/FileExplorer';
import AIChat from './components/AIChat';
import { LANGUAGE_VERSIONS, CODE_SNIPPETS } from './constants';
import axios from 'axios';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import './index.css'
const queryClient = new QueryClient();

// Map file extensions to language keys
const extensionToLanguage = {
  'py': 'python',
  'js': 'javascript',
  'jsx': 'javascript',
  'ts': 'typescript',
  'tsx': 'typescript',
  'java': 'java',
  'c': 'c',
  'cpp': 'cpp',
  'cs': 'csharp',
  'rb': 'ruby',
  'go': 'go',
  'rs': 'rust',
  'php': 'php',
  'swift': 'swift',
  'kt': 'kotlin',
  'scala': 'scala',
  'sh': 'bash',
  // Add more as needed
};

function detectLanguageFromFilename(filename) {
  const ext = filename.split('.').pop().toLowerCase();
  return extensionToLanguage[ext] || 'plaintext';
}

function App() {
  const [openFiles, setOpenFiles] = useState([]); // [{ path, name, code }]
  const [activeFile, setActiveFile] = useState(null); // path string
  const [code, setCode] = useState(''); // file content
  const [language, setLanguage] = useState('python');
  const [output, setOutput] = useState([]);
  const [cursorPosition, setCursorPosition] = useState({ line: 1, column: 1 });
  const [saveStatus, setSaveStatus] = useState(''); // '', 'saving', 'saved', 'error'
  const [refreshKey, setRefreshKey] = useState(0); // For file explorer refresh

  const openFilesRef = useRef(openFiles);
  useEffect(() => { openFilesRef.current = openFiles; }, [openFiles]);

  const MIN_SIDEBAR = 140;
  const MIN_CENTER = 280;
  const splitSizes = [16, 68, 16];

  const handleCodeChange = (val) => {
    setCode(val);
  };

  const handleLanguageChange = (newLang) => {
    if (!code.trim() || code === CODE_SNIPPETS[language]) {
      setCode(CODE_SNIPPETS[newLang] || '');
    }
    setLanguage(newLang);
  };

  const current = openFiles.find(f => f.path === activeFile);

  // --- Manual Save Function ---
  const handleManualSave = async () => {
    if (!current) return;
    setSaveStatus('saving');
    try {
      const res = await fetch('http://localhost:8000/fs/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: current.path, content: current.code }),
      });
      if (res.ok) {
        setSaveStatus('saved');
        setTimeout(() => setSaveStatus(''), 1200);
      } else {
        setSaveStatus('error');
      }
    } catch {
      setSaveStatus('error');
    }
  };

  // --- Keyboard Shortcut for Save (Ctrl+S / Cmd+S) ---
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        handleManualSave();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
    // eslint-disable-next-line
  }, [current]);

  const handleRun = async () => {
    if (!current) return;
    try {
      console.log('Running with:', { language, version: LANGUAGE_VERSIONS[language], code: current.code });
      const response = await axios.post('https://emkc.org/api/v2/piston/execute', {
        language: language,
        version: LANGUAGE_VERSIONS[language],
        files: [{ content: current.code }],
      });
      const result = response.data.run;
      setOutput((result.output || '').split('\n'));
    } catch (err) {
      setOutput([
        'Error running code:',
        err.message,
        err.response?.data ? JSON.stringify(err.response.data) : ''
      ]);
    }
  };

  const openFile = async (filePath, fileName) => {
    const existing = openFiles.find(f => f.path === filePath);
    if (existing) {
      setActiveFile(filePath);
      setLanguage(detectLanguageFromFilename(fileName));
      return;
    }
    const res = await fetch(`http://localhost:8000/fs/read?path=${encodeURIComponent(filePath)}`);
    const code = res.ok ? await res.text() : '// Error loading file';
    setOpenFiles(files => [...files, { path: filePath, name: fileName, code }]);
    setActiveFile(filePath);
    setLanguage(detectLanguageFromFilename(fileName));
  };

  useEffect(() => {
    if (current) {
      setLanguage(detectLanguageFromFilename(current.name));
    }
    // eslint-disable-next-line
  }, [current]);

  // --- Refresh File Explorer and Open Files ---
  const refreshFilesAndEditor = async () => {
    setRefreshKey(key => key + 1); // Refresh file explorer
    if (openFilesRef.current.length > 0) {
      const updatedFiles = await Promise.all(openFilesRef.current.map(async (f) => {
        const res = await fetch(`http://localhost:8000/fs/read?path=${encodeURIComponent(f.path)}`);
        const code = res.ok ? await res.text() : '// Error loading file';
        return { ...f, code };
      }));
      setOpenFiles(updatedFiles);
    }
  };

  // Example: Call this after /run-task completes
  // You can pass refreshFilesAndEditor to AIChat or wherever you run tasks

  return (
    <QueryClientProvider client={queryClient}>
    <div className="ide-root">
      <header className="ide-header">
        <span className="ide-header-logo">AgentCode <span className="ide-header-angle">&lt;/&gt;</span></span>
      </header>
      <Split
        className="ide-horizontal-split"
        sizes={splitSizes}
        minSize={[MIN_SIDEBAR, MIN_CENTER, MIN_SIDEBAR]}
        style={{ height: 'calc(100vh - 54px)', width: '100vw', display: 'flex' }}
        gutterSize={6}
      >
        <div className="ide-sidebar-left">
          <FileExplorer onFileOpen={openFile} refreshKey={refreshKey} />
        </div>
        <div className="ide-center">
            <div style={{ display: 'flex', background: '#23272f', borderBottom: '1px solid #222' }}>
              {openFiles.map(f => (
                <div
                  key={f.path}
                  style={{
                    padding: '6px 16px',
                    background: f.path === activeFile ? '#181a20' : 'transparent',
                    color: '#fff',
                    borderRight: '1px solid #222',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    height:'2rem'
                  }}
                  onClick={() => setActiveFile(f.path)}
                >
                  {f.name}
                  <span
                    style={{ marginLeft: 8, color: '#aaa', cursor: 'pointer' }}
                    onClick={e => {
                      e.stopPropagation();
                      setOpenFiles(files => files.filter(file => file.path !== f.path));
                      if (activeFile === f.path) {
                        const others = openFiles.filter(file => file.path !== f.path);
                        setActiveFile(others.length ? others[0].path : null);
                      }
                    }}
                  >
                    ×
                  </span>
                </div>
              ))}
            </div>
          <Split direction="vertical" sizes={[70, 30]} minSize={[120, 80]} className="ide-vertical-split" style={{ height: '100%' }}>
            <div className="ide-editor-pane">
              <div style={{ height: 18, marginBottom: 2 }}>
                {saveStatus === 'saving' && (
                  <span style={{ color: '#aaa', fontSize: 12 }}>Saving...</span>
                )}
                {saveStatus === 'saved' && (
                  <span style={{ color: '#4ade80', fontSize: 12 }}>Saved</span>
                )}
                {saveStatus === 'error' && (
                  <span style={{ color: '#f87171', fontSize: 12 }}>Save failed</span>
                )}
              </div>
              <div style={{ display: 'flex', gap: 8, marginBottom: 6 ,justifyContent:'flex-end'}}>
                <button
                  onClick={handleManualSave}
                  style={{
                    padding: '4px 16px',
                    background: '#23272f',
                    color: '#fff',
                    border: '1px solid #444',
                    borderRadius: 4,
                    cursor: current ? 'pointer' : 'not-allowed',
                    opacity: current ? 1 : 0.5
                  }}
                  disabled={!current}
                  title="Save (Ctrl+S)"
                >
                  Save
                </button>
                <button
                  onClick={handleRun}
                  style={{
                    padding: '4px 16px',
                    background: '#4ade80',
                    color: '#181a20',
                    border: 'none',
                    borderRadius: 4,
                    cursor: current ? 'pointer' : 'not-allowed',
                    opacity: current ? 1 : 0.5
                  }}
                  disabled={!current}
                  title="Run"
                >
                  Run
                </button>
              </div>
              <CodeEditor
                language={language}
                code={current ? current.code : ''}
                onLanguageChange={handleLanguageChange}
                onCodeChange={val => {
                  setOpenFiles(files =>
                    files.map(f =>
                      f.path === activeFile ? { ...f, code: val } : f
                    )
                  );
                }}
                onRun={handleRun}
                onCursorChange={setCursorPosition}
              >
                {Object.entries(LANGUAGE_VERSIONS).map(([key, version]) => (
                  <option key={key} value={key}>{key} ({version})</option>
                ))}
              </CodeEditor>
            </div>
            <div className="ide-output-pane">
              <hr style={{
                border: 0,
                borderTop: '1.5px solid #fff',
                margin: 0,
                marginBottom: 4,
                opacity: 0.5
              }} />
              <Output output={output} />
            </div>
          </Split>
        </div>
        <div className="ide-sidebar-right">
          <AIChat refreshFilesAndEditor={refreshFilesAndEditor} />
        </div>
      </Split>
      <footer className="ide-footer">
        <span className="ide-footer-text">Ln {cursorPosition.line}, Col {cursorPosition.column} &nbsp; | &nbsp; Spaces: 4 &nbsp; | &nbsp; UTF-8 &nbsp; | &nbsp; Powered by AgentCode</span>
      </footer>
    </div>
    </QueryClientProvider>
  );
}

export default App;