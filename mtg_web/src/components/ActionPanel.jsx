import React, { useState } from 'react';
import CardMenu from './CardMenu';

export default function ActionPanel({ actions, onActionSelected, hasPriority }) {
  const [selectedMainAction, setSelectedMainAction] = useState(null);

  if (!hasPriority) {
    return (
      <div className="action-panel waiting">
        Waiting for Opponent...
      </div>
    );
  }

  if (!actions || actions.length === 0) {
    return (
      <div className="action-panel empty">
        No actions available.
      </div>
    );
  }

  // Pre-process actions to group similar types
  const playLands = actions.filter(a => a.type === 'PLAY_LAND');
  const castSpells = actions.filter(a => a.type === 'CAST_SPELL');
  const tapMana = actions.filter(a => a.type === 'TAP_FOR_MANA');
  const genericActions = actions.filter(a => !['PLAY_LAND', 'CAST_SPELL', 'TAP_FOR_MANA'].includes(a.type));

  const handleActionClick = (action) => {
    // If the action requires a target, we might need to open a secondary menu
    // For now, if it has predefined targets in the action list, we assume it's a specific choice
    // and we can just send the ID. 
    onActionSelected(action.id);
  };

  return (
    <div className="action-panel active">
      <h3>Priority Actions</h3>
      <div className="action-buttons">
        {/* Pass Priority always first if available */}
        {genericActions.find(a => a.type === 'PASS_PRIORITY') && (
           <button 
             className="btn pass-btn"
             onClick={() => handleActionClick(genericActions.find(a => a.type === 'PASS_PRIORITY'))}
           >
             Pass
           </button>
        )}
        
        {/* Grouped interactions */}
        {playLands.length > 0 && (
           <button className="btn grouped-btn" onClick={() => setSelectedMainAction(selectedMainAction === 'lands' ? null : 'lands')}>
             Play Land ({playLands.length})
           </button>
        )}
        {castSpells.length > 0 && (
           <button className="btn grouped-btn" onClick={() => setSelectedMainAction(selectedMainAction === 'spells' ? null : 'spells')}>
             Cast Spell ({castSpells.length})
           </button>
        )}
        {tapMana.length > 0 && (
           <button className="btn grouped-btn" onClick={() => setSelectedMainAction(selectedMainAction === 'mana' ? null : 'mana')}>
             Tap for Mana ({tapMana.length})
           </button>
        )}

        {/* Other generic actions */}
        {genericActions.filter(a => a.type !== 'PASS_PRIORITY').map(action => (
          <button key={action.id} className="btn generic-btn" onClick={() => handleActionClick(action)}>
             {action.type.replace(/_/g, ' ')}
          </button>
        ))}
      </div>

      {/* Sub-menus for grouped actions */}
      {selectedMainAction === 'lands' && (
        <CardMenu title="Select Land to Play" items={playLands} onSelect={handleActionClick} />
      )}
      {selectedMainAction === 'spells' && (
        <CardMenu title="Select Spell to Cast" items={castSpells} onSelect={handleActionClick} />
      )}
      {selectedMainAction === 'mana' && (
        <CardMenu title="Tap for Mana" items={tapMana} onSelect={handleActionClick} />
      )}

    </div>
  );
}
