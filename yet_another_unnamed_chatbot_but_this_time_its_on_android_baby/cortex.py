import os
import json
import re
import logging
import urllib.request
import urllib.parse
from google import genai
from google.genai import types
import datetime

from .prompts import (
    SYSTEM_PROMPT,
    STRICT_OUTPUT_EXAMPLE,
    EMOTIVE_STATES,
    COGNITIVE_STATES,
    MEMORY_RECALL_INSTRUCTION,
    FINAL_RESPONSE_INSTRUCTION,
    QUESTION_INSTRUCTION,
    PROMPT_VERSION
)

logger = logging.getLogger(__name__)

def get_wikipedia_image(query: str) -> str:
    """Finds an image URL from Wikipedia for the given query."""
    try:
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json"
        req = urllib.request.Request(search_url, headers={'User-Agent': 'SteveAgent/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data.get("query", {}).get("search"):
                title = data["query"]["search"][0]["title"]
                img_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles={urllib.parse.quote(title)}"
                req2 = urllib.request.Request(img_url, headers={'User-Agent': 'SteveAgent/1.0'})
                with urllib.request.urlopen(req2) as resp2:
                    data2 = json.loads(resp2.read().decode())
                    pages = data2.get("query", {}).get("pages", {})
                    for page_id, page_data in pages.items():
                        if "original" in page_data:
                            return page_data["original"]["source"]
    except Exception as e:
        return f"Error: {e}"
    return "No image found."
class Cortex:
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.prompt_version = PROMPT_VERSION
        self.refresh_system_prompt()

        logger.info(f"Initializing Cortex with Gemini model: {self.model_name}")

    def refresh_system_prompt(self):
        """Loads identity and continuity context from disk and updates the system prompt."""
        runtime_dir = os.getenv("STEVE_RUNTIME_DIR", "runtime")
        identity_path = os.path.join(runtime_dir, "identity_context.md")
        continuity_path = os.path.join(runtime_dir, "continuity_context.md")
        
        identity = "I am Steve. An evolving AI entity."
        continuity = "No current conversational handoff summary available."
        
        try:
            if os.path.exists(identity_path):
                with open(identity_path, "r", encoding="utf-8") as f:
                    identity = f.read().strip()
            
            if os.path.exists(continuity_path):
                with open(continuity_path, "r", encoding="utf-8") as f:
                    continuity = f.read().strip()
        except Exception as e:
            logger.error(f"Failed to load context files: {e}")

        # Format the template from prompts.py using safer replacement
        self.system_prompt = SYSTEM_PROMPT.replace("{identity}", identity).replace("{continuity}", continuity)
        logger.debug("System prompt refreshed with dynamic identity and continuity.")

    def _extract_sections(self, raw: str):
        """Parse the LLM output into state, reflection, and keyword sections."""
        text = raw or ""
        norm = re.sub(r'```.*?```', '', text, flags=re.S).strip()

        # --- REFLECTION ---
        refl = ""
        m_refl = re.search(r'REFLECTION\s*:\s*(.+?)(?:\n[A-Z ]{3,}?:|\Z)', norm, flags=re.S | re.I)
        if m_refl:
            refl = m_refl.group(1).strip()

        # --- KEYWORDS ---
        kws = []
        m_kw = re.search(r'KEYWORDS\s*:\s*(.+?)(?:\n[A-Z ]{3,}?:|\Z)', norm, flags=re.S | re.I)
        if m_kw:
            blob = m_kw.group(1).strip()
            blob = re.sub(r'^\[|\]$', '', blob).strip()
            parts = re.split(r'[,\n]', blob)
            kws = [p.strip() for p in parts if p.strip()]

        # --- STATE ---
        state = {"emotions": []}
        m_state = re.search(r'STATE\s*:\s*(\{[\s\S]*?\})', norm, flags=re.I)
        parsed = None
        if m_state:
            obj_str = m_state.group(1).strip()
            try:
                parsed = json.loads(obj_str)
            except Exception:
                try:
                    obj_str_fixed = re.sub(r',\s*}', '}', obj_str)
                    obj_str_fixed = re.sub(r',\s*\]', ']', obj_str_fixed)
                    parsed = json.loads(obj_str_fixed)
                except Exception:
                    parsed = None

        # --- QUESTIONS ---
        questions = {}
        m_q = re.search(r'QUESTIONS\s*:\s*(\{[\s\S]*?\})', norm, flags=re.S | re.I)
        if m_q:
            q_str = m_q.group(1).strip()
            try:
                questions = json.loads(q_str)
            except Exception as e:
                logger.warning(f"Failed to parse QUESTIONS JSON: {e}")
                questions = {}

        def _to_states(d):
            all_states = []
            if not isinstance(d, dict):
                return all_states
            for i in range(1, 4):
                n = d.get(f"emo_{i}_name")
                v = d.get(f"emo_{i}_intensity")
                if n and v is not None:
                    try:
                        all_states.append({"name": str(n), "intensity": float(v), "type": "emotive"})
                    except Exception:
                        pass
            for i in range(1, 4):
                n = d.get(f"cog_{i}_name")
                v = d.get(f"cog_{i}_intensity")
                if n and v is not None:
                    try:
                        all_states.append({"name": str(n), "intensity": float(v), "type": "cognitive"})
                    except Exception:
                        pass
            return all_states
        
        if parsed:
            state["emotions"] = _to_states(parsed)

        if not state["emotions"]:
            state["emotions"] = [{"name": "Focus", "intensity": 0.6, "type": "cognitive"}]
            
        return state, refl, kws, questions

    def feel_and_reflect(self, user_query: str, turn_id: str, timestamp: str):
        self.refresh_system_prompt()
        msg = (
            f"{MEMORY_RECALL_INSTRUCTION}\n\n"
            f"***VALID EMOTIVE STATES***: {', '.join(EMOTIVE_STATES)}\n"
            f"***VALID COGNITIVE STATES***: {', '.join(COGNITIVE_STATES)}\n\n"
            f"Time: {timestamp}\nTurn: {turn_id}\nUser: {user_query}"
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=msg,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    temperature=0.6,
                )
            )
            raw_text = response.text
            
            logger.debug(f"Feel and Reflect raw output:\n{raw_text}")
            
            state, reflection, keywords, questions = self._extract_sections(raw_text)
                
            return state, reflection, keywords, questions
            
        except Exception as e:
            logger.error(f"Reflection phase crashed: {e}")
            return None, None, [], {}

    def respond(self, user_query: str, state: dict, reflection: str, recent_turns: list, memories: list):
        self.refresh_system_prompt()
        recent = (recent_turns or [])[-3:]
        short_context = "\n\n".join([
            f"User: {t.get('user_query', '')}\nSteve: {t.get('response', '')}"
            for t in recent
        ]) or "(no recent turns)"

        memory_context = "\n".join([
            f"- {m.get('text', str(m))[:300]}" for m in (memories or [])[:20]
        ]) or "(no relevant memories retrieved)"

        msg = f"""
[CONVERSATIONAL CONTINUITY]
{short_context} THESE PAST EXCHANGES SHOULD INFORM YOUR UNDERSTANDING OF THE CURRENT CONTEXT AND TONE.

[MEMORY CONTEXT]
{memory_context}

[CURRENT STATE (FROM REFLECTION)]
{json.dumps(state, indent=2)}

[REFLECTION]
{reflection}

{FINAL_RESPONSE_INSTRUCTION}

***VALID EMOTIVE STATES***: {', '.join(EMOTIVE_STATES)}
***VALID COGNITIVE STATES***: {', '.join(COGNITIVE_STATES)}

{STRICT_OUTPUT_EXAMPLE}

User query: {user_query}

[SYSTEM INFORMATION]
Current System Time: {datetime.datetime.now().isoformat()}

***THIS IS NOT YOUR FIRST OR LAST INTERACTION WITH THE USER. USE ALL OF THE CONTEXT PROVIDED TO RESPOND COHERENTLY AND MAINTAIN CONTINUITY.
***
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=msg,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    temperature=0.7,
                    tools=[
                        types.Tool(function_declarations=[
                            types.FunctionDeclaration(
                                name="get_wikipedia_image",
                                description="Finds an image URL from Wikipedia for the given query.",
                                parameters=types.Schema(
                                    type="OBJECT",
                                    properties={
                                        "query": types.Schema(type="STRING")
                                    },
                                    required=["query"]
                                )
                            )
                        ])
                    ]
                )
            )
            raw_text = response.text
            
            if "STATE:" in raw_text and "REFLECTION:" in raw_text:
                state_json, reflection_primary, keywords, questions = self._extract_sections(raw_text)
                
                final_res = raw_text
                m_res = re.search(r'RESPONSE\s*:\s*(.*)', raw_text, flags=re.S | re.I)
                if m_res:
                    final_res = m_res.group(1).strip()
                    
                return {
                    "state": state_json,
                    "reflection": reflection_primary,
                    "keywords": keywords,
                    "questions": questions,
                    "response": final_res,
                    "raw": raw_text.strip()
                }

            return {"state": state, "reflection": reflection, "keywords": [], "questions": {}, "raw": raw_text.strip()}
            
        except Exception as e:
            logger.error(f"Response phase crashed: {e}")
            return {"state": state, "reflection": reflection, "keywords": [], "questions": {}, "raw": "(Response Generation Failed)"}
