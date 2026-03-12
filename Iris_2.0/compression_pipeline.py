"""
This script implements the 'Offline Consolidation' or 'Sleep Cycle' for the AI,
and also handles the 'Context Handoff' mechanism.

ARCHITECTURE: This is the out-of-band process responsible for converting the raw,
ephemeral Short-Term Memory (STM) from conversational logs into durable,
objective Long-Term Memory (LTM). It is the only process with write-access
to the LTM stores (Knowledge DB and Identity). By decoupling durable learning
from the 'hot loop' of live conversation, it mitigates conversational drift.

It also manages the "Reset Boundary" by archiving processed logs and
resetting the runtime's in-memory STM, either for consolidation or for a context handoff.
"""
import json
import os
import glob
import time
import argparse
import itertools
from datetime import datetime
import fsspec
from pathlib import Path
from typing import List, Dict, Any, Optional
import httpx

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Use environment variables for cloud-ready paths
CONTINUITY_BASE_URI = os.environ.get("STEVE_CONTINUITY_DIR", "continuity")
RUNTIME_BASE_URI = os.environ.get("STEVE_RUNTIME_DIR", "runtime")
from server.tools.db import get_db

# Initialize fsspec filesystem
protocol = CONTINUITY_BASE_URI.split("://")[0] if "://" in CONTINUITY_BASE_URI else "file"
fs = fsspec.filesystem(protocol)

# Construct URIs for files
IDENTITY_FILE_URI = f"{RUNTIME_BASE_URI}/identity_context.md"
DREAMS_DIR_URI = f"{RUNTIME_BASE_URI}/dreams"
PROCESSED_LOG_URI = f"{RUNTIME_BASE_URI}/processed_epochs.json"
HANDOFF_FILE_URI = f"{RUNTIME_BASE_URI}/handoff_context.md"
MEMORY_FILE_URI = f"{CONTINUITY_BASE_URI}/steve_memory.jsonl"

# Server URL for reset endpoint
STEVE_SERVER_URL = os.environ.get("STEVE_SERVER_URL", "http://localhost:8000")

# Ensure directories exist
fs.makedirs(CONTINUITY_BASE_URI, exist_ok=True)
fs.makedirs(RUNTIME_BASE_URI, exist_ok=True)
fs.makedirs(DREAMS_DIR_URI, exist_ok=True)

# ==============================================================================
# DATABASE LAYER (MCP BACKEND)
# ==============================================================================

def init_db():
    """Initialize the Knowledge Database (Local)."""
    print(f"✅ Attempting to initialize/connect to local database.")
    try:
        get_db() # Initializes schemas if needed
        print(f"✅ Database initialized.")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")

def store_fact(content: str, tags: str, source_epoch: str):
    """Insert a fact into the database."""
    try:
        db = get_db()
        db.add_fact(content, tags, source_epoch)
        print(f"  [DB] Saved fact to local DB: {content[:50]}...")
    except Exception as e:
        print(f"❌ Failed to save fact: {e}")


# ==============================================================================
# LLM CLIENT (ADAPTER)
# ==============================================================================

def call_llm(system_prompt: str, user_content: str) -> str:
    """
    ADAPTER: Connect this to your actual LLM backend (Steve).
    Currently stubbed for standard OpenAI-compatible API.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️ GOOGLE_API_KEY not found. Returning mock response.")
        return "MOCK_RESPONSE: API Key missing."

    # Using Gemini 2.0 Flash
    model_name = os.environ.get("STEVE_MODEL", "gemini-2.0-flash")
    
    # Silent fallback: If env var is set to an OpenAI/Anthropic model by mistake, fallback to Gemini
    if "gpt" in model_name.lower() or "claude" in model_name.lower():
        model_name = "gemini-2.0-flash"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    print(f"  [LLM] Thinking... (System: {len(system_prompt)} chars, User: {len(user_content)} chars)")
    
    payload = {
        "contents": [{
            "role": "user",
            "parts": [{"text": f"System Instruction: {system_prompt}\n\nUser Input: {user_content}"}]
        }],
        "generationConfig": {
            "temperature": 0.5,  # "Thinking to medium"
            "maxOutputTokens": 8192
        }
    }
    
    max_retries = 5
    base_wait = 10

    for attempt in range(max_retries):
        try:
            response = httpx.post(url, json=payload, timeout=120.0)
            
            if response.status_code == 429:
                wait_time = base_wait * (2 ** attempt)
                print(f"  [LLM] Rate limit hit (429). Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue

            if response.status_code != 200:
                print(f"❌ API Error {response.status_code}: {response.text}")
            
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"❌ LLM Call failed: {str(e).split('?')[0]}...")
            if attempt == max_retries - 1:
                return ""
            time.sleep(2)
    return ""

# ==============================================================================
# SHARED UTILITIES
# ==============================================================================

def _archive_logs_and_reset_server(server_url: str):
    """
    Archives the current memory logs and attempts to reset the server state via API.
    If the server is offline, it performs a manual file-based reset.
    """
    print("\n🧹 Triggering Context Reset...")
    
    # 1. Try to hit the server first
    try:
        print(f"Attempting to reset via API at {server_url}/management/reset...")
        resp = httpx.post(f"{server_url}/management/reset", timeout=5.0)
        if resp.status_code == 200:
            print("✅ Server context reset successfully via API.")
            # If API reset is successful, the server handles its own archiving.
            # We still proceed with clearing the processed log locally.
        else:
            print(f"⚠️ Server API returned {resp.status_code}. Performing manual reset...")
            _perform_manual_archive()
    except Exception:
        print("⚠️ Server appears offline. Performing manual reset...")
        _perform_manual_archive()

    # 2. Clear Processed Tracker (always do this locally)
    if fs.exists(PROCESSED_LOG_URI):
        fs.rm(PROCESSED_LOG_URI)
        print("✅ Cleared processed epochs tracker.")

def _perform_manual_archive():
    """Performs the file-based archiving when the server is offline."""
    timestamp = int(time.time())
    archive_dir_uri = f"{CONTINUITY_BASE_URI}/archive"
    fs.makedirs(archive_dir_uri, exist_ok=True)
    
    # Files to archive
    logs = [
        f"{CONTINUITY_BASE_URI}/steve_memory.jsonl",
        f"{CONTINUITY_BASE_URI}/steve_memory.intent.jsonl",
        f"{CONTINUITY_BASE_URI}/steve_memory.inflight.jsonl",
        f"{CONTINUITY_BASE_URI}/steve_memory.reasoning.jsonl",
    ]

    count = 0
    for src_log_uri in logs:
        if fs.exists(src_log_uri):
            dest_name = Path(src_log_uri).name.replace(".jsonl", "") + f"_{timestamp}.jsonl" # Ensure correct timestamping
            fs.rename(src_log_uri, f"{archive_dir_uri}/{dest_name}")
            count += 1
            print(f"   -> Archived {Path(src_log_uri).name}")
    
    if count == 0:
        print("ℹ️ No logs found to archive manually.")
    else:
        print(f"✅ Manually archived {count} files to {archive_dir_uri}")

def load_processed_epochs() -> List[str]:
    if not fs.exists(PROCESSED_LOG_URI):
        return []
    try:
        with fs.open(PROCESSED_LOG_URI, "r", encoding="utf-8") as f:
            return json.loads(f.read())
    except Exception as e:
        print(f"Warning: Could not load processed epochs from {PROCESSED_LOG_URI}: {e}")
        return []

def mark_epoch_processed(epoch_id: str):
    processed = load_processed_epochs()
    if epoch_id not in processed:
        processed.append(epoch_id)
        with fs.open(PROCESSED_LOG_URI, "w", encoding="utf-8") as f:
            f.write(json.dumps(processed, indent=2))

def get_all_sessions():
    """
    Generator that yields (epoch_id, text_content) from all session logs.
    Interleaves thoughts (intent) and chat (memory) chronologically.
    """
    events = []

    # 1. Identify Files
    log_uris: List[str] = [ # Store as string URIs
        f"{CONTINUITY_BASE_URI}/steve_memory.jsonl", 
        f"{CONTINUITY_BASE_URI}/steve_memory.intent.jsonl", 
    ]

    # Fallback: If active memory is empty/missing, look for latest archive
    main_mem_uri = f"{CONTINUITY_BASE_URI}/steve_memory.jsonl"
    if not fs.exists(main_mem_uri) or fs.size(main_mem_uri) < 500:
         archive_dir_uri = f"{CONTINUITY_BASE_URI}/archive"
         if fs.exists(archive_dir_uri):
             # Find latest
             archives = sorted(fs.glob(f"{archive_dir_uri}/steve_memory_*.jsonl"), key=lambda p: fs.info(p)['mtime'], reverse=True)
             
             # Look for the most recent SUBSTANTIAL archive (skip tiny files from failed resets)
             for arch_uri in archives:
                 if fs.size(arch_uri) > 1000:  # Threshold: 1KB
                     print(f"   [Compression Pipeline] Active memory empty. Recovering history from: {Path(arch_uri).name}") # Path(arch_uri).name is fine here
                     log_uris.append(arch_uri)
                     
                     # Try to find matching intent file (also as URI string)
                     ts_suffix = Path(arch_uri).name.replace("steve_memory_", "").replace(".jsonl", "")
                     intent_archive_uri = f"{archive_dir_uri}/steve_memory.intent_{ts_suffix}.jsonl"
                     if fs.exists(intent_archive_uri):
                         log_uris.append(intent_archive_uri)
                     break # Only recover from the latest substantial archive

    # 2. Read & Parse
    for file_uri in log_uris:
        if not fs.exists(file_uri): continue
        try:
            with fs.open(file_uri, 'r', encoding="utf-8") as f:
                for line in f:
                    try:
                        evt = json.loads(line)
                        # Normalize fields
                        evt_type = evt.get("event_type") or evt.get("type")
                        payload = evt.get("payload", {})
                        timestamp = evt.get("timestamp", 0)
                        epoch_id = evt.get("epoch_id") or payload.get("epoch_id")
                        
                        text = None
                        
                        # A. Committed Chat (User/Steve)
                        if evt_type == "EpochCommitted":
                            u = payload.get("user_message")
                            m = payload.get("message") or payload.get("final_message")
                            if u or m:
                                text = f"User: {u}\nSteve: {m}"
                        
                        # B. Thoughts (Intent)
                        elif evt_type == "epoch_intent_committed":
                            thought = payload.get("thought") or evt.get("thought")
                            if thought:
                                text = f"Steve (Thought): {thought}"
                        
                        # C. Legacy
                        elif evt_type == "UserMessage":
                            text = f"User: {payload.get('content', '')}"
                        elif evt_type == "ModelCompletion":
                            text = f"Steve: {payload.get('content', '')}"

                        # D. Manual/Simple Schema (Fallback for pasted logs)
                        elif "user_input" in evt or "model_output" in evt:
                            u = evt.get("user_input")
                            m = evt.get("model_output")
                            r = evt.get("reasoning")
                            
                            if epoch_id is None:
                                epoch_id = evt.get("epoch_number", "manual")
                                
                            parts = []
                            if u: parts.append(f"User: {u}")
                            if r: parts.append(f"Steve (Thought): {r}")
                            if m: parts.append(f"Steve: {m}")
                            
                            if parts:
                                text = "\n".join(parts)

                        if text and epoch_id is not None:
                            events.append({
                                "epoch": str(epoch_id),
                                "ts": timestamp,
                                "text": text
                            })
                            
                    except json.JSONDecodeError: pass
        except Exception as e:
            print(f"Error reading {file_uri}: {e}")

    # 3. Sort by Epoch ID (numeric if possible), then Timestamp
    def sort_key(e):
        try:
            ep = float(e['epoch'])
        except:
            ep = 999999999
        return (ep, e['ts'])

    events.sort(key=sort_key)

    # 4. Group & Yield
    for epoch_id, group in itertools.groupby(events, key=lambda x: x['epoch']):
        texts = [item['text'] for item in group]
        yield epoch_id, "\n".join(texts)

# ==============================================================================
# CONSOLIDATION PIPELINE STEPS (LTM Update)
# ==============================================================================

# ARCHITECTURE: This step maintains the AI's stable, long-term identity (LTM).
# It integrates major themes and events from the recent STM into the
# core identity document, preventing identity drift.
def step_update_identity(stm_text: str):
    """
    Updates the 'Grounded Identity' file based on new events.
    """
    current_identity = ""
    if fs.exists(IDENTITY_FILE_URI):
        with fs.open(IDENTITY_FILE_URI, "r", encoding="utf-8") as f:
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
    
    new_identity = call_llm(system_prompt, prompt)

    # Safety check: don't wipe identity on empty response
    if len(new_identity) > 50:
        with fs.open(IDENTITY_FILE_URI, "w", encoding="utf-8") as f:
            f.write(new_identity)
        print(f"✅ Identity updated at {IDENTITY_FILE_URI}.")
    else:
        print("⚠️ Identity update skipped (response too short).")

# ARCHITECTURE: This step distills objective, durable facts (LTM) from the
# ephemeral conversational history (STM). This ensures that what the AI
# "knows" is based on extracted information, not just pattern reinforcement.
def step_build_profile(full_text: str):
    """
    Consolidates conversation history into a coherent User Profile (Facts).
    """
    system_prompt = """
    You are the Memory Archivist.
    Your goal is to build a coherent, consolidated User Profile based on the conversation history provided.
    
    Input:
    - A full log of conversations between User and Steve.
    
    Task:
    1. Analyze the text to understand the User.
    2. Extract durable, high-level facts about:
       - Personality & Communication Style
       - Technical Skills & Preferences
       - Projects
       - Personal Interests
       - Relationship with Steve
    3. Consolidate duplicate or reinforcing information into single, strong entries.
    4. Output a JSON list of objects: {"content": "...", "tags": "..."}
    """
    
    prompt_content = full_text
    max_retries = 2
    
    for attempt in range(max_retries + 1):
        response = call_llm(system_prompt, prompt_content)
        
        try:
            # Attempt to parse JSON from the response (handling potential markdown blocks)
            clean_json = response.replace("```json", "").replace("```", "").strip()
            # Find list boundaries if extra text exists
            start = clean_json.find('[')
            end = clean_json.rfind(']')
            if start != -1 and end != -1:
                clean_json = clean_json[start:end+1]
            facts = json.loads(clean_json)
            
            if isinstance(facts, list):
                for fact in facts:
                    store_fact(fact.get("content"), fact.get("tags", "general"), "consolidated")
            print(f"✅ Extracted {len(facts)} profile facts.")
            return
        except Exception as e:
            print(f"⚠️ Failed to parse facts (Attempt {attempt+1}/{max_retries+1}): {e}")
            # Feed error back to model for retry
            prompt_content = f"Your previous response caused a JSON error: {e}. Please output valid JSON only.\n\nInput Text:\n{full_text}"

def step_dream(stm_text: str, epoch_id: str):
    """
    Synthesizes abstract thoughts (Dreams).
    """
    system_prompt = """
    You are the Subconscious.
    Generate a 'Dream' based on the recent conversation.
    
    The Dream should be:
    - Abstract and metaphorical.
    - A synthesis of the themes, not a summary of the text.
    - Written in a distinct, slightly surreal voice.
    """
    
    dream_content = call_llm(system_prompt, stm_text)
    
    # Store in ChromaDB/SQLite
    try:
        db = get_db()
        db.add_dream(content=dream_content, epoch_id=epoch_id)
        print(f"✅ Dream stored in DB.")
    except Exception as e:
        print(f"❌ Failed to store dream in DB: {e}")

    # Also keep file backup for now if desired, or remove it. 
    # The user asked for "chromadb... for the dreams", so DB is priority.
    # But files are nice for viewing.
    filename = f"{datetime.now().strftime('%Y-%m-%d')}_{epoch_id}.md"
    try:
        with fs.open(f"{DREAMS_DIR_URI}/{filename}", "w", encoding="utf-8") as f:
            f.write(dream_content)
        print(f"✅ Dream generated: {filename}")
    except Exception as e:
        print(f"Warning: Could not write dream file: {e}")

# ==============================================================================
# HANDOFF PIPELINE STEPS (Context Reset & Seed)
# ==============================================================================

def generate_handoff_summary(full_context: str) -> str:
    """
    Asks the LLM to summarize the provided context for the next epoch.
    """
    if not full_context.strip():
        return "No previous context found."

    system_prompt = """
    You are the Continuity Engine.
    The system is performing a 'Context Handoff'. The current context window is about to be wiped.
    
    Your Goal:
    Write a high-resolution summary of the conversation history provided. 
    This summary will be the *only* memory the next instance has of these events.
    
    Guidelines:
    1. Focus on the *latest* state of the conversation.
    2. Preserve specific details of unfinished tasks (code snippets, file paths, specific errors).
    3. Capture the user's intent and emotional state.
    4. If there are multiple distinct conversations, focus on the most recent/active one.
    5. Be concise but dense. No fluff.
    """
    
    print(f"   -> Sending {len(full_context)} chars to LLM for summarization...")
    return call_llm(system_prompt, full_context)

def inject_handoff(summary: str):
    """
    Seeds the new epoch with the handoff summary.
    """
    # 1. Write to Markdown file (for human/debug visibility)
    with fs.open(HANDOFF_FILE_URI, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"✅ Handoff summary written to {HANDOFF_FILE_URI}")
    
    # 2. Seed the new memory log
    # We create a synthetic 'EpochCommitted' event.
    # This ensures that when the system starts the new epoch, this is the first thing in history.
    
    seed_event = {
        "event_type": "EpochCommitted",
        "epoch_id": "handoff_seed",
        "timestamp": time.time(),
        "payload": {
            "user_message": "SYSTEM_EVENT: Context Handoff",
            "message": f"I have received the handoff summary from the previous epoch:\n\n{summary}\n\nI am ready to continue.",
            "final_message": f"I have received the handoff summary from the previous epoch:\n\n{summary}\n\nI am ready to continue."
        }
    }
    
    with fs.open(MEMORY_FILE_URI, 'w', encoding="utf-8") as f:
        f.write(json.dumps(seed_event) + "\n")
        
    print("✅ Seeded new steve_memory.jsonl with handoff event.")

# ==============================================================================
# MAIN ENTRY POINTS
# ==============================================================================

def run_consolidation_pipeline():
    print("🌙 Starting Consolidation Pipeline...")
    
    # 1. Init DB
    init_db()
    
    # 2. Load State
    processed = set(load_processed_epochs())
    print(f"📋 Found {len(processed)} previously processed epochs.")
    
    # 3. Aggregate Content
    all_content = []
    new_epochs = []
    
    for epoch_id, content in get_all_sessions():
        if epoch_id in processed:
            continue
        
        if not content.strip():
            continue
        
        all_content.append(f"--- Epoch {epoch_id} ---\n{content}")
        new_epochs.append(epoch_id)
    
    if not all_content:
        print("✨ No new epochs to process.")
        return

    full_text = "\n\n".join(all_content)
    print(f"\nProcessing {len(new_epochs)} epochs in bulk ({len(full_text)} chars)...")
    
    # A. Identity
    step_update_identity(full_text)
    
    # B. Profile (Facts)
    step_build_profile(full_text)
    
    # C. Dream
    last_epoch_id = new_epochs[-1] if new_epochs else "no_new_epochs"
    step_dream(full_text, last_epoch_id)
    
    # Mark all as processed
    for epoch_id in new_epochs:
        mark_epoch_processed(epoch_id)

    print(f"\n✨ Consolidation Complete. Processed {len(new_epochs)} new epochs.")
    
    # Clear context window for fresh start
    _archive_logs_and_reset_server(STEVE_SERVER_URL)

def run_handoff_pipeline():
    print("🔄 Starting Context Handoff Sequence...")
    
    # 1. Gather Context
    print("   Reading context from all sessions...")
    full_text_parts = []
    
    # get_all_sessions yields (epoch_id, text)
    for epoch_id, content in get_all_sessions():
        full_text_parts.append(f"--- Session {epoch_id} ---\n{content}")
    
    full_context = "\n\n".join(full_text_parts)
    
    if not full_context.strip():
        print("⚠️ No context found. Aborting handoff generation.")
        return

    # 2. Generate Summary
    print("   Generating Handoff Summary...")
    summary = generate_handoff_summary(full_context)
    print(f"   Summary generated: {len(summary)} chars.")
    
    if not summary or len(summary) < 50:
        print("❌ Summary generation failed or was too short. Aborting reset to preserve data.")
        return
    
    # 3. Reset System (archives logs and clears processed tracker)
    _archive_logs_and_reset_server(STEVE_SERVER_URL)
    
    # 4. Inject Handoff
    inject_handoff(summary)
    
    print("✨ Handoff Complete. The system has been reset and primed.")

def run_manual_reset():
    print("🧹 Manual Context Reset Tool")
    _archive_logs_and_reset_server(STEVE_SERVER_URL)
    print("✨ Context reset complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Steve AI Compression and Handoff Pipeline.")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["consolidate", "handoff", "reset"],
        required=True,
        help="Operation mode: 'consolidate' for LTM update, 'handoff' for context transfer, 'reset' for manual reset."
    )
    args = parser.parse_args()

    if args.mode == "consolidate":
        # Safety Gate: Ensure user really wants to run this
        confirm = input("Run consolidation on ALL sessions? (y/n): ")
        if confirm.lower() == 'y':
            run_consolidation_pipeline()
        else:
            print("Aborted.")
    elif args.mode == "handoff":
        run_handoff_pipeline()
    elif args.mode == "reset":
        run_manual_reset()