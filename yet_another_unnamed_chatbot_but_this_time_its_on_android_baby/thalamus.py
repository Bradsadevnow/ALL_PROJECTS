import datetime
import os
import uuid
import logging
from typing import Dict, Any, Tuple

from backend.db.engine import SessionLocal
from backend.db.models import Turn

logger = logging.getLogger(__name__)

class Thalamus:
    def __init__(self, cortex, hippocampus, embedding_service):
        self.cortex = cortex
        self.hippocampus = hippocampus
        self.embedding_service = embedding_service
        self.cortex.hippocampus = hippocampus
        logger.info("Thalamus initialized. Cortex and Hippocampus bound.")

    def log_turn(self, turn_data: dict) -> None:
        """Saves the turn to the SQLAlchemy SQLite STM Database."""
        db = SessionLocal()
        try:
            db_turn = Turn(
                id=turn_data["turn_id"],
                timestamp=turn_data["timestamp"],
                user_query=turn_data.get("user_query", ""),
                reflection=turn_data.get("reflection", ""),
                response=turn_data.get("response", ""),
                state=turn_data.get("state", {}),
                keywords=turn_data.get("keywords", []),
                memories_used=turn_data.get("memories_used", 0),
                memory_ids_used=turn_data.get("memory_ids_used", []),
                prompt_version=turn_data.get("prompt_version", "1.0")
            )
            db.add(db_turn)
            db.commit()
            logger.info(f"🧾 Logged turn {turn_data['turn_id']} to STM Database.")
        except Exception as e:
            db.rollback()
            logger.error(f"⚠️ STM Logging failed: {e}")
        finally:
            db.close()

    def get_recent_turns(self, n=3) -> list:
        """Fetches the most recent N turns from the SQLite STM Database."""
        db = SessionLocal()
        try:
            turns = db.query(Turn).filter(Turn.is_consolidated == False).order_by(Turn.timestamp.desc()).limit(n).all()
            return [
                {
                    "turn_id": t.id,
                    "timestamp": t.timestamp,
                    "user_query": t.user_query,
                    "reflection": t.reflection,
                    "response": t.response,
                    "state": t.state,
                    "keywords": t.keywords,
                    "memories_used": t.memories_used,
                    "memory_ids_used": t.memory_ids_used,
                    "prompt_version": t.prompt_version
                }
                for t in turns
            ][::-1] # Reverse to get chronological order (oldest first within the window)
        except Exception as e:
            logger.error(f"⚠️ Failed to fetch recent turns from STM: {e}")
            return []
        finally:
            db.close()

    def process_turn(self, user_query: str, task_id: str = "REST_API") -> Tuple[dict, str, str]:
        turn_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()
        
        logger.info(f"--- TURN {turn_id} INITIATED ---")
        logger.info(f"User Query: {user_query}")
        
        # Clear embedding cache for new turn
        self.embedding_service.clear_cache()

        # 1. Feel and Reflect
        try:
            state, reflection, keywords, questions = self.cortex.feel_and_reflect(user_query, turn_id, timestamp)
            if state is None:
                raise ValueError("Reflection phase returned None.")
        except Exception as e:
            logger.error(f"Reflection phase crashed: {e}")
            return {}, "(reflection phase failed)", "I experienced an internal error during reflection."

        # 2. Recall Memories
        logger.info("Recalling memories...")
        memories = self.hippocampus.recall_with_context(user_query, keywords=keywords, n_results=10)

        # 3. Retrieve STM Context
        logger.info("Fetching recent turns from STM database...")
        recent_turns = self.get_recent_turns(n=3)

        # 4. Generate Final Response
        logger.info("Generating response...")
        response_data = self.cortex.respond(
            user_query=user_query,
            state=state,
            reflection=reflection,
            recent_turns=recent_turns,
            memories=memories
        )

        response_text = response_data.get("response", response_data.get("raw", ""))
        # The AI may have drifted its state during the synthesis phase, capture it
        final_state = response_data.get("state", state) 
        final_reflection = response_data.get("reflection", reflection)
        final_keywords = response_data.get("keywords", keywords)

        turn_data = {
            "turn_id": turn_id,
            "task_id": task_id,
            "timestamp": timestamp,
            "user_query": user_query,
            "reflection": final_reflection,
            "response": response_text,
            "state": final_state or {},
            "keywords": final_keywords or [],
            "memories_used": len(memories),
            "memory_ids_used": [m.get("memory_id", m.get("id")) for m in memories],
            "prompt_version": self.cortex.prompt_version
        }

        # 5. Log to STM
        self.log_turn(turn_data)

        # 6. Delayed Commit to LTM
        try:
            self.hippocampus.delayed_commit(
                user_query=user_query,
                reflection=final_reflection,
                response=response_text,
                state_json=final_state,
                metadata={
                    "turn_id": turn_id,
                    "task_id": task_id,
                    "keywords": final_keywords or [],
                },
            )
        except Exception as e:
            logger.error(f"Memory commit failed: {e}")

        logger.info(f"--- TURN {turn_id} COMPLETED ---")
        return final_state, final_reflection, response_text
