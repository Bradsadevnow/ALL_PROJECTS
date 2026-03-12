import asyncio
import os
import sys

# Ensure backend acts as package root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.config import settings
from backend.db.engine import init_db
from backend.agent.cortex import Cortex
from backend.agent.embedding_service import EmbeddingService
from backend.agent.hippocampus import Hippocampus
from backend.agent.thalamus import Thalamus

def main():
    print("Initializing Database...")
    init_db()

    print("Initializing Cortex...")
    if not settings.api_key:
        print("ERROR: GOOGLE_API_KEY or GEMINI_API_KEY environment variable is required.")
        return

    cortex = Cortex(api_key=settings.api_key, model_name=settings.model_name)
    embedding_service = EmbeddingService(api_key=settings.api_key)
    
    print("Initializing Hippocampus...")
    hippocampus = Hippocampus(embedding_service)
    
    print("Initializing Thalamus...")
    thalamus = Thalamus(cortex, hippocampus, embedding_service)

    print("\n--- Sending Test Query ---")
    state, reflection, response = thalamus.process_turn("Hello Steve! This is a test query to see if you can feel, think, and remember.")
    
    print("\n[RESULT]")
    print("STATE:", state)
    print("REFLECTION:", reflection)
    print("RESPONSE:", response)
    
    print("\n--- Running Sleep Cycle ---")
    from backend.agent.sleep_cycle import SleepCycle
    sc = SleepCycle(cortex)
    sc.run_consolidation_pipeline()

if __name__ == "__main__":
    main()
