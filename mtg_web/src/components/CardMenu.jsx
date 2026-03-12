import React from 'react';

export default function CardMenu({ title, items, onSelect }) {
  if (!items || items.length === 0) return null;

  return (
    <div className="card-menu">
      <div className="card-menu-title">{title}</div>
      <div className="card-menu-list">
        {items.map(action => {
           // We might not have a full card object, but the original action
           // from Python JSON payload might have stringified labels
           // or we can fall back to the card_id
           const id = action.object_id || action.id;
           // If payload has a card_id we can show something
           const label = action.payload?.card_id || `${action.type} ${id}`;

           return (
             <button key={action.id} className="menu-btn" onClick={() => onSelect(action)}>
               {label}
             </button>
           );
        })}
      </div>
    </div>
  );
}
