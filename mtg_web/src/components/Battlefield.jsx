import React from 'react';

const CardThumb = ({ card }) => {
  // Try to use a Scryfall image if we have the card_id
  const name = card.name || card.card_id || 'Unknown';
  const imgUrl = `https://api.scryfall.com/cards/named?exact=${encodeURIComponent(name)}&format=image&version=small`;

  return (
    <div className={`card-thumb ${card.tapped ? 'tapped' : ''}`}>
      <img src={imgUrl} alt={name} onError={(e) => { 
        e.target.onerror = null; 
        e.target.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="146" height="204" style="background:%23333"><text x="50%" y="50%" fill="%23fff" text-anchor="middle" font-family="sans-serif">Card</text></svg>';
      }} />
      <div className="card-info">
        <span className="card-name">{name}</span>
        {card.power !== undefined && card.toughness !== undefined && (
          <span className="card-pt">{card.power}/{card.toughness}</span>
        )}
      </div>
    </div>
  );
};

export default function Battlefield({ permanents, isOpponent }) {
  // Sort permanents (e.g., lands in back, creatures in front)
  const lands = permanents.filter(p => p.types?.includes('Land') || p.card_id.includes('Land'));
  const nonLands = permanents.filter(p => !p.types?.includes('Land') && !p.card_id.includes('Land'));

  return (
    <div className={`battlefield ${isOpponent ? 'opponent' : 'player'}`}>
      <div className="bf-row non-lands">
        {nonLands.map(p => <CardThumb key={p.instance_id} card={p} />)}
      </div>
      <div className="bf-row lands">
         {lands.map(p => <CardThumb key={p.instance_id} card={p} />)}
      </div>
    </div>
  );
}
