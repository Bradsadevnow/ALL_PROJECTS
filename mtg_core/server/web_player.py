import asyncio
from typing import List, Optional
from fastapi import WebSocket

from mtg_core.actions import Action
from mtg_core.aibase import VisibleState


class WebSocketPlayer:
    """
    Bridge between the engine and the WebSocket client.
    Sends requested actions to the client and asynchronously waits for a response.
    """
    def __init__(self, player_id: str, websocket: WebSocket):
        self.player_id = player_id
        self.websocket = websocket
        self._pending_action_future: Optional[asyncio.Future] = None
        self._current_actions: List[Action] = []

    async def choose_action(self, state: VisibleState, actions: List[Action]) -> Action:
        """
        Called by the GameSession when the engine needs this player to act.
        """
        self._current_actions = actions
        
        # Determine a serializable format for allowed actions
        serialized_actions = []
        for i, action in enumerate(actions):
            # Simplistic serialization for initial build
            serialized_actions.append({
                "id": i,
                "type": action.type.value if hasattr(action.type, 'value') else str(action.type),
                "object_id": action.object_id,
                "targets": action.targets,
            })

        # Send ACTION_REQUEST
        try:
            await self.websocket.send_json({
                "type": "ACTION_REQUEST",
                "player_id": self.player_id,
                "actions": serialized_actions
            })
        except Exception as e:
             print(f"[WebSocketPlayer {self.player_id}] Failed to send ACTION_REQUEST: {e}")
             # Return a default action or error
             return actions[0] if actions else None

        # Wait for ACTION_RESPONSE without blocking the event loop
        self._pending_action_future = asyncio.Future()
        
        try:
            action_index = await self._pending_action_future
            
            if 0 <= action_index < len(self._current_actions):
                return self._current_actions[action_index]
            else:
                 print(f"[WebSocketPlayer {self.player_id}] Invalid action index received: {action_index}")
                 return self._current_actions[0] if self._current_actions else None
        finally:
            self._pending_action_future = None
            self._current_actions = []

    def receive_action_response(self, action_id: int):
        """
        Called by GameSession when the client sends an ACTION_RESPONSE.
        Resolves the pending future with the chosen index.
        """
        if self._pending_action_future and not self._pending_action_future.done():
            self._pending_action_future.set_result(action_id)
        else:
             print(f"[WebSocketPlayer {self.player_id}] Received unexpected action response: {action_id}")
