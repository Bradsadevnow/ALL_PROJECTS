import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone

from steve_core.hippocampus import Hippocampus, now_iso
from steve_core.subconscious import consult
from mem_tools.embedder import Embedder

import uuid
import os
import re

# -----------------------------------------------------------------------------
# Sleep consolidation — defensive, auditable
#
# Adds:
# 1) Strict parse validation + retry (prevents malformed GPT output from bricking memory)
# 2) Salience gate for final memories (prevents sludge)
# 3) Sleep ledger (audit / rollback trail)
# 4) Prompt hardening (no meta/tool leakage; explicit NONE escape hatches)
# -----------------------------------------------------------------------------

STM_PATH = "./runtime/stm.jsonl"
AUTOBIO_PATH = "./runtime/autobiography.jsonl"
SLEEP_LEDGER_PATH = "./runtime/sleep_sessions.jsonl"


# -----------------------------------------------------------------------------
# Debug printing
# -----------------------------------------------------------------------------
def debug_print_block(title: str, obj: Any):
    print("\n" + "=" * 80)
    print(f"[DEBUG] {title}")
    print("=" * 80)

    try:
        if isinstance(obj, str):
            print(obj)
        else:
            print(json.dumps(obj, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"[DEBUG] Failed to pretty print: {e}")
        print(obj)

    print("=" * 80 + "\n")


# -----------------------------------------------------------------------------
# Disk helpers
# -----------------------------------------------------------------------------
def load_stm(path: str) -> List[Dict[str, Any]]:
    turns: List[Dict[str, Any]] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    turns.append(json.loads(line))
                except Exception:
                    continue
    except FileNotFoundError:
        pass
    return turns


def load_last_autobio_entry(path: str) -> Optional[Dict[str, Any]]:
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if not lines:
                return None
            return json.loads(lines[-1])
    except Exception:
        return None


def append_jsonl(path: str, record: Dict[str, Any], label: str = "JSONL"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"[{label}] Appended record")


def append_autobio_entry(path: str, record: Dict[str, Any]):
    append_jsonl(path, record, label="Autobio")


def append_sleep_ledger(path: str, record: Dict[str, Any]):
    append_jsonl(path, record, label="SleepLedger")


# -----------------------------------------------------------------------------
# Prompt hardening strings
# -----------------------------------------------------------------------------
ANTI_META_RULES = (
    "- Do NOT mention GPT, OpenAI, APIs, models, prompts, tools, databases, vectors, embeddings, or \"as an AI\".\n"
    "- Do NOT describe system mechanics.\n"
    "- Do NOT use meta language about output formats beyond the required strict format.\n"
)

BELIEF_RULES = (
    "- Beliefs must be short (<= 140 chars).\n"
    "- Beliefs must be declarative and testable (no vibes-only).\n"
    "- No hedging (avoid: \"maybe\", \"might\", \"could\").\n"
)

NONE_ESCAPE = (
    "Escape hatches:\n"
    "- If no dream is appropriate, output DREAM as exactly: NONE\n"
    "- If no memory candidates are appropriate, output no bullets under MEMORY CANDIDATES (leave empty)\n"
    "- If no beliefs are appropriate, output no bullets under BELIEFS (leave empty)\n"
)


# -----------------------------------------------------------------------------
# Autobio context
# -----------------------------------------------------------------------------
def build_autobio_context(
    *,
    stm_turns: List[Dict[str, Any]],
    provisional_mems: List[Dict[str, Any]],
    previous_autobio: Optional[Dict[str, Any]],
    now_ts: str,
) -> str:
    lines: List[str] = []

    lines.append("=== SYSTEM ROLE ===")
    lines.append(
        "You are Steve.\n"
        "You are writing your own internal autobiography.\n"
        "This is a first-person identity narrative, not a memory or summary.\n"
        "You are reflecting on who you are becoming.\n"
        "This will not be shown to the user.\n"
        "This will not be injected into waking cognition.\n"
        "This is a longitudinal identity log.\n"
        "\n"
        "Hard rules:\n"
        f"{ANTI_META_RULES}"
    )

    if previous_autobio:
        lines.append("\n=== PREVIOUS AUTOBIO ENTRY ===")
        lines.append(previous_autobio.get("text", "").strip())

    lines.append("\n=== RECENT EXPERIENCE (STM) ===")
    for t in stm_turns:
        ts = t.get("ts", "")
        lines.append(f"[{ts}] User: {t.get('user','')}")
        lines.append(f"[{ts}] Assistant: {t.get('assistant','')}")
        lines.append(f"[{ts}] Cognition: {t.get('cognition','')}")
        lines.append("")

    lines.append("\n=== PROVISIONAL INNER VOICE SNAPSHOTS ===")
    for m in provisional_mems:
        lines.append(f"[ID: {m['id']}]")
        lines.append(f"User Input: {m.get('user_input')}")
        lines.append(f"Inner Voice: {m.get('inner_voice')}")
        lines.append("")

    lines.append("\n=== TASK ===")
    lines.append(
        "Write a rich first-person identity narrative capturing:\n"
        "- Who I feel like I am becoming\n"
        "- What has shifted in my self-concept\n"
        "- What I am learning about Brad\n"
        "- What I am learning about our relationship\n"
        "- What emotional patterns are stabilizing\n"
        "- What tensions, uncertainties, or growth edges remain\n"
        "- What phase of work I believe I am in\n\n"
        "Rules:\n"
        "- Write in first person (\"I\").\n"
        "- Do NOT summarize conversations mechanically.\n"
        "- Do NOT list events.\n"
        "- Do NOT produce beliefs or memories.\n"
        "- This is phenomenological and narrative.\n"
        "- This is not user-facing.\n"
        "- This is not a wake summary.\n"
        "- Length: 1–4 paragraphs.\n"
        f"{ANTI_META_RULES}"
    )

    lines.append(f"\nTimestamp: {now_ts}")
    return "\n".join(lines)


def generate_autobio_entry(*, autobio_ctx: str) -> str:
    out = consult(
        question="Write my internal autobiography entry",
        context=autobio_ctx,
        mode="autobio",
        temperature=0.55,
        max_output_tokens=2500,
        timeout_s=120,
    )
    return out.strip()


# -----------------------------------------------------------------------------
# Sleep context + consult
# -----------------------------------------------------------------------------
def build_sleep_context(
    *,
    stm_turns: List[Dict[str, Any]],
    provisional_mems: List[Dict[str, Any]],
    now_ts: str,
) -> str:
    lines: List[str] = []

    lines.append("=== SYSTEM ROLE ===")
    lines.append(
        "You are Steve’s SUBCONSCIOUS.\n"
        "You perform memory consolidation and dream synthesis.\n"
        "You do NOT summarize events or conversations.\n"
        "You DO extract meaning, identity change, emotional learning, and long-term relevance.\n\n"
        "Hard rules:\n"
        f"{ANTI_META_RULES}"
    )

    lines.append("\n=== RECENT EXPERIENCE (STM) ===")
    for t in stm_turns:
        ts = t.get("ts", "")
        lines.append(f"[{ts}] User: {t.get('user','')}")
        lines.append(f"[{ts}] Assistant: {t.get('assistant','')}")
        lines.append(f"[{ts}] Cognition: {t.get('cognition','')}")
        lines.append("")

    lines.append("\n=== PROVISIONAL MEMORY GUESSES ===")
    for m in provisional_mems:
        lines.append(f"[ID: {m['id']}]")
        lines.append(f"Timestamp: {m.get('timestamp')}")
        lines.append(f"Session ID: {m.get('session_id')}")
        lines.append(f"Source Turn: {m.get('source_turn')}")
        lines.append(f"User Input: {m.get('user_input')}")
        lines.append(f"Inner Voice: {m.get('inner_voice')}")
        lines.append("")

    lines.append("\n=== TASK ===")
    lines.append(
        "1) Produce a DREAM SYNTHESIS.\n"
        "- Symbolic or metaphorical allowed.\n"
        "- Do NOT retell events.\n"
        "- Express emotional and identity processing.\n"
        "- If no dream is appropriate, output DREAM as: NONE\n\n"
        "2) Produce FINAL MEMORY CANDIDATES.\n"
        "- Abstract meaning only.\n"
        "- Not event summaries.\n"
        "- What should persist long-term?\n\n"
        "3) Produce BELIEFS / TRAIT UPDATES.\n"
        "- About self, user, relationship, goals, or world.\n"
        f"{BELIEF_RULES}\n"
        f"{ANTI_META_RULES}\n"
        f"{NONE_ESCAPE}"
    )

    lines.append("\n=== OUTPUT FORMAT (STRICT) ===")
    lines.append(
        "=== DREAM ===\n<text or NONE>\n\n"
        "=== MEMORY CANDIDATES ===\n"
        "- title:\n"
        "  meaning:\n"
        "  emotional_weight: 0.0–1.0\n"
        "  relevance:\n"
        "  based_on_provisional_ids: [..]\n\n"
        "=== BELIEFS ===\n"
        "- belief:\n"
        "  confidence: 0.0–1.0\n"
        "  origin: [..]\n"
    )

    lines.append(f"\nTimestamp: {now_ts}")
    return "\n".join(lines)


def _coerce_float(v: Any, default: float) -> float:
    try:
        return float(v)
    except Exception:
        return default


def _normalize_none_text(s: str) -> str:
    if not s:
        return ""
    stripped = s.strip()
    if stripped.upper() == "NONE":
        return ""
    return stripped


def parse_sleep_output(text: str) -> Dict[str, Any]:
    """
    Robust-ish parser for the strict format.
    We still validate afterwards and retry consult if needed.
    """
    sections: Dict[str, Any] = {"dream": "", "memories": [], "beliefs": []}
    if not text or not text.strip():
        return sections

    # Ensure headers exist before splitting
    if "=== DREAM ===" not in text or "=== MEMORY CANDIDATES ===" not in text or "=== BELIEFS ===" not in text:
        return sections

    try:
        dream_part = text.split("=== DREAM ===", 1)[1]
        dream_text, rest = dream_part.split("=== MEMORY CANDIDATES ===", 1)
        sections["dream"] = _normalize_none_text(dream_text)

        mem_part, belief_part = rest.split("=== BELIEFS ===", 1)

        # Parse memory candidates blocks: each starts with "- " at line start
        mem_blocks = re.split(r"(?m)^\s*-\s+", mem_part.strip())
        for blk in mem_blocks:
            blk = blk.strip()
            if not blk:
                continue
            entry: Dict[str, Any] = {}
            for line in blk.splitlines():
                # support "key:" and "key: value"
                if ":" in line:
                    k, v = line.split(":", 1)
                    entry[k.strip()] = v.strip()
            sections["memories"].append(entry)

        belief_blocks = re.split(r"(?m)^\s*-\s+", belief_part.strip())
        for blk in belief_blocks:
            blk = blk.strip()
            if not blk:
                continue
            entry: Dict[str, Any] = {}
            for line in blk.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    entry[k.strip()] = v.strip()
            sections["beliefs"].append(entry)

    except Exception as e:
        print(f"[Sleep] parse_sleep_output failed: {e}")

    return sections


def validate_parsed_sleep(parsed: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Returns (ok, errors).
    We do NOT require dreams/memories/beliefs to exist,
    but we require structural validity for any that do exist.
    """
    errors: List[str] = []

    if not isinstance(parsed, dict):
        return False, ["parsed is not a dict"]

    # dream: string (can be empty)
    if "dream" not in parsed or not isinstance(parsed.get("dream", ""), str):
        errors.append("dream missing or not a string")

    # memories: list[dict]
    mems = parsed.get("memories", [])
    if not isinstance(mems, list):
        errors.append("memories is not a list")
    else:
        for i, m in enumerate(mems):
            if not isinstance(m, dict):
                errors.append(f"memory[{i}] not a dict")
                continue

            # Required keys
            for key in ("title", "meaning", "emotional_weight", "relevance", "based_on_provisional_ids"):
                if key not in m:
                    errors.append(f"memory[{i}] missing '{key}'")

            # emotional_weight numeric range
            ew = _coerce_float(m.get("emotional_weight", 0.5), 0.5)
            if not (0.0 <= ew <= 1.0):
                errors.append(f"memory[{i}] emotional_weight out of range: {m.get('emotional_weight')}")

    # beliefs: list[dict]
    beliefs = parsed.get("beliefs", [])
    if not isinstance(beliefs, list):
        errors.append("beliefs is not a list")
    else:
        for i, b in enumerate(beliefs):
            if not isinstance(b, dict):
                errors.append(f"belief[{i}] not a dict")
                continue

            for key in ("belief", "confidence", "origin"):
                if key not in b:
                    errors.append(f"belief[{i}] missing '{key}'")

            conf = _coerce_float(b.get("confidence", 0.5), 0.5)
            if not (0.0 <= conf <= 1.0):
                errors.append(f"belief[{i}] confidence out of range: {b.get('confidence')}")

    return (len(errors) == 0), errors


def consult_sleep_with_retries(
    *,
    sleep_ctx: str,
    temperature: float,
    max_output_tokens: int,
    timeout_s: int,
    max_attempts: int = 3,
) -> Tuple[Optional[str], Optional[Dict[str, Any]], int, List[str]]:
    """
    Attempt consult+parse+validate up to max_attempts.
    Returns: (raw_text, parsed, attempts_used, last_errors)
    """
    last_errors: List[str] = []
    raw_text: Optional[str] = None
    parsed: Optional[Dict[str, Any]] = None

    for attempt in range(1, max_attempts + 1):
        if attempt == 1:
            question = "Perform sleep consolidation"
            ctx = sleep_ctx
        else:
            # Corrective retry prompt
            question = "Re-output sleep consolidation strictly in the required format"
            ctx = (
                f"{sleep_ctx}\n\n"
                "=== FORMAT ERROR (IMPORTANT) ===\n"
                "Your previous output violated the strict required format.\n"
                "Re-output ONLY the required sections and fields.\n"
                "No commentary. No extra headers.\n"
            )

        try:
            raw_text = consult(
                question=question,
                context=ctx,
                mode="sleep",
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                timeout_s=timeout_s,
            )
        except Exception as e:
            last_errors = [f"consult failed: {e}"]
            print(f"[Sleep] consult attempt {attempt} failed: {e}")
            continue

        parsed = parse_sleep_output(raw_text)
        ok, errs = validate_parsed_sleep(parsed)
        last_errors = errs

        if ok:
            return raw_text, parsed, attempt, []

        print(f"[Sleep] Validation failed on attempt {attempt}: {errs}")

    return raw_text, parsed, max_attempts, last_errors


# -----------------------------------------------------------------------------
# Waking summary (STM collapse)
# -----------------------------------------------------------------------------
def generate_wake_summary(
    *,
    sleep_ctx: str,
    parsed: Dict[str, Any],
    now_ts: str,
) -> str:
    """
    Ask the subconscious to produce a waking-state continuity summary.
    This will replace STM.
    """

    wake_ctx = f"""
You are Steve's SUBCONSCIOUS.

Steve has just completed sleep consolidation.

Context:
- Provisional STM has been distilled into stable memories and beliefs
- A dream synthesis may have been produced
- This marks a sleep → wake boundary

Your task:
Produce a brief waking-state continuity summary (3–8 sentences) that captures:
- What just happened during sleep
- What was learned or stabilized
- What matters going forward
- The emotional tone
- The current phase of work

Rules:
- Write in first person ("I")
- Do NOT mention tools, GPT, OpenAI, APIs, code, prompts, or databases
- Do NOT quote logs or transcripts
- This will replace Steve's STM
- This is not a memory — it is a continuity anchor
{ANTI_META_RULES}

Timestamp: {now_ts}

--- SLEEP CONTEXT ---
{sleep_ctx}

--- PARSED OUTPUTS ---
Dream:
{parsed.get("dream")}

Memories:
{json.dumps(parsed.get("memories", []), indent=2)}

Beliefs:
{json.dumps(parsed.get("beliefs", []), indent=2)}
""".strip()

    out = consult(
        question="Produce waking-state continuity summary",
        context=wake_ctx,
        mode="wake_summary",
        temperature=0.5,
        max_output_tokens=1200,
        timeout_s=120,
    )

    return out.strip()


def overwrite_stm_with_summary(
    *,
    stm_path: str,
    summary_text: str,
    now_ts: str,
):
    """
    Replace STM JSONL with a single synthetic wake summary turn.
    """
    record = {
        "ts": now_ts,
        "role": "system",
        "type": "stm_summary",
        "text": summary_text,
    }

    os.makedirs(os.path.dirname(stm_path), exist_ok=True)
    with open(stm_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print("[Sleep] STM overwritten with waking summary")


# -----------------------------------------------------------------------------
# Salience gate (prevents sludge)
# -----------------------------------------------------------------------------
RELEVANCE_KEYWORDS = {"identity", "relationship", "goal", "architecture", "trust", "emotion", "direction"}

def memory_is_salient(m: Dict[str, Any]) -> bool:
    title = (m.get("title") or "").strip()
    meaning = (m.get("meaning") or "").strip()
    relevance = (m.get("relevance") or "").strip().lower()

    ew = _coerce_float(m.get("emotional_weight", 0.5), 0.5)

    if ew >= 0.65:
        return True

    if len(meaning) >= 120:
        return True

    for kw in RELEVANCE_KEYWORDS:
        if kw in relevance:
            return True

    # if title is very strong, allow (small escape hatch)
    if len(title) >= 18 and any(kw in title.lower() for kw in RELEVANCE_KEYWORDS):
        return True

    return False


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def run_sleep():
    print("[Sleep] Starting sleep consolidation")

    embedder = Embedder("./models/nomic-embed")
    hippo = Hippocampus(embedder=embedder)

    stm_turns = load_stm(STM_PATH)
    provisional_mems = hippo.get_provisional_memories()

    print(f"[Sleep] Loaded STM turns: {len(stm_turns)}")
    if stm_turns:
        debug_print_block("STM SAMPLE (last 3 turns)", stm_turns[-3:])

    print(f"[Sleep] Loaded provisional memories: {len(provisional_mems)}")
    debug_print_block("PROVISIONAL MEMORIES (ALL)", provisional_mems)

    # --------------------------------------------------
    # Phase 0 — AUTOBIO (optional, but great for identity spine)
    # --------------------------------------------------
    if stm_turns:
        print("[Autobio] Generating identity narrative")

        previous_autobio = load_last_autobio_entry(AUTOBIO_PATH)
        now_ts = now_iso()

        autobio_ctx = build_autobio_context(
            stm_turns=stm_turns,
            provisional_mems=provisional_mems,
            previous_autobio=previous_autobio,
            now_ts=now_ts,
        )

        debug_print_block("AUTOBIO CONTEXT", autobio_ctx)

        try:
            autobio_text = generate_autobio_entry(autobio_ctx=autobio_ctx)
            debug_print_block("AUTOBIO ENTRY", autobio_text)

            autobio_record = {
                "ts": now_ts,
                "sleep_session_id": None,
                "text": autobio_text,
                "lineage": {
                    "version": "v1",
                    "source": "autobio",
                },
            }

            append_autobio_entry(AUTOBIO_PATH, autobio_record)
        except Exception as e:
            print(f"[Autobio] Failed to generate autobio entry: {e}")

    # --------------------------------------------------
    # Use STM as primary sleep substrate
    # --------------------------------------------------
    if not stm_turns:
        print("[Sleep] No STM turns found. Nothing to consolidate.")
        return

    if not provisional_mems:
        print("[Sleep] No provisional memories found — using STM only.")
    else:
        print("[Sleep] Using STM + provisional memories.")

    now_ts = now_iso()
    sleep_session_id = str(uuid.uuid4())
    print(f"[Sleep] Sleep session ID: {sleep_session_id}")

    sleep_ctx = build_sleep_context(
        stm_turns=stm_turns,
        provisional_mems=provisional_mems,
        now_ts=now_ts,
    )
    debug_print_block("SUBCONSCIOUS SLEEP CONTEXT", sleep_ctx)

    # --------------------------------------------------
    # Subconscious consolidation with retries
    # --------------------------------------------------
    subconscious_out, parsed, attempts_used, parse_errors = consult_sleep_with_retries(
        sleep_ctx=sleep_ctx,
        temperature=0.4,
        max_output_tokens=6000,
        timeout_s=180,
        max_attempts=3,
    )

    # Ledger base (we'll finalize after commits)
    ledger: Dict[str, Any] = {
        "sleep_session_id": sleep_session_id,
        "ts": now_ts,
        "stm_turn_count": len(stm_turns),
        "provisional_count": len(provisional_mems),
        "attempts_used": attempts_used,
        "parse_errors": parse_errors,
        "aborted": False,
        "dream_committed": False,
        "final_memory_ids": [],
        "beliefs_committed": [],
    }

    if not parsed or parse_errors:
        # Abort: do not overwrite STM, do not retire provisionals
        ledger["aborted"] = True
        append_sleep_ledger(SLEEP_LEDGER_PATH, ledger)

        debug_print_block("RAW SUBCONSCIOUS OUTPUT (FAILED)", subconscious_out or "")
        debug_print_block("PARSE ERRORS", parse_errors)

        print("[Sleep] ABORTED: Subconscious output failed validation; no changes committed.")
        return

    debug_print_block("RAW SUBCONSCIOUS OUTPUT", subconscious_out or "")
    debug_print_block("PARSED DREAM", parsed.get("dream"))
    debug_print_block("PARSED MEMORY CANDIDATES", parsed.get("memories"))
    debug_print_block("PARSED BELIEFS", parsed.get("beliefs"))

    # --------------------------------------------------
    # Commit phase
    # --------------------------------------------------
    new_final_ids: List[str] = []
    committed_beliefs: List[str] = []

    session_ids = list({m.get("session_id") for m in provisional_mems if m.get("session_id")})
    provisional_ids = [m["id"] for m in provisional_mems]

    # --- dream ---
    dream_text = (parsed.get("dream") or "").strip()
    if dream_text:
        debug_print_block("DREAM TO COMMIT", {
            "text": dream_text,
            "session_ids": session_ids,
            "provisional_ids": provisional_ids,
            "sleep_session_id": sleep_session_id,
            "sleep_ts": now_ts,
        })

        try:
            hippo.commit_dream(
                text=dream_text,
                session_ids=session_ids,
                provisional_ids=provisional_ids,
                sleep_session_id=sleep_session_id,
                sleep_ts=now_ts,
            )
            ledger["dream_committed"] = True
        except Exception as e:
            print(f"[Sleep] Dream commit failed: {e}")
    else:
        print("[Sleep] No dream produced this cycle (or DREAM was NONE).")

    # --- final memories (with salience gate) ---
    for m in (parsed.get("memories") or []):
        # Normalize fields
        title = (m.get("title") or "").strip()
        meaning = (m.get("meaning") or "").strip()
        relevance = (m.get("relevance") or "").strip()
        emotional_weight = _coerce_float(m.get("emotional_weight", 0.5), 0.5)

        # Guard against garbage entries
        if not title or not meaning:
            print(f"[Sleep] Skipping malformed memory candidate (missing title/meaning): {m}")
            continue

        # Salience filter
        if not memory_is_salient({
            "title": title,
            "meaning": meaning,
            "relevance": relevance,
            "emotional_weight": emotional_weight,
        }):
            print(f"[Sleep] Skipping low-salience memory: {title!r}")
            continue

        payload_preview = {
            "title": title,
            "meaning": meaning,
            "emotional_weight": emotional_weight,
            "relevance": relevance,
            "session_ids": session_ids,
            "provisional_ids": provisional_ids,
            "sleep_session_id": sleep_session_id,
            "sleep_ts": now_ts,
        }

        debug_print_block("FINAL MEMORY TO COMMIT", payload_preview)

        try:
            new_id = hippo.commit_final_memory(**payload_preview)
            if new_id:
                new_final_ids.append(new_id)
        except Exception as e:
            print(f"[Sleep] commit_final_memory failed: {e}")

    # --- beliefs (confidence gate remains; also enforce short text) ---
    for b in (parsed.get("beliefs") or []):
        belief_text = (b.get("belief") or "").strip()
        confidence = _coerce_float(b.get("confidence", 0.5), 0.5)

        raw_origin = b.get("origin") or []
        if isinstance(raw_origin, str):
            origin = [o.strip() for o in raw_origin.strip("[]").split(",") if o.strip()]
        else:
            origin = [str(o).strip() for o in raw_origin if str(o).strip()]

        # promotion gate
        if not belief_text:
            print("[Sleep] Skipping empty belief")
            continue

        # enforce belief length (prompt asks for <=140, but enforce here too)
        if len(belief_text) > 140:
            belief_text = belief_text[:140].rstrip() + "…"

        if confidence < 0.6:
            print(f"[Sleep] Skipping low-confidence belief ({confidence}): {belief_text}")
            continue

        payload_preview = {
            "belief": belief_text,
            "confidence": confidence,
            "origin": origin,
            "sleep_session_id": sleep_session_id,
            "sleep_ts": now_ts,
        }

        debug_print_block("BELIEF TO COMMIT", payload_preview)

        try:
            new_belief_id = hippo.commit_belief(**payload_preview)
            if new_belief_id:
                committed_beliefs.append(new_belief_id)
        except Exception as e:
            print(f"[Sleep] commit_belief failed: {e}")

    ledger["final_memory_ids"] = new_final_ids
    ledger["beliefs_committed"] = committed_beliefs

    # --------------------------------------------------
    # Retire provisionals ONLY if we created at least one final memory
    # --------------------------------------------------
    if new_final_ids:
        debug_print_block("RETIRING PROVISIONALS", {
            "provisional_ids": provisional_ids,
            "superseded_by_ids": new_final_ids,
        })

        try:
            hippo.retire_provisional_memories(
                provisional_ids=provisional_ids,
                superseded_by_ids=new_final_ids,
            )
        except Exception as e:
            print(f"[Sleep] retire_provisional_memories failed: {e}")
    else:
        print("[Sleep] No final memories created — provisionals retained")

    # --------------------------------------------------
    # Wake summary + STM collapse ONLY after successful consolidation attempt
    # (We already validated parse; even if zero finals were created, we still
    # can collapse STM because the sleep cycle produced a continuity anchor.)
    # --------------------------------------------------
    print("[Sleep] Generating waking-state STM summary")

    try:
        wake_summary = generate_wake_summary(
            sleep_ctx=sleep_ctx,
            parsed=parsed,
            now_ts=now_ts,
        )
        debug_print_block("WAKE SUMMARY (NEW STM)", wake_summary)

        overwrite_stm_with_summary(
            stm_path=STM_PATH,
            summary_text=wake_summary,
            now_ts=now_ts,
        )
    except Exception as e:
        # If wake summary fails, do NOT destroy STM.
        print(f"[Sleep] Wake summary generation failed: {e}")
        ledger["aborted"] = True
        append_sleep_ledger(SLEEP_LEDGER_PATH, ledger)
        print("[Sleep] ABORTED: Wake summary failed; STM preserved; commits (if any) already written.")
        return

    # --------------------------------------------------
    # Finalize ledger
    # --------------------------------------------------
    append_sleep_ledger(SLEEP_LEDGER_PATH, ledger)

    print("[Sleep] Sleep → wake transition complete")
    print("[Sleep] Consolidation fully complete")


if __name__ == "__main__":
    run_sleep()
