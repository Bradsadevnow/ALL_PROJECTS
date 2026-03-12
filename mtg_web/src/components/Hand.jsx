import React from 'react';

export default function Hand({ cards }) {
  return (
    <div className="hand-container">
      {cards.map((card, i) => {
        const name = card.name || card.card_id || 'Unknown';
        const imgUrl = `https://api.scryfall.com/cards/named?exact=${encodeURIComponent(name)}&format=image&version=normal`;
        
        return (
          <div key={card.instance_id || i} className="hand-card">
            <img src={imgUrl} alt={name} onError={(e) => { 
                e.target.onerror = null; 
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'flex';
            }} />
            <div className="hand-card-fallback" style={{display: 'none'}}>
               {name}
            </div>
          </div>
        );
      })}
    </div>
  );
}
