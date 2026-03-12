import os
import json
import time
from typing import List, Dict, Any
from google import genai
from pydantic import BaseModel

class IdentityRefinement(BaseModel):
    operating_principles: str
    recent_learnings: str
    dream_fragment: str

class IdentityRefiner:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = genai.Client(api_key=self.api_key)
        self.runtime_dir = "runtime"
        self.identity_path = os.path.join(self.runtime_dir, "identity_context.md")
        self.dream_path = os.path.join(self.runtime_dir, "dream_fragment.md")

    def refine(self, history: List[Dict[str, Any]], current_identity: str):
        """
        Refines identity into its 3 sections and generates a dream fragment.
        """
        system_prompt = """
        You are the Identity Refiner for IRIS.
        
        Your task is to take the current Identity Context and the recent Epoch History, then output a structured refinement.
        
        CONSTRAINTS:
        1. PRIME INVARIANTS (Section 1) are IMMUTABLE. Do not suggest changes to them.
        2. OPERATING PRINCIPLES (Section 2) are SLOW-CHANGING. Only update if you detect a persistent shift in behavior or stance (80% confidence).
        3. RECENT LEARNINGS (Section 3) are MUTABLE. Rewrite this entirely to reflect the most critical developments, learnings, and current project context. STRICT CAP: 200 words.
        4. DREAM FRAGMENT: Distill the history into a surreal, 1-2 sentence metaphorical synthesis of the "vibe" and unresolved tensions.
        
        OUTPUT: You must return a JSON object matching this schema:
        {
          "operating_principles": "Refined Section 2 text",
          "recent_learnings": "Refined Section 3 text",
          "dream_fragment": "Metaphorical dream string"
        }
        """
        
        user_prompt = f"""
        CURRENT IDENTITY:
        {current_identity}
        
        RECENT HISTORY:
        {json.dumps(history, indent=2)}
        """
        
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config={
                'system_instruction': system_prompt,
                'response_mime_type': 'application/json',
                'response_schema': IdentityRefinement.model_json_schema()
            }
        )
        
        refinement = IdentityRefinement.model_validate_json(response.text)
        return refinement

    def execute_sleep_cycle(self, history: List[Dict[str, Any]]):
        """Perform the full Sleep Cycle: Refine Identity, Save Dream, Reset STM."""
        print("🌙 Starting Sleep Cycle (Consolidation)...")
        
        # 1. Load current identity
        if not os.path.exists(self.identity_path):
            print("❌ Identity file not found. Aborting.")
            return
            
        with open(self.identity_path, "r") as f:
            full_content = f.read()
            
        # Split into sections (rough markers)
        parts = full_content.split("## ")
        section_1 = "## " + parts[1] if len(parts) > 1 else "" # Prime Invariants
        
        # 2. Refine
        refinement = self.refine(history, full_content)
        
        # 3. Assemble New Identity
        new_identity = f"""# IRIS Identity Contract

{section_1.strip()}

## 2. Operating Principles (Slow-Changing)
{refinement.operating_principles}

## 3. Recent Learnings (Mutable, Capped)
{refinement.recent_learnings}
"""
        
        # 4. Write Files
        with open(self.identity_path, "w") as f:
            f.write(new_identity)
            
        with open(self.dream_path, "w") as f:
            f.write(refinement.dream_fragment)
            
        print("✅ Identity re-anchored.")
        print(f"✅ Dream synthesized: {refinement.dream_fragment}")
        return True

if __name__ == "__main__":
    # Test stub
    pass
