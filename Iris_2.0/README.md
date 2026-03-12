# Iris 2.0

An evolution of the [Iris](../iris) runtime with a refined epoch lifecycle and an explicit **compression pipeline** for memory consolidation.

The core concepts — emotive physics, epoch-based state machine, MTM/LTM memory hierarchy, identity anchors — are inherited from Iris v1. This version focuses on the compression problem: how to distill a growing conversation history into durable, semantically dense long-term memory without losing continuity.

## What's Different

- **Compression Pipeline** (`compression_pipeline.py`): Token-aware distillation from MTM into LTM. Designed to run at epoch boundaries or on sleep trigger.
- **Refiner** (`server/refiner.py`): Server-side refinement pass before response synthesis.
- **Ledger** (`core/ledger.py`): Append-only event ledger enabling deterministic replay of any session.
- **Lifecycle** (`core/lifecycle.py`): Cleaner epoch state machine with explicit phase transitions.

## Architecture

```
Epoch trigger
    │
    ▼
core/lifecycle.py  ─→  LLM (Gemini)
    │
    ├─ memory/mtm.py     (Mid-Term Memory traces)
    ├─ core/ledger.py    (append-only event log)
    └─ compression_pipeline.py  ─→  LTM
```

**Memory tiers:**
- **MTM** (`memory/`): Ghosted traces from recent epochs, retrieved by subconscious resonance
- **LTM** (`persistence/`): Durable, distilled facts written only by compression pipeline
- **Ledger** (`core/ledger.py`): Source of truth for all state transitions; enables replay

## Tech Stack

- **Backend**: Python async, aiohttp
- **LLM**: Gemini
- **Frontend**: React / TypeScript / Tailwind CSS / Vite
- **Deployment**: Docker + nginx

## Setup

**Backend:**
```bash
cd Iris_2.0
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add GOOGLE_API_KEY + Firestore credentials
python run.py
```

**Frontend:**
```bash
cd Iris_2.0/frontend
npm install
npm run dev
```

**Docker:**
```bash
docker build -t iris2 .
docker run -p 80:80 iris2
```
