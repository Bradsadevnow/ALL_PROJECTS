import React, { useEffect } from 'react';
import styles from './AgentStatus.module.css';

const getColorForEmotion = (emotionName) => {
  const map = {
    'Curiosity': 'var(--color-curiosity)',
    'Joy': 'var(--color-joy)',
    'Hope': 'var(--color-hope)',
    'Frustration': 'var(--color-frustration)',
    'Anxiety': 'var(--color-anxiety)',
    'Calmness': 'var(--color-calmness)',
    'Determination': 'var(--color-determination)'
  };
  return map[emotionName] || 'var(--border-focus)';
};

const AgentStatus = ({ status, agentState }) => {
  
  // When state arrives, extract the strongest emotion to dye the UI
  useEffect(() => {
    if (agentState && agentState.emotions && agentState.emotions.length > 0) {
      // Find highest intensity emotive type
      const emotions = agentState.emotions.filter(e => e.type === 'emotive');
      if (emotions.length > 0) {
        emotions.sort((a, b) => b.intensity - a.intensity);
        const topEmotion = emotions[0];
        const color = getColorForEmotion(topEmotion.name);
        document.documentElement.style.setProperty('--base-emotion-color', color);
      }
    } else {
      document.documentElement.style.setProperty('--base-emotion-color', 'var(--border-subtle)');
    }
  }, [agentState]);

  let statusDisplay = 'Idle';
  if (status === 'reflecting' || status === 'waiting') {
    statusDisplay = 'Synthesizing response...';
  }

  return (
    <div className={styles.statusContainer}>
      <div className={styles.agentInfo}>
        <div className={`${styles.avatar} ${status === 'reflecting' || status === 'waiting' ? styles.reflecting : ''}`}>
          🌌
        </div>
        <div className={styles.nameBlock}>
          <span className={styles.name}>Steve</span>
          <span className={styles.statusText}>{statusDisplay}</span>
        </div>
      </div>
      
      {agentState && agentState.emotions && (
        <div className={styles.stateVisualizer}>
          {agentState.emotions.map((e, idx) => (
             <div key={idx} className={styles.emotionPill} style={{ borderColor: getColorForEmotion(e.name) }}>
               {e.name}
             </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AgentStatus;
