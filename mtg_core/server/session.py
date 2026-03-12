from typing import List, Optional
import asyncio
from fastapi import WebSocket

from mtg_core.engine import MTGEngine
from mtg_core.game_state import GameState
from mtg_core.aibase import VisibleState
from mtg_core.actions import Action, ActionType
from mtg_core.server.web_player import WebSocketPlayer
import random

class MockAIPlayer:
    def __init__(self, player_id: str):
        self.player_id = player_id

    async def choose_action(self, state: VisibleState, actions: List[Action]) -> Action:
        await asyncio.sleep(0.5)
        # Always prefer PASS_PRIORITY if available
        pass_action = next((a for a in actions if getattr(a.type, 'value', a.type) == "PASS_PRIORITY" or a.type == ActionType.PASS_PRIORITY), None)
        if pass_action:
            return pass_action
        return random.choice(actions) if actions else None

class GameSession:
    """
    Handles a single game session.
    Owns the MTGEngine, the players, and the websocket connection.
    """
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.engine: Optional[MTGEngine] = None
        self.players: dict[str, WebSocketPlayer] = {}
        self._task: Optional[asyncio.Task] = None

    def start_game(self, players_config: dict):
        """Initializes the game state and starts the session loop."""
        # Config would contain setup like player IDs, deck names, etc.
        # For now, hardcode P1 and P2 for testing
        
        player1_id = "P1"
        player2_id = "P2"

        # Initialize web players
        user_player = WebSocketPlayer(player1_id, self.websocket)
        ai_player = MockAIPlayer(player2_id)

        self.players = {
            player1_id: user_player,
            player2_id: ai_player,
        }

        # Setup initial game state
        from mtg_core.player_state import PlayerState
        from mtg_core.game_state import CardInstance
        import uuid
        
        # Create a mock deck of 60 plains for each player
        deck_size = 60
        p1_library = [CardInstance(instance_id=str(uuid.uuid4()), card_id="basic_plains", owner_id=player1_id) for _ in range(deck_size)]
        p2_library = [CardInstance(instance_id=str(uuid.uuid4()), card_id="basic_plains", owner_id=player2_id) for _ in range(deck_size)]

        game = GameState.new_game(players={
            player1_id: PlayerState(player_id=player1_id, life=20, library=p1_library, hand=[], graveyard=[]),
            player2_id: PlayerState(player_id=player2_id, life=20, library=p2_library, hand=[], graveyard=[])
        })
        
        self.engine = MTGEngine(game_state=game)
        
        # Start the game loop in the background
        self._task = asyncio.create_task(self.run())

    async def run(self):
        """The main game loop."""
        if not self.engine:
            return

        try:
            print("[Session] Game loop started.")
            
            while not self.engine.game.game_over:
                # 1. Get priority holder
                holder_id = self.engine.priority_holder
                player = self.players.get(holder_id)
                
                if player:
                   visible = self.engine.get_visible_state(holder_id)
                   
                   # Send state update to the client
                   await self._send_state_update(visible)
                   
                   actions = self.engine.get_legal_actions(holder_id)
                   
                   if actions:
                       # Ask the player for an action
                       action = await player.choose_action(visible, actions)
                       if action:
                           result = self.engine.submit_action(action)
                           print(f"[Session] Action resolved: {result.status}")
                   else:
                       await asyncio.sleep(0.1)
                else:
                   await asyncio.sleep(0.1)

            print("[Session] Game over.")
            
        except asyncio.CancelledError:
            print("[Session] Game loop cancelled.")
        except Exception as e:
           import traceback
           traceback.print_exc()
           print(f"[Session] Error in game loop: {e}")

    async def handle_client_message(self, data: dict):
        """Routes messages received from the client to the appropriate handler."""
        msg_type = data.get("type")
        
        if msg_type == "ACTION_RESPONSE":
            await self._handle_action_response(data)
        else:
            print(f"[Session] Unknown message type: {msg_type}")

    async def _handle_action_response(self, data: dict):
        """Routes the action response to the player waiting for it."""
        player_id = data.get("player_id")
        action_id = data.get("action_id")
        
        if player_id in self.players:
            player = self.players[player_id]
            if isinstance(player, WebSocketPlayer):
               player.receive_action_response(action_id)

    async def _send_state_update(self, visible_state: VisibleState):
        """Sends the exact VisibleState to the client."""
        import dataclasses
        try:
            state_dict = dataclasses.asdict(visible_state)
            await self.websocket.send_json({
                "type": "STATE_UPDATE",
                "state": state_dict
            })
        except Exception as e:
             print(f"[Session] Failed to send state update: {e}")

    async def broadcast_event(self, event_type: str, payload: dict):
        """Sends an event to the UI for animations/updates."""
        await self.websocket.send_json({
            "type": "EVENT",
            "event": event_type,
            **payload
        })
