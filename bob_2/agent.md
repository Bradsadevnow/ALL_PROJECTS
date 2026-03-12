# Steve Agent Repository Notes

## Overview
This repository contains the source code for "Steve", an AI learning core. It is divided into a FastAPI backend, a React/Vite frontend, and a runtime environment for state and memory management.

## Tech Stack
- **Backend**: Python, FastAPI, Uvicorn (REST API and WebSockets expected)
- **Frontend**: React, Vite, CSS Modules
- **Memory**: SQLite (`stm.db` for short-term memory), ChromaDB (`chroma_db/` for long-term memory embeddings)
- **AI Core**: Gemini SDK (assumed based on notes, used for generation and embeddings)

## Directory Structure

### 1. `backend/`
Contains the core API and agent logic.
- `main.py`: Entry point for the FastAPI server.
- `agent/`: The cognitive architecture of Steve.
  - `thalamus.py`: The central orchestrator. It binds the Cortex and Hippocampus together, handles logging of turns, and orchestrates the think/reflect/respond loop.
  - `cortex.py`: Handles feelings, reflections, and response generation based on the state and user query.
  - `hippocampus.py`: Manages memory ingestion, short-term memory (STM), and recall queries against long-term memory.
  - `sleep_cycle.py`: An offline script that runs asynchronously to consolidate STM into long-term memory and update identity/dreams.
  - `prompts.py`: System prompts for the agent.
  - `embedding_service.py`: Text embedding logic.
- `api/`, `core/`, `db/`: API routes, configuration features, and database utilities.

### 2. `frontend/`
A modern React application built with Vite.
- `src/App.jsx`: Main application component.
- `src/components/`: Modular React components handling chat, agent status UI, etc.
- Communicates with the backend independently, displaying Steve's current state and handling user input.

### 3. `runtime/`
Stores all dynamic state for Steve.
- `identity_context.md`: The core 'persona' and self-awareness of Steve (currently describes him as a learning core tested by "Brad", experiencing curiosity and anxiety).
- `continuity_context.md`: A handoff file used to maintain state continuity across restarts or major events (like memory overhauls).
- `stm.db`: SQLite database for immediate short-term memory.
- `chroma_db/`: Vector database for long-term episodic/semantic memory.
- `dreams/`: Directory for processing or generating offline "dreams" during the sleep cycle.

## How to Run

**1. Start the Backend:**
```bash
source .venv/bin/activate
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

**2. Start the Frontend (in a separate terminal):**
```bash
cd frontend
npm run dev
```

**3. Run the Sleep Cycle (Consolidation):**
```bash
source .venv/bin/activate
python3 -m backend.agent.sleep_cycle
```
