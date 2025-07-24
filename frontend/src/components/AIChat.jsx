import { useState, useRef, useEffect } from 'react';
import { sendMessageToBackend } from '../api';

export default function AIChat({ refreshFilesAndEditor }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [executingTaskId, setExecutingTaskId] = useState(null);
  const [executedTaskIds, setExecutedTaskIds] = useState([]);

  const messagesEndRef = useRef(null);

  // Function to reset conversation
  const handleReset = async () => {
    setResetting(true);
    try {
      await fetch('http://localhost:8000/reset', { method: 'POST' });
      setMessages([]);
      setExecutedTaskIds([]); // Reset executed tasks on conversation reset
    } catch (err) {
      // Optionally show error
    } finally {
      setResetting(false);
    }
  };

  // Ensure every task has a unique id
  const ensureTaskId = (task) => {
    if (typeof task === "string") {
      return { text: task, id: Date.now() + Math.random() };
    }
    if (!task.id) {
      return { ...task, id: Date.now() + Math.random() };
    }
    return task;
  };

  const handleExecuteWork = async (task) => {
    console.log("task",task);
    const taskWithId = ensureTaskId(task);
    setExecutingTaskId(taskWithId.id);
    try {
      const response = await fetch("http://localhost:8000/run-task", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task: task }),
      });
      const data = await response.json();
      setMessages((msgs) => [
        ...msgs,
        { sender: "system", text: "Task executed. Result: " + JSON.stringify(data) },
      ]);
      // Refresh file explorer and open files after task execution
      if (typeof refreshFilesAndEditor === "function") {
        await refreshFilesAndEditor();
      }
      setExecutedTaskIds(ids => [...ids, taskWithId.id]);
    } catch (err) {
      setMessages((msgs) => [
        ...msgs,
        { sender: "system", text: "Task execution failed: " + err.message },
      ]);
    } finally {
      setExecutingTaskId(null);
    }
  };

  const handleSend = async () => {
    if (input.trim() === '' || loading) return;
    const userMsg = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const botReplyObj = await sendMessageToBackend(input);
      let botReply;
      if (typeof botReplyObj === "string") {
        try {
          botReply = JSON.parse(botReplyObj);
        } catch {
          botReply = { reply: botReplyObj };
        }
      } else {
        botReply = botReplyObj;
      }

      // Always assign a new unique id to every new task
      if (botReply && botReply.task) {
        botReply.task = ensureTaskId(botReply.task);
      }

      const botMsg = {
        sender: 'bot',
        ...botReply,
        text: botReply.reply
      };

      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'bot', text: "Error: Could not reach backend." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleInputKeyDown = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const Spinner = () => (
    <span style={{
      width: 16,
      height: 16,
      border: '2px solid #181a20',
      borderTop: '2px solid #4ade80',
      borderRadius: '50%',
      display: 'inline-block',
      marginRight: 6,
      animation: 'spin 1s linear infinite'
    }}>
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg);}
            100% { transform: rotate(360deg);}
          }
        `}
      </style>
    </span>
  );

  return (
    <div style={{ height: '100%', width: '100%', background: '#181c23', color: '#fff', display: 'flex', flexDirection: 'column', padding: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
        <h3 style={{ margin: 0, fontSize: 16 }}>AgentCode🤖</h3>
        <button
          onClick={handleReset}
          disabled={resetting}
          style={{
            background: '#23272f',
            color: '#fff',
            border: '1px solid #333',
            borderRadius: 6,
            padding: '4px 12px',
            fontSize: 13,
            cursor: resetting ? 'not-allowed' : 'pointer',
            marginLeft: 8
          }}
        >
          {resetting ? 'Resetting...' : 'Reset Conversation'}
        </button>
      </div>
      <div style={{ flex: 1, overflowY: 'auto', margin: '12px 0', paddingRight: 4 }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{ marginBottom: 8, textAlign: msg.sender === 'user' ? 'right' : 'left' }}>
            <span style={{ background: msg.sender === 'user' ? '#2563eb' : '#23272f', color: '#fff', borderRadius: 8, padding: '6px 12px', display: 'inline-block', maxWidth: '80%' }}>
              {msg.reply || msg.text}
            </span>
            {msg.show_execute_button === true && msg.task && (
              <button
                style={{
                  marginTop: 6,
                  marginLeft: msg.sender === 'user' ? 0 : 8,
                  padding: '6px 18px',
                  borderRadius: '6px',
                  background: executingTaskId === msg.task.id ? '#a3e635' : '#4ade80',
                  color: '#181a20',
                  border: 'none',
                  fontWeight: 600,
                  fontSize: 15,
                  cursor: executingTaskId === msg.task.id || executedTaskIds.includes(msg.task.id) ? 'not-allowed' : 'pointer',
                  boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
                  transition: 'background 0.2s, color 0.2s'
                }}
                disabled={executingTaskId === msg.task.id || executedTaskIds.includes(msg.task.id)}
                onClick={() => handleExecuteWork(msg.task)}
              >
                {executingTaskId === msg.task.id ? (
                  <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Spinner />
                    Executing...
                  </span>
                ) : (
                  executedTaskIds.includes(msg.task.id) ? "Executed" : "Execute Work"
                )}
              </button>
            )}
            {msg.task && <span style={{ fontSize: 12, color: '#888', marginLeft: msg.sender === 'user' ? 0 : 8 }}>Task ID: {msg.task.id}</span>}
            {msg.task && <span style={{ fontSize: 12, color: '#888', marginLeft: msg.sender === 'user' ? 0 : 8 }}>Task Text: {msg.task.text}</span>}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div style={{ display: 'flex', gap: 8 }}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleInputKeyDown}
          placeholder="Type your message..."
          style={{ flex: 1, padding: '8px 12px', borderRadius: 6, border: '1px solid #333', background: '#23272f', color: '#fff', outline: 'none' }}
          disabled={loading}
        />
        <button
          onClick={handleSend}
          style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 6, padding: '8px 18px', fontWeight: 500, fontSize: 15, cursor: loading ? 'not-allowed' : 'pointer', transition: 'background 0.2s' }}
          disabled={loading}
          onMouseOver={e => (e.currentTarget.style.background = '#1d4ed8')}
          onMouseOut={e => (e.currentTarget.style.background = '#2563eb')}
        >
          {loading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
} 


