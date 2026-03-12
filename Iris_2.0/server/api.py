from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import asyncio
import json

from core.runtime import IrisRuntime
from core.pipeline import IrisPipeline
from memory.mtm import MediumTermMemory
from memory.tokens import TokenTracker
from server.refiner import IdentityRefiner

app = FastAPI(title="Iris Backend")

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared state
API_KEY = "AIzaSyCkluiL8tnaAajV3pDaXd1OwDshAeRXXEY"
PERSISTENCE_DIR = "persistence"
LEDGER_PATH = os.path.join(PERSISTENCE_DIR, "iris_memory.jsonl")
MTM_PATH = os.path.join(PERSISTENCE_DIR, "iris_mtm.db")
SYSTEM_PROMPT_PATH = "system_prompt.txt"

os.makedirs(PERSISTENCE_DIR, exist_ok=True)
mtm = MediumTermMemory(MTM_PATH)
tokens = TokenTracker()
runtime = IrisRuntime(LEDGER_PATH)
pipeline = IrisPipeline(API_KEY, mtm, tokens)
refiner = IdentityRefiner(API_KEY)

# Recover on startup
runtime._recover_from_logs()

with open(SYSTEM_PROMPT_PATH, "r") as f:
    system_prompt = f.read()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    epoch_id: str
    thought: str
    emotive_state: Dict[str, float]
    final_response: str
    tokens: Dict[str, int]
    resonances: List[str]

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Transactional Epoch
        epoch = await runtime.start_epoch()
        epoch.execute()
        
        # Get MTM resonances for frontend visibility
        resonances = mtm.search_resonances(request.message)
        
        # Run pipeline
        iris_voice = await pipeline.execute(
            request.message, 
            system_prompt, 
            runtime.stm
        )
        
        # Commit epoch
        payload = {
            "user_input": request.message,
            "thought": iris_voice.thought,
            "emotive_state": iris_voice.emotive_state.model_dump(),
            "final_response": iris_voice.final_response
        }
        await runtime.commit_epoch(payload)
        
        # Save thought to MTM
        mtm.add_thought(epoch.epoch_id, iris_voice.thought)
        
        return {
            "epoch_id": epoch.epoch_id,
            "thought": iris_voice.thought,
            "emotive_state": iris_voice.emotive_state.model_dump(),
            "final_response": iris_voice.final_response,
            "tokens": tokens.get_usage_report(),
            "resonances": resonances
        }

    except RuntimeError as e:
        raise HTTPException(status_code=423, detail=str(e))
    except Exception as e:
        if runtime.current_epoch:
            await runtime.abort_epoch(str(e))
        raise HTTPException(status_code=500, detail=f"Epoch Aborted: {str(e)}")

@app.get("/history")
async def get_history():
    return {
        "stm": runtime.stm,
        "ledger": runtime.ledger.read_all()
    }

@app.get("/status")
async def get_status():
    # Get last emotive state from STM if available
    emotive = {"curiosity": 0.5, "determination": 0.5, "frustration": 0.1, "calmness": 0.9}
    if runtime.stm:
        emotive = runtime.stm[-1].get("emotive_state", emotive)
    
    # Calculate token pressure
    usage = tokens.get_usage_report()
    total = usage["total_usage"]
    threshold = usage["threshold"]
    pressure = max(0.0, (total - (threshold * 0.8)) / (threshold * 0.2)) if total > threshold * 0.8 else 0.0
        
    return {
        "tokens": usage,
        "runtime_state": runtime.lifecycle_state,
        "emotive": emotive,
        "pressure": pressure
    }

@app.get("/dream")
async def get_dream():
    dream_path = "runtime/dream_fragment.md"
    if os.path.exists(dream_path):
        with open(dream_path, "r") as f:
            return {"dream": f.read()}
    return {"dream": "No current dream residuals."}

@app.get("/identity")
async def get_identity():
    identity_path = "runtime/identity_context.md"
    if os.path.exists(identity_path):
        with open(identity_path, "r") as f:
            return {"identity": f.read()}
    return {"identity": "Identity context unavailable."}

@app.post("/management/sleep")
async def trigger_sleep():
    """Manual trigger for the Consolidation/Sleep Cycle."""
    print("🌙 Manual Sleep Cycle triggered via API.")
    # Extract just the payload part for the refiner
    history = [event["payload"] for event in runtime.stm if "payload" in event]
    
    # 1. Refine Identity and Dream
    success = refiner.execute_sleep_cycle(history)
    
    if success:
        # 2. Reset STM and Ledger
        runtime.ledger.clear()
        runtime.stm = []
        return {"status": "success", "message": "Sleep Cycle complete. Identity re-anchored."}
    
    return {"status": "error", "message": "Sleep Cycle failed."}

@app.post("/clear")
async def clear_memory():
    # Dangerous operation, use with caution
    runtime.ledger.clear()
    runtime.stm = []
    # Re-init DB if needed or clear tables
    return {"status": "Memory cleared"}
