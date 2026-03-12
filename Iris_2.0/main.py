import asyncio
import os
from core.runtime import IrisRuntime
from core.pipeline import IrisPipeline
from memory.mtm import MediumTermMemory
from memory.tokens import TokenTracker

# Config
API_KEY = "AIzaSyCkluiL8tnaAajV3pDaXd1OwDshAeRXXEY"
PERSISTENCE_DIR = "persistence"
LEDGER_PATH = os.path.join(PERSISTENCE_DIR, "iris_memory.jsonl")
MTM_PATH = os.path.join(PERSISTENCE_DIR, "iris_mtm.db")
SYSTEM_PROMPT_PATH = "system_prompt.txt"

async def main():
    # 1. Initialization
    os.makedirs(PERSISTENCE_DIR, exist_ok=True)
    
    mtm = MediumTermMemory(MTM_PATH)
    tokens = TokenTracker()
    runtime = IrisRuntime(LEDGER_PATH)
    pipeline = IrisPipeline(API_KEY, mtm, tokens)
    
    # 2. Recovery
    runtime._recover_from_logs()
    
    # Load system prompt
    with open(SYSTEM_PROMPT_PATH, "r") as f:
        system_prompt = f.read()

    print("\n--- IRIS 2.0 READY ---")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("Architect: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        try:
            # 3. Epoch Cycle
            epoch = await runtime.start_epoch()
            epoch.execute()
            
            # Run pipeline
            iris_voice = await pipeline.execute(
                user_input, 
                system_prompt, 
                runtime.stm
            )
            
            # Commit epoch
            payload = {
                "user_input": user_input,
                "thought": iris_voice.thought,
                "emotive_state": iris_voice.emotive_state.model_dump(),
                "final_response": iris_voice.final_response
            }
            await runtime.commit_epoch(payload)
            
            # Save thought to MTM
            mtm.add_thought(epoch.epoch_id, iris_voice.thought)
            
            # Output
            print(f"\nIris (Thinking): {iris_voice.thought}")
            print(f"Iris (Emotive): {iris_voice.emotive_state.model_dump()}")
            print(f"Iris: {iris_voice.final_response}\n")
            
            # Token Check
            if tokens.is_threshold_reached():
                print(f"--- WARNING: Token Threshold Reached ({tokens.total_usage}) ---")
            if tokens.is_hard_cap_exceeded():
                print("--- FATAL: Token Hard Cap Exceeded. Reset Required. ---")

        except RuntimeError as e:
            print(f"Error: {e}")
        except Exception as e:
            await runtime.abort_epoch(str(e))
            print(f"Epoch Aborted: {e}")

if __name__ == "__main__":
    asyncio.run(main())
