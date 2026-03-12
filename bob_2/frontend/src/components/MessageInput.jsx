import React, { useState } from 'react';
import styles from './MessageInput.module.css';

const MessageInput = ({ onSend, disabled }) => {
  const [text, setText] = useState('');

  const handleSend = () => {
    if (text.trim() && !disabled) {
      onSend(text);
      setText('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={styles.inputContainer}>
      <div className={styles.inputWrapper}>
        <textarea
          className={styles.textArea}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Speak to Steve..."
          disabled={disabled}
          rows={1}
        />
        <button 
          className={styles.sendButton}
          onClick={handleSend}
          disabled={disabled || !text.trim()}
        >
          {/* Simple SVG icon for send */}
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
    </div>
  );
};

export default MessageInput;
