import { useEffect, useRef } from 'react';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import 'xterm/css/xterm.css';

const Output = ({ output }) => {
  const terminalRef = useRef(null);
  const fitAddon = useRef(new FitAddon());
  const term = useRef(null);

  useEffect(() => {
    if (!term.current) {
      term.current = new Terminal({
        fontSize: 14,
        theme: { background: '#1e1e1e' },
        // Remove rows: 15, so it auto-fits
      });
      term.current.loadAddon(fitAddon.current);
      term.current.open(terminalRef.current);
      fitAddon.current.fit();
    }
    term.current.clear();
    if (output && output.length) {
      output.forEach(line => term.current.writeln(line));
    }
    fitAddon.current.fit();
  }, [output]);

  return (
    <div style={{ height: '100%', width: '100%', display: 'flex', flex: 1, minHeight: 0, background: '#1e1e1e' }}>
      <div ref={terminalRef} style={{ height: '100%', width: '100%' }} />
    </div>
  );
};

export default Output;