import { useState, useEffect, useCallback } from 'react';
import Battlefield from './components/Battlefield';
import Hand from './components/Hand';
import Stack from './components/Stack';
import ActionPanel from './components/ActionPanel';
import PlayerPanel from './components/PlayerPanel';
import './components.css';
import './App.css';

function App() {
  const [ws, setWs] = useState(null);
  const [gameState, setGameState] = useState(null);
  const [allowedActions, setAllowedActions] = useState([]);
  const [events, setEvents] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('Disconnected');

  useEffect(() => {
    // Generate a simple client ID for this session
    const clientId = Math.random().toString(36).substring(7);
    const socket = new WebSocket(`ws://localhost:8000/ws/${clientId}`);

    socket.onopen = () => {
      console.log('Connected to game server');
      setConnectionStatus('Connected');
      setWs(socket);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("Received message:", data.type, data);

        if (data.type === 'STATE_UPDATE') {
          setGameState(data.state);
          // Clear actions on new state update until a new ACTION_REQUEST arrives
          setAllowedActions([]);
        } else if (data.type === 'ACTION_REQUEST') {
          setAllowedActions(data.actions);
          window.actingPlayerId = data.player_id;
        } else if (data.type === 'EVENT') {
          // Add event to the log/animation queue
          setEvents(prev => [...prev, data].slice(-10)); // Keep last 10 events
          console.log("Game Event:", data);
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
      }
    };

    socket.onclose = () => {
      console.log('Disconnected from game server');
      setConnectionStatus('Disconnected');
      setWs(null);
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnectionStatus('Error');
    };

    return () => {
      socket.close();
    };
  }, []);

  const handleActionSelected = useCallback((actionId) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      console.log("Sending ACTION_RESPONSE:", actionId);
      ws.send(JSON.stringify({
        type: 'ACTION_RESPONSE',
        player_id: window.actingPlayerId || 'P1',
        action_id: actionId
      }));
      // Clear allowed actions to prevent double submission
      setAllowedActions([]);
    }
  }, [ws]);

  if (connectionStatus !== 'Connected') {
    return (
      <div className="connection-screen">
        <h1>MTG Engine</h1>
        <p>Status: {connectionStatus}</p>
        <div className="spinner"></div>
      </div>
    );
  }

  if (!gameState) {
    return (
      <div className="connection-screen">
        <h1>MTG Engine</h1>
        <p>Connected. Waiting for game state...</p>
      </div>
    );
  }

  // Assuming player IDs are P1 and P2 based on our initial python code
  const myId = 'P1';
  const oppId = 'P2';

  // Extract component props from the VisibleState
  const myLife = gameState.life_totals?.[myId] ?? 20;
  const oppLife = gameState.life_totals?.[oppId] ?? 20;
  
  const myMana = gameState.available_mana ?? {}; // Server only sends ours
  
  // zones might be structured differently depending on the serialization
  const zones = gameState.zones || { battlefield: [], hand: [], stack: [] };
  
  const myPermanents = zones.battlefield?.filter(p => p.controller_id === myId) || [];
  const oppPermanents = zones.battlefield?.filter(p => p.controller_id === oppId) || [];

  return (
    <div className="app-container glass-theme">
      
      {/* Sidebar - Game Info & Events */}
      <aside className="sidebar panel-glass">
         <div className="game-info">
            <h2>Game Status</h2>
            <div className="info-row"><span>Turn</span> <strong>{gameState.turn_number}</strong></div>
            <div className="info-row"><span>Phase</span> <strong>{gameState.phase}</strong></div>
            <div className="info-row"><span>Active</span> <strong>{gameState.active_player_id}</strong></div>
            <div className="info-row"><span>Priority</span> <strong>{gameState.priority_holder_id}</strong></div>
         </div>
         
         <div className="event-log">
            <h3>Event Log</h3>
            <div className="event-list">
              {events.length === 0 ? <p className="muted">No events yet</p> : null}
              {events.map((ev, i) => (
                <div key={i} className="event-item">
                  <span className="event-type">{ev.event}</span>
                  {ev.card && <span className="event-detail">{ev.card}</span>}
                </div>
              ))}
            </div>
         </div>
      </aside>

      {/* Main Game Area */}
      <main className="game-area">
        
        {/* Opponent Zone */}
        <section className="player-zone opp-zone transparent-panel">
            <PlayerPanel playerId={oppId} life={oppLife} isOpponent={true} />
            <Battlefield permanents={oppPermanents} isOpponent={true} />
        </section>

        {/* The Stack (Center) */}
        <section className="center-zone transparent-panel">
           <Stack items={zones.stack || []} />
        </section>

        {/* Player Zone */}
        <section className="player-zone my-zone transparent-panel">
            <Battlefield permanents={myPermanents} isOpponent={false} />
            
            <div className="my-bottom-row">
               <PlayerPanel playerId={myId} life={myLife} mana={myMana} isOpponent={false} />
               <Hand cards={zones.hand || []} />
               <ActionPanel 
                  actions={allowedActions} 
                  onActionSelected={handleActionSelected} 
                  hasPriority={gameState.priority_holder_id === myId}
               />
            </div>
        </section>

      </main>
    </div>
  );
}

export default App;
