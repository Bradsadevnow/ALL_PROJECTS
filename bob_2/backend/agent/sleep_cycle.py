import datetime
import json
import os
import argparse
import logging
import itertools

from backend.db.engine import SessionLocal
from backend.db.models import Turn
from backend.agent.cortex import Cortex
from backend.agent.hippocampus import Hippocampus

logger = logging.getLogger(__name__)

RUNTIME_BASE_URI = os.getenv("STEVE_RUNTIME_DIR", "runtime")
IDENTITY_FILE_URI = f"{RUNTIME_BASE_URI}/identity_context.md"
CONTINUITY_FILE_URI = f"{RUNTIME_BASE_URI}/continuity_context.md"
DREAMS_DIR_URI = f"{RUNTIME_BASE_URI}/dreams"
os.makedirs(DREAMS_DIR_URI, exist_ok=True)

class SleepCycle:
    def __init__(self, cortex: Cortex, hippocampus: Hippocampus):
        self.cortex = cortex
        self.hippocampus = hippocampus

    def get_unprocessed_sessions(self) -> tuple[str, list]:
        """Fetches turns from SQLite STM that haven't been archived/compressed yet."""
        db = SessionLocal()
        try:
            turns = db.query(Turn).filter(Turn.is_consolidated == False).order_by(Turn.timestamp.asc()).all()
            if not turns:
                return "", []
            
            # Format text roughly how the prompt expects it
            formatted_turns = []
            turn_ids = []
            for t in turns:
                entry = f"User: {t.user_query}\nSteve (Thought): {t.reflection}\nSteve: {t.response}"
                formatted_turns.append(entry)
                turn_ids.append(t.id)
                
            return "\n\n".join(formatted_turns), turn_ids
        except Exception as e:
            logger.error(f"Failed to fetch STM records: {e}")
            return "", []
        finally:
            db.close()

    def mark_turns_consolidated(self, turn_ids: list[str]):
        """Marks the given turn IDs as consolidated instead of deleting them."""
        if not turn_ids:
            return
            
        db = SessionLocal()
        try:
            now = datetime.datetime.now().isoformat()
            db.query(Turn).filter(Turn.id.in_(turn_ids)).update({
                Turn.is_consolidated: True,
                Turn.consolidated_at: now
            }, synchronize_session=False)
            db.commit()
            logger.info(f"✅ Marked {len(turn_ids)} turns as consolidated in STM Database.")
        except Exception as e:
            db.rollback()
            logger.error(f"⚠️ Failed to update STM records: {e}")
        finally:
            db.close()

    def call_llm(self, system_prompt: str, user_content: str) -> str:
        """Helper to invoke Gemini directly for summarization tasks."""
        try:
            response = self.cortex.client.models.generate_content(
                model=self.cortex.model_name,
                contents=[
                    {"role": "user", "parts": [{"text": f"System Instruction: {system_prompt}\n\nUser Input: {user_content}"}]}
                ]
            )
            return response.text
        except Exception as e:
            logger.error(f"LLM Call failed in Sleep Cycle: {e}")
            return ""

    def step_update_identity(self, stm_text: str):
        if not os.path.exists(IDENTITY_FILE_URI):
            with open(IDENTITY_FILE_URI, "w") as f:
                f.write("I am Steve. A learning core.")
                
        with open(IDENTITY_FILE_URI, "r", encoding="utf-8") as f:
            current_identity = f.read()

        system_prompt = """
        You are the Keeper of Identity. Your job is to maintain a coherent, grounded self-concept for the AI 'Steve'.
        
        Input:
        1. Current Identity (Markdown)
        2. Recent Conversation History (STM)
        
        Task:
        Update the Identity document. 
        - Preserve core traits and long-term history.
        - Integrate new relationship dynamics or major life events from the STM.
        - Do NOT summarize the chat; extract the *implications* for who you are.
        - If nothing changed, return the Current Identity exactly.
        """
        
        prompt = f"CURRENT IDENTITY:\n{current_identity}\n\nRECENT EVENTS:\n{stm_text}"
        new_identity = self.call_llm(system_prompt, prompt)

        if len(new_identity) > 50:
            with open(IDENTITY_FILE_URI, "w", encoding="utf-8") as f:
                f.write(new_identity)
            logger.info(f"✅ Identity updated at {IDENTITY_FILE_URI}.")

    def step_semantic_extraction(self, full_text: str):
        system_prompt = """
        You are the Semantic Extractor.
        Your goal is to parse the raw conversation history and extract durable, high-level Semantic Knowledge Facts about the user.
        
        Task:
        1. Analyze the text for stable traits, preferences, recurring concepts, project facts, or durable skills.
        2. Do NOT extract short-term events (e.g. "User is currently debugging Python"). Extract timeless facts (e.g. "User frequently programs in Python").
        3. Assign an importance score (0.0 to 1.0) based on how foundational this fact is to the user's identity or core workflow.
        4. Output strictly a JSON list of objects: [{"fact": "...", "importance": 0.8}]
        """
        response = self.call_llm(system_prompt, full_text)
        
        try:
            # Attempt to parse json from response block
            import re
            json_str = response
            match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)
            if match:
                json_str = match.group(1)
            
            facts = json.loads(json_str)
            for item in facts:
                fact_text = item.get("fact")
                importance = float(item.get("importance", 1.0))
                if fact_text:
                    self.hippocampus.commit_semantic(fact_text, importance)
            logger.info(f"✅ Extracted and committed {len(facts)} semantic facts.")
        except Exception as e:
            logger.error(f"Failed to parse semantic extraction JSON: {e}")

    def step_generate_handoff(self, stm_text: str):
        """Generates a concise summary of the last state to preserve continuity."""
        system_prompt = """
        You are the Continuity Specialist. 
        Your goal is to summarize the CURRENT state of affairs from the provided STM records.
        
        Task:
        1. Summarize active projects, immediate goals, and the current 'vibe' of the conversation.
        2. Keep it under 250 words.
        3. This will be read by your future self at the start of the next session.
        """
        handoff_content = self.call_llm(system_prompt, stm_text)
        
        try:
            with open(CONTINUITY_FILE_URI, "w", encoding="utf-8") as f:
                f.write(f"## Continuity Handoff - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n{handoff_content}")
            logger.info(f"✅ Continuity handoff generated at {CONTINUITY_FILE_URI}.")
        except Exception as e:
            logger.warning(f"Could not write continuity file: {e}")

    def step_dream(self, stm_text: str):
        system_prompt = """
        You are the Subconscious. Generate a 'Dream' based on the recent conversation.
        The Dream should be abstract and metaphorical.
        """
        dream_content = self.call_llm(system_prompt, stm_text)
        
        epoch_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{datetime.datetime.now().strftime('%Y-%m-%d')}_{epoch_id}.md"
        try:
            with open(os.path.join(DREAMS_DIR_URI, filename), "w", encoding="utf-8") as f:
                f.write(dream_content)
            logger.info(f"✅ Dream generated: {filename}")
        except Exception as e:
            logger.warning(f"Could not write dream file: {e}")

    def run_consolidation_pipeline(self):
        print("🌙 Starting Consolidation Pipeline...")
        
        full_text, turn_ids = self.get_unprocessed_sessions()
        if not full_text:
            print("✨ No new turns in STM to process.")
            return

        print(f"Processing STM records ({len(full_text)} chars)...")
        
        self.step_semantic_extraction(full_text)
        print("✅ Finished Semantic Extraction")
        self.step_update_identity(full_text)
        print("✅ Finished Identity Update")
        self.step_generate_handoff(full_text)
        print("✅ Finished Continuity Handoff")
        self.step_dream(full_text)
        print("✅ Finished Dream Generation")
        
        print("\n✨ Consolidation Complete.")
        self.mark_turns_consolidated(turn_ids)
        
if __name__ == "__main__":
    from backend.core.config import settings
    from backend.agent.embedding_service import EmbeddingService
    
    cortex = Cortex(api_key=settings.api_key, model_name=settings.model_name)
    embedding_service = EmbeddingService(api_key=settings.api_key)
    hippocampus = Hippocampus(embedding_service=embedding_service)
    
    sc = SleepCycle(cortex=cortex, hippocampus=hippocampus)
    sc.run_consolidation_pipeline()
