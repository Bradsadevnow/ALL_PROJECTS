from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from mtg_core.server.session import GameSession

app = FastAPI(title="MTG Engine Server")

# Allow React app to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev, restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active sessions
sessions: Dict[str, GameSession] = {}


@app.get("/")
def root():
    return {"message": "MTG Engine Server is running"}


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    
    # Create a new game session for this connection
    session = GameSession(websocket)
    sessions[client_id] = session
    
    # Start the session
    session.start_game({})

    try:
        while True:
            # Wait for messages from the client
            data = await websocket.receive_json()
            
            # Route to the session
            await session.handle_client_message(data)
            
    except WebSocketDisconnect:
        print(f"Client #{client_id} disconnected")
        # Cleanup session
        if client_id in sessions:
            del sessions[client_id]
    except Exception as e:
        print(f"WebSocket error for client #{client_id}: {e}")
        if client_id in sessions:
             del sessions[client_id]
