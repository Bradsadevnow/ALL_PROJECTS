import React from 'react';

export default function Stack({ items }) {
  if (!items || items.length === 0) {
    return <div className="stack empty">Stack is empty</div>;
  }

  return (
    <div className="stack filled">
      <h3>The Stack</h3>
      <div className="stack-items">
        {items.map((item, index) => {
          const name = item.name || item.card_id || 'Unknown Spell';
          // Determine if there are targets
          let targetStr = '';
          if (item.targets) {
            if (item.targets.type === 'PLAYER') {
               targetStr = ` -> Player ${item.targets.player_id}`;
            } else if (item.targets.type === 'PERMANENT') {
               targetStr = ` -> Permanent ${item.targets.instance_id.substring(0,8)}...`;
            }
          }
          
          return (
            <div key={item.instance_id || index} className="stack-item" style={{zIndex: items.length - index}}>
              <span className="spell-name">{name}</span>
              <span className="spell-target">{targetStr}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
