import React from 'react';

export default function PlayerPanel({ playerId, life, mana, isOpponent }) {
  
  const manaIcons = {
    'WHITE': '🤍',
    'BLUE': '💧',
    'BLACK': '💀',
    'RED': '🔥',
    'GREEN': '🌳'
  };

  const renderManaPool = () => {
    if (!mana) return null;
    
    let elements = [];
    if (mana.generic > 0) {
       elements.push(<span key="generic" className="mana-symbol generic">{mana.generic}</span>);
    }
    
    if (mana.colored) {
      Object.entries(mana.colored).forEach(([color, amount]) => {
         if (amount > 0) {
            elements.push(
               <span key={color} className="mana-symbol colored" title={color}>
                  {amount}{manaIcons[color] || ''}
               </span>
            );
         }
      });
    }
    
    if (elements.length === 0) {
      return <span className="muted">Empty</span>;
    }
    
    return elements;
  };

  return (
    <div className={`player-panel ${isOpponent ? 'opponent-panel' : 'my-panel'}`}>
      <div className="player-id">{playerId}</div>
      <div className="life-total">
        <span className="life-label">Life</span>
        <span className="life-value">{life}</span>
      </div>
      {!isOpponent && (
        <div className="mana-pool">
          <span className="pool-label">Pool</span>
          <div className="pool-symbols">
            {renderManaPool()}
          </div>
        </div>
      )}
    </div>
  );
}
