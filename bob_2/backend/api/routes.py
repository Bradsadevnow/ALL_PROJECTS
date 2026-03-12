from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import asyncio
import json
import logging
import os

from backend.agent.cortex import Cortex
from backend.agent.hippocampus import Hippocampus
from backend.agent.thalamus import Thalamus
from backend.agent.embedding_service import EmbeddingService
from backend.core.config import settings
from backend.db.engine import init_db, SessionLocal
from backend.db.models import Turn

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize Agent Components
init_db()
embedding_service = EmbeddingService(api_key=settings.api_key)
cortex = Cortex(api_key=settings.api_key, model_name=settings.model_name)
hippocampus = Hippocampus(embedding_service)
thalamus = Thalamus(cortex, hippocampus, embedding_service)


class ChatRequest(BaseModel):
    query: str
    task_id: str = "REST_API"

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Stateless REST endpoint for testing."""
    # Since Thalamus is currently synchronous, we run it in a thread
    final_state, reflection, response = await asyncio.to_thread(
        thalamus.process_turn, request.query, request.task_id
    )
    
    return {
        "response": response,
        "reflection": reflection,
        "state": final_state
    }

@router.get("/stm")
def get_stm(limit: int = 50):
    if limit > 200:
        limit = 200
        
    db = SessionLocal()
    try:
        turns = (
            db.query(Turn)
            .order_by(Turn.timestamp.desc())
            .limit(limit)
            .all()
        )
        return [turn.to_dict() for turn in turns]
    finally:
        db.close()

@router.get("/ltm/episodic")
def get_episodic_ltm(limit: int = 50):
    try:
        results = hippocampus.col_episodic.get(
            limit=limit,
            include=["metadatas", "documents"]
        )
        
        # Zip and format
        items = []
        if results and results["ids"]:
            for i, doc_id in enumerate(results["ids"]):
                meta = results["metadatas"][i] or {}
                items.append({
                    "id": doc_id,
                    "metadata": meta,
                    "document": results["documents"][i] if results.get("documents") else None
                })
        
        # Sort by timestamp descending
        items.sort(key=lambda x: x["metadata"].get("timestamp", ""), reverse=True)
        return items
    except Exception as e:
        logger.error(f"Failed to fetch episodic LTM: {e}")
        return []

@router.get("/ltm/semantic")
def get_semantic_ltm(limit: int = 50):
    try:
        results = hippocampus.col_semantic.get(
            limit=limit,
            include=["metadatas", "documents"]
        )
        
        items = []
        if results and results["ids"]:
            for i, doc_id in enumerate(results["ids"]):
                meta = results["metadatas"][i] or {}
                items.append({
                    "id": doc_id,
                    "metadata": meta,
                    "document": results["documents"][i] if results.get("documents") else None
                })
        
        items.sort(key=lambda x: x["metadata"].get("timestamp", ""), reverse=True)
        return items
    except Exception as e:
        logger.error(f"Failed to fetch semantic LTM: {e}")
        return []

@router.get("/identity")
def get_identity():
    file_path = f"{os.getenv('STEVE_RUNTIME_DIR', 'runtime')}/identity_context.md"
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return {"content": f.read()}
        return {"content": "Identity file not found."}
    except Exception as e:
        logger.error(f"Failed to read identity: {e}")
        return {"content": f"Error loading identity: {str(e)}"}

@router.get("/dreams")
def get_dreams():
    dreams_dir = f"{os.getenv('STEVE_RUNTIME_DIR', 'runtime')}/dreams"
    dreams = []
    try:
        if os.path.exists(dreams_dir):
            for filename in os.listdir(dreams_dir):
                if filename.endswith(".md"):
                    with open(os.path.join(dreams_dir, filename), "r", encoding="utf-8") as f:
                        dreams.append({
                            "filename": filename,
                            "content": f.read()
                        })
        # Sort by filename descending (date prefix)
        dreams.sort(key=lambda x: x["filename"], reverse=True)
        return dreams
    except Exception as e:
        logger.error(f"Failed to fetch dreams: {e}")
        return []

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time interaction.
    Allows streaming the 'reflection' state before the final response.
    """
    await websocket.accept()
    logger.info("WebSocket connected.")
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                payload = json.loads(data)
                query = payload.get("query", "")
                task_id = payload.get("task_id", "WS_CLIENT")
            except json.JSONDecodeError:
                query = data
                task_id = "WS_CLIENT"
                
            if not query.strip():
                continue
                
            # Inform UI we are thinking
            await websocket.send_json({"type": "status", "message": "reflecting"})
            
            # Since Thalamus evaluates feel_and_reflect synchronously alongside response,
            # we'll emit the block once the turn is processed.
            # In a fully asynchronous rewrite of the agent core, we could yield the reflection early.
            final_state, reflection, response = await asyncio.to_thread(
                thalamus.process_turn, query, task_id
            )
            
            await websocket.send_json({
                "type": "turn_complete",
                "reflection": reflection,
                "state": final_state,
                "response": response
            })
            
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected.")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
           await websocket.send_json({"type": "error", "message": str(e)})
        except:
           pass
