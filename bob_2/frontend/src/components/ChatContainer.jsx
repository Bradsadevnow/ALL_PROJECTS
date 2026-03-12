import React, { useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import styles from './ChatContainer.module.css';

const ChatContainer = ({ messages, status }) => {
  const containerRef = useRef(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages, status]);

  return (
    <div className={styles.chatContainer} ref={containerRef}>
      {messages.length === 0 && (
        <div style={{ margin: 'auto', color: 'var(--text-secondary)', textAlign: 'center' }}>
          <p>The mind is quiet.</p>
        </div>
      )}

      {messages.map((msg) => (
        <div 
          key={msg.id} 
          className={`${styles.messageRow} ${msg.role === 'user' ? styles.userRow : styles.agentRow}`}
        >
          {msg.role === 'agent' && msg.reflection && (
            <div className={styles.reflection}>
              <span className={styles.reflectionText}>{msg.reflection}</span>
            </div>
          )}
          <div className={`${styles.messageBubble} ${msg.role === 'user' ? styles.userBubble : styles.agentBubble}`}>
            {msg.role === 'user' ? (
              msg.content
            ) : (
              <ReactMarkdown 
                remarkPlugins={[remarkGfm]}
                components={{
                  img: ({node, ...props}) => (
                    <img 
                      {...props} 
                      style={{ maxWidth: '100%', borderRadius: '8px', marginTop: '0.5rem', display: 'block' }} 
                      alt={props.alt || "Image"} 
                      loading="lazy"
                    />
                  ),
                  a: ({node, ...props}) => (
                    <a {...props} target="_blank" rel="noopener noreferrer" style={{color: 'var(--color-hope)', textDecoration: 'underline'}}/>
                  )
                }}
              >
                {msg.content}
              </ReactMarkdown>
            )}
          </div>
        </div>
      ))}

      {(status === 'reflecting' || status === 'waiting') && (
        <div className={`${styles.messageRow} ${styles.agentRow}`}>
          <div className={styles.typingIndicator}>
             <div className={styles.dot}></div>
             <div className={styles.dot}></div>
             <div className={styles.dot}></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatContainer;
