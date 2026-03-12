# Android AI Chatbot

A mobile-first AI chatbot with the same multi-tier memory architecture as the desktop runtimes — Gemini backend, Qdrant long-term memory, offline sleep cycle consolidation — but deployed to Android via [Flet](https://flet.dev/).

## Architecture

The backend is a Python async server (aiohttp) that mirrors the cortex/thalamus/hippocampus pattern from the other runtimes. The Android frontend connects to it over HTTP, rendering a native-feeling mobile UI via Flet.

```
Android UI (Flet)
    │
    ▼
thalamus.py (orchestrator)
    ├─ cortex.py         → Gemini API
    ├─ hippocampus.py    → Qdrant (LTM, named vectors)
    ├─ embedding_service.py
    └─ sleep_cycle.py    → offline consolidation
```

## Memory

- **Qdrant** with named vectors: content embedding + emotional embedding per memory
- **Sleep cycle**: offline distillation of conversation logs into LTM — same pattern as Bob/Steve/Iris
- Persistent across sessions

## Tech Stack

- **Backend**: Python, aiohttp, Gemini SDK, Qdrant client
- **Frontend**: Flet (Python-based cross-platform UI → Android APK)

## Setup

**Backend:**
```bash
cd yet_another_unnamed_chatbot_but_this_time_its_on_android_baby
pip install -r requirements.txt  # or check GEMINI.md for deps
cp .env.example .env              # add GOOGLE_API_KEY + QDRANT config

# Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Start backend
python app/main.py  # or equivalent entry point
```

**Android frontend:**
```bash
cd AndroidChatbot
pip install flet
flet run --android  # or flet build apk for APK
```

See `GEMINI.md` for Gemini-specific configuration notes.
