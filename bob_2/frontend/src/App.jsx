import React, { useState, useEffect, useRef } from 'react';
import ChatContainer from './components/ChatContainer';
import MessageInput from './components/MessageInput';
import AgentStatus from './components/AgentStatus';
import STMViewer from './components/STMViewer';
import styles from './App.module.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [status, setStatus] = useState('idle'); // 'idle', 'reflecting', 'responding'
  const [agentState, setAgentState] = useState(null);
  const [isSTMOpen, setIsSTMOpen] = useState(false);
  const [stmRefreshTrigger, setStmRefreshTrigger] = useState(0);
  const wsRef = useRef(null);

  useEffect(() => {
    // Initial connection
    const connectWs = () => {
      const socket = new WebSocket(`ws://${window.location.hostname}:8000/api/ws/chat`);

      socket.onopen = () => {
        console.log('Connected to Steve Core');
      };

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'status') {
          setStatus(data.message);
        } else if (data.type === 'turn_complete') {
          setAgentState(data.state);
          setStatus('idle');
          
          setMessages(prev => [...prev, {
            id: Date.now(),
            role: 'agent',
            content: data.response,
            reflection: data.reflection
          }]);
          
          setStmRefreshTrigger(prev => prev + 1);
        } else if (data.type === 'error') {
          console.error('Server error:', data.message);
          setStatus('idle');
        }
      };

      socket.onclose = () => {
        console.log('Disconnected. Reconnecting in 3s...');
        setTimeout(connectWs, 3000);
      };

      wsRef.current = socket;
    };

    connectWs();
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  const handleSendMessage = (text) => {
    if (!text.trim() || status !== 'idle') return;

    setMessages(prev => [...prev, { id: Date.now(), role: 'user', content: text }]);
    setStatus('waiting');

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ query: text, task_id: 'UI_WEB' }));
    }
  };

  return (
    <div className={styles.appContainer}>
      <div className={styles.ambientGlow} />
      
      {!isSTMOpen && (
        <button 
          className="toggleButton" 
          onClick={() => setIsSTMOpen(true)}
          style={{
            position: 'absolute', top: '1.5rem', right: '1.5rem', zIndex: 50,
            background: 'var(--surface-overlay)', border: '1px solid var(--border-subtle)',
            color: 'var(--text-secondary)', padding: '0.5rem 1rem', borderRadius: '20px',
            fontSize: '0.85rem', cursor: 'pointer', backdropFilter: 'blur(10px)'
          }}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{marginRight: '6px', verticalAlign: 'middle'}}>
            <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
            <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
            <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
          </svg>
          View Agent Memory
        </button>
      )}

      <STMViewer 
        isOpen={isSTMOpen} 
        onClose={() => setIsSTMOpen(false)} 
        refreshTrigger={stmRefreshTrigger}
      />
      
      <div className={`${styles.chatLayout} glass-panel`}>
        <AgentStatus status={status} agentState={agentState} />
        <ChatContainer messages={messages} status={status} />
        <MessageInput onSend={handleSendMessage} disabled={status !== 'idle'} />
      </div>
    </div>
  );
}

export default App;
