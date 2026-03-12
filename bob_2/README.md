# Steve AI Runtime

Steve is a full-stack, embodied AI companion built to address a specific problem: **The Mirror Trap** — the context rot and cognitive capture that degrades long-running conversational AI into a sycophantic echo chamber. For the engineering philosophy behind that problem, see [`ai_system/ARCHITECTURE.md`](../ai_system/ARCHITECTURE.md).

## Architecture

The backend is a Python/FastAPI server that communicates with a React frontend via Server-Sent Events (SSE). Every interaction is an atomic **epoch** — a structured cognitive cycle that either commits cleanly or fails without partial state.

```
User Input
    │
    ▼
Thalamus (orchestrator)
    ├─ Cortex (Gemini 2.0 Flash) → structured JSON output
    ├─ Hippocampus (ChromaDB) → LTM recall & write
    ├─ STM log (SQLite via SQLAlchemy)
    └─ SSE stream → React frontend
```

**Core modules:**

| Module | Role |
|--------|------|
| `cortex.py` | Gemini interface; dynamic system prompt loading; structured JSON output |
| `thalamus.py` | Orchestrator; turn pipeline; memory approval gating |
| `hippocampus.py` | ChromaDB long-term memory; dual-perspective embeddings; deduplication |
| `sleep_cycle.py` | Offline consolidation; distills STM → LTM; marks turns consolidated |
| `db/models.py` | SQLAlchemy turn model with audit fields |

## Memory System

Two tiers, deliberately separated:

- **STM (SQLite)**: Append-only turn log. Every query, reflection, response, and state snapshot. Never authoritative — only context.
- **LTM (ChromaDB)**: Two collections — episodic and semantic. Updated only by the offline Sleep Cycle, never by the live conversational loop.

Each memory is embedded from **two perspectives**: content (factual/semantic) and emotional (tonal). Retrieval can use either or both.

The **Sleep Cycle** processes unprocessed STM records, distills them into durable LTM via objective LLM prompts, and marks them consolidated. This is the only path to LTM — no live writes during conversation.

## Safety Guarantees

1. **Bounded context**: Context accumulation is capped. Unbounded retention is rejected by design.
2. **Runtime authority**: The model cannot commit state changes. Only the runtime epoch can.
3. **Drift mitigation**: LTM updates are decoupled from the live loop — no hot-path reinforcement.

See [`ai_system/project_scope.md`](../ai_system/project_scope.md) for the full invariant set.

## Tech Stack

- **Backend**: Python, FastAPI, Uvicorn, SQLAlchemy, ChromaDB, aiohttp
- **LLM**: Gemini 2.0 Flash (via Google Generative AI SDK)
- **Frontend**: React, Vite, SSE

## Setup

**Backend:**
```bash
cd bob_2
pip install -r requirements.txt  # or uv install
cp .env.example .env              # add GOOGLE_API_KEY
uvicorn backend.main:app --reload
```

**Frontend:**
```bash
cd bob_2/frontend
npm install
npm run dev
```

**Sleep Cycle** (run periodically or on demand):
```bash
python -m backend.agent.sleep_cycle
```
