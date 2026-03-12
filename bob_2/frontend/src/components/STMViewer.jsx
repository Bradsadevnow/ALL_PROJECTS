import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import styles from './STMViewer.module.css';

const TurnBlock = ({ turn }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className={styles.turnBlock}>
      <div className={styles.turnHeader} onClick={() => setIsOpen(!isOpen)}>
        <span className={styles.turnTitle}>TURN #{turn.id.split('-')[0]}</span>
        <span className={styles.turnTime}>{new Date(turn.timestamp).toLocaleTimeString()}</span>
      </div>
      
      {isOpen && (
        <div className={styles.turnBody}>
          <div className={styles.section}>
            <span className={styles.sectionLabel}>User</span>
            <div className={styles.textContent}>{turn.user_query}</div>
          </div>
          
          <div className={styles.section}>
            <span className={styles.sectionLabel}>Response</span>
            <div className={styles.textContent}>{turn.response}</div>
          </div>

          <div className={styles.section}>
            <span className={styles.sectionLabel}>State</span>
            <pre className={styles.jsonContent}>
              {JSON.stringify(turn.state, null, 2)}
            </pre>
          </div>

          <div className={styles.section}>
            <span className={styles.sectionLabel}>Keywords</span>
            <div className={styles.pillContainer}>
              {turn.keywords?.map((kw, i) => (
                <span key={i} className={styles.pill}>{kw}</span>
              ))}
            </div>
          </div>

          <div className={styles.section}>
            <span className={styles.sectionLabel}>Reflection</span>
            <div className={styles.textContent}>{turn.reflection}</div>
          </div>

          <div className={styles.section}>
            <span className={styles.sectionLabel}>Memories Used ({turn.memories_used})</span>
            {turn.memory_ids_used?.length > 0 ? (
              <div className={styles.memoryList}>
                {turn.memory_ids_used.map((memId, i) => (
                  <span key={i} className={styles.memoryItem}>{memId}</span>
                ))}
              </div>
            ) : (
              <span className={styles.textContent} style={{fontStyle: 'italic', opacity: 0.6}}>None</span>
            )}
          </div>
          
          <div className={styles.section} style={{marginTop: '0.5rem', opacity: 0.5}}>
             <span className={styles.sectionLabel}>Prompt V{turn.prompt_version} | {turn.is_consolidated ? "Consolidated" : "Active"}</span>
          </div>
        </div>
      )}
    </div>
  );
};

const LTMBlock = ({ item }) => {
  const [isOpen, setIsOpen] = useState(false);
  const meta = item.metadata || {};
  return (
    <div className={styles.turnBlock}>
      <div className={styles.turnHeader} onClick={() => setIsOpen(!isOpen)}>
        <span className={styles.turnTitle}>{item.id.split('_')[0]}...</span>
        <span className={styles.turnTime}>{meta.timestamp ? new Date(meta.timestamp).toLocaleTimeString() : ''}</span>
      </div>
      {isOpen && (
        <div className={styles.turnBody}>
          <div className={styles.section}>
            <span className={styles.sectionLabel}>Vector Text</span>
            <div className={styles.textContent}>
              <pre className={styles.jsonContent}>{item.document}</pre>
            </div>
          </div>
          <div className={styles.section}>
            <span className={styles.sectionLabel}>Metadata</span>
            <pre className={styles.jsonContent}>
              {JSON.stringify(meta, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

const IdentityBlock = ({ identity }) => (
  <div className={styles.markdownContent} style={{ padding: '1rem' }}>
    <ReactMarkdown remarkPlugins={[remarkGfm]}>{identity.content}</ReactMarkdown>
  </div>
);

const DreamBlock = ({ dream }) => {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <div className={styles.turnBlock}>
      <div className={styles.turnHeader} onClick={() => setIsOpen(!isOpen)}>
        <span className={styles.turnTitle}>{dream.filename}</span>
      </div>
      {isOpen && (
        <div className={styles.turnBody}>
          <div className={styles.markdownContent}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{dream.content}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
};

const STMViewer = ({ isOpen, onClose, refreshTrigger }) => {
  const [activeTab, setActiveTab] = useState('stm');
  const [data, setData] = useState({
    stm: [],
    episodic: [],
    semantic: [],
    identity: { content: '' },
    dreams: []
  });
  const [loading, setLoading] = useState(false);

  const fetchData = async (tab) => {
    setLoading(true);
    try {
      let endpoint = '';
      if (tab === 'stm') endpoint = '/api/stm?limit=50';
      else if (tab === 'episodic') endpoint = '/api/ltm/episodic?limit=50';
      else if (tab === 'semantic') endpoint = '/api/ltm/semantic?limit=50';
      else if (tab === 'identity') endpoint = '/api/identity';
      else if (tab === 'dreams') endpoint = '/api/dreams';

      if (endpoint) {
        const res = await fetch(`http://${window.location.hostname}:8000${endpoint}`);
        if (res.ok) {
          const result = await res.json();
          setData(prev => ({ ...prev, [tab]: result }));
        }
      }
    } catch (e) {
      console.error(`Failed to fetch ${tab}:`, e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchData(activeTab);
    }
  }, [isOpen, activeTab, refreshTrigger]);

  const tabs = [
    { id: 'stm', label: 'STM Buffer' },
    { id: 'episodic', label: 'Episodic LTM' },
    { id: 'semantic', label: 'Semantic LTM' },
    { id: 'identity', label: 'Identity' },
    { id: 'dreams', label: 'Dreams' }
  ];

  return (
    <div className={`${styles.stmViewerContainer} ${isOpen ? styles.open : ''} glass-panel`}>
      <div className={styles.header}>
        <h2>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{marginRight: '8px'}}>
            <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
            <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
            <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
          </svg>
          Memory Viewer
        </h2>
        <div className={styles.controls}>
          <button className={styles.iconButton} onClick={() => fetchData(activeTab)} title="Refresh">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="23 4 23 10 17 10"></polyline>
              <polyline points="1 20 1 14 7 14"></polyline>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
            </svg>
          </button>
          <button className={styles.iconButton} onClick={onClose} title="Close">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      </div>
      
      <div style={{ display: 'flex', borderBottom: '1px solid var(--border-subtle)', padding: '0 1rem' }}>
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            style={{
              padding: '1rem',
              background: 'none',
              border: 'none',
              borderBottom: activeTab === t.id ? '2px solid var(--accent)' : '2px solid transparent',
              color: activeTab === t.id ? 'var(--text-primary)' : 'var(--text-secondary)',
              cursor: 'pointer',
              fontSize: '0.9rem',
              fontWeight: activeTab === t.id ? '600' : '400',
              transition: 'all 0.2s'
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className={styles.content}>
        {loading && (!data[activeTab] || data[activeTab].length === 0) ? (
          <div style={{textAlign: 'center', opacity: 0.5, marginTop: '2rem'}}>Loading...</div>
        ) : (
          <>
            {activeTab === 'stm' && (
              data.stm.length === 0 ? <div style={{textAlign: 'center', opacity: 0.5, marginTop: '2rem'}}>STM is empty.</div> :
              data.stm.map(turn => <TurnBlock key={turn.id} turn={turn} />)
            )}
            {activeTab === 'episodic' && (
              data.episodic.length === 0 ? <div style={{textAlign: 'center', opacity: 0.5, marginTop: '2rem'}}>Episodic memory is empty.</div> :
              data.episodic.map(item => <LTMBlock key={item.id} item={item} />)
            )}
            {activeTab === 'semantic' && (
              data.semantic.length === 0 ? <div style={{textAlign: 'center', opacity: 0.5, marginTop: '2rem'}}>Semantic memory is empty.</div> :
              data.semantic.map(item => <LTMBlock key={item.id} item={item} />)
            )}
            {activeTab === 'identity' && (
              <IdentityBlock identity={data.identity} />
            )}
            {activeTab === 'dreams' && (
              data.dreams.length === 0 ? <div style={{textAlign: 'center', opacity: 0.5, marginTop: '2rem'}}>No dreams generated yet.</div> :
              data.dreams.map(dream => <DreamBlock key={dream.filename} dream={dream} />)
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default STMViewer;
