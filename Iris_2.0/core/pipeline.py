from google import genai
from google.genai import types
import json
import os
import time
from typing import List, Dict, Any, Optional
from core.lifecycle import IrisInternalVoice, EmotiveState
from memory.mtm import MediumTermMemory
from memory.tokens import TokenTracker

class IrisPipeline:
    def __init__(self, api_key: str, mtm: MediumTermMemory, tokens: TokenTracker):
        self.api_key = api_key
        self.mtm = mtm
        self.tokens = tokens
        self.client = genai.Client(api_key=self.api_key, http_options={'api_version': 'v1alpha'}) # or v1beta appropriately
        self.model_id = 'gemini-2.5-flash'
        self.persistence_dir = "persistence"
        self.runtime_dir = "runtime"
        self.dream_fragment_path = os.path.join(self.runtime_dir, "dream_fragment.md")
        self.identity_path = os.path.join(self.runtime_dir, "identity_context.md")

    async def execute(self, user_input: str, system_prompt: str, history: List[Dict[str, str]]) -> IrisInternalVoice:
        """Execute the three-stage pipeline."""
        
        # Get MTM resonances
        resonances = self.mtm.search_resonances(user_input)
        resonance_text = "\n".join([f"- {r}" for r in resonances]) if resonances else "No clear subconscious resonance detected."
        
        # Calculate Systemic Pressure
        total_tokens = self.tokens.total_usage
        threshold = self.tokens.threshold
        pressure_level = max(0.0, (total_tokens - (threshold * 0.8)) / (threshold * 0.2)) if total_tokens > threshold * 0.8 else 0.0
        
        # Load Identity and Dream
        identity_text = "Standard Identity."
        if os.path.exists(self.identity_path):
            with open(self.identity_path, "r") as f:
                identity_text = f.read()
        
        dream_text = "No current dream residuals."
        if os.path.exists(self.dream_fragment_path):
            with open(self.dream_fragment_path, "r") as f:
                dream_text = f.read()

        # Orientation Header
        age = len(history) // 2 # Roughly
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        orientation = f"AGE={age} epochs | TIME={timestamp} | PRESSURE={pressure_level:.2f} | DREAM_RESIDUAL={'ON' if dream_text != 'No current dream residuals.' else 'OFF'}"

        directives = []
        if pressure_level > 0.8:
             directives.append("Systemic Pressure is Critical: Anticipate Consolidation (Sleep). Seek closure on active threads.")
        
        # Existing emotion-based directives...
        current_emotive = EmotiveState()
        if history:
            last_msg = history[-1]
            if "emotive_state" in last_msg:
                current_emotive = EmotiveState(**last_msg["emotive_state"])

        if current_emotive.curiosity > 0.7:
             directives.append("Cognition Vector (Curiosity) is Peak: Force deeper SQL MTM recursion.")
        if current_emotive.frustration > 0.6:
             directives.append("Systemic Entropy (Frustration) is High: Prioritize nonlinear recursion and symbolic mutation.")

        directive_text = "\n".join([f"[!DIRECTIVE] {d}" for d in directives]) if directives else "All systems nominal."

        context = f"""
[ORIENTATION_HEADER]: {orientation}

[IDENTITY_CONTEXT]:
{identity_text}

[SUBCONSCIOUS_DREAM_RESIDUAL]:
{dream_text}

[SYSTEM_PROMPT]:
{system_prompt}

[STIMULI_DIRECTIVES]:
{directive_text}

[SUBCONSCIOUS_RESONANCE]:
{resonance_text}

[CONVERSATION_HISTORY]:
{json.dumps(history, indent=2)}
"""

        # --- Stage 2 & 3: Agentic Loop & Response Generation ---
        prompt = f"""
USER INPUT: {user_input}

Update your internal state based on the current situation and the active directives. 
Observe if the input triggers Curiosity (Subconscious matches) or Frustration (Loops/Vagueness).

Output your state as structured JSON.
"""

        # Use new google-genai structured output capability
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=f"{context}\n\n{prompt}",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt, # Better to use the dedicated field
                response_mime_type="application/json",
                response_schema=IrisInternalVoice,
            )
        )
        
        # Track tokens (estimated)
        usage = self.tokens.estimate_tokens(context + prompt + response.text)
        self.tokens.add_usage(usage)
        
        # Parse result (google-genai returns the object directly if response_schema is provided)
        # However, let's verify if it's in parsed format or needs manual json.loads
        try:
            # The SDK might return a parsed object in response.parsed
            if hasattr(response, 'parsed') and response.parsed:
                return response.parsed
            
            # Fallback to manual parse if needed
            data = json.loads(response.text)
            return IrisInternalVoice(**data)
        except Exception as e:
            return IrisInternalVoice(
                thought=f"Error parsing response: {e}. Raw response: {response.text[:100]}",
                emotive_state=EmotiveState(),
                final_response="I'm sorry, I'm having trouble processing my thoughts right now."
            )
