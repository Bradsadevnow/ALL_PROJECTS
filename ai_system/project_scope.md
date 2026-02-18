# Project Scope — Epoch-Authoritative Counter-Example Chatbot

This document is the **contract** for what this repo is building.

## Core Thesis

Build a chatbot runtime where **authority lives in the runtime**, not in model output.

> This inversion of control is the primary mechanism for mitigating **Long-Horizon Conversational Drift** (see [ARCHITECTURE.md](./ARCHITECTURE.md)).

> Only **committed epochs** are real.

The UI is a *projection* of authoritative events and snapshots.

## Key Invariants (Non-Negotiable)

1. **Epoch authority**
   - Only `EPOCH_COMMITTED` mutates continuity / committed context.
2. **Crash-safe continuity**
   - Committed history is append-only and can rehydrate state on restart.
3. **Rollback correctness**
   - In-flight output must not become authoritative after crash/restart.
4. **UI is non-authoritative**
   - UI shows what the runtime says; it must not infer or invent state.
5. **Bounded Context Lifecycle**
   - Context accumulation must be capped and reset to prevent "Mirror Trap" drift.

## Current Implementation (v2)

The project is a faithful implementation of its core architectural goals, featuring a robust backend, a feature-rich client, and a unique, cyclical memory system.

### Backend (FastAPI, `server/runtime.py`)

The core of the system is the `Runtime` class, which manages the Epoch Lifecycle and orchestrates all tool use.

-   **API**: A comprehensive REST API provides endpoints for all major features, including memory access.
-   **Real-time Events**: A Server-Sent Events (SSE) stream (`/events`) broadcasts all runtime events, allowing the UI to be a live projection of the AI's state.
-   **Structured Intent**: The runtime uses Gemini's JSON mode to require the model to respond in a strict `SteveInternalVoice` schema, ensuring reliable tool use and state management.

### Persistence & Memory

The system features a complete, tiered memory architecture.

-   **Short-Term Memory**: The `continuity/steve_memory.jsonl` event ledger acts as the authoritative log of conversation history.
-   **Long-Term Memory**:
    -   **Knowledge**: A SQLite database (`continuity/knowledge.db`) stores durable facts.
    -   **Identity**: A markdown file (`runtime/identity_context.md`) defines the AI's personality.
    -   **Dreams**: Metaphorical summaries of conversations are stored in `runtime/dreams/`.
-   **Sleep Cycle**: The `doc_script/consolidate.py` script runs offline to read the STM logs and use an LLM to distill new information into the LTM stores, before resetting the STM.

### Implemented Tool Suite

The AI has access to a wide range of tools to interact with data and external services:
- **MTG:** `scryfall`
- **Information:** `internet` (search, fetch), `rss`
- **Entertainment:** `steam`
- **Metacognition:** `memory` (remember, search, forget facts)

### Client (React, "The Surface")

The frontend is a collaborative workspace, not just a chat window.

-   **The Cortex**: A panel for viewing the AI's LTM (Identity, Knowledge, and Dreams).
-   **Live State Sync**: The UI subscribes to the SSE stream and updates in real-time to reflect the AI's thoughts and actions.

## Intended Next Additions

With the core architecture in place, future work can focus on expanding the AI's capabilities and user experience.

-   **Game Engine Surface**: Render a visual representation of an MTG game state.
-   **Voice Mode**: Integrate WebRTC for real-time voice interaction.
-   **Advanced Tooling**: Explore autonomous tool loops with explicit policy/budget controls.
-   **Code Execution**: Grant the AI the ability to write and execute code in a sandboxed environment.

## Explicitly Out of Scope

-   Unbounded/unrestricted web browsing.
-   Personal data ingestion (PII) or identity inference outside of explicit, user-provided facts.
-   Social media integration or analysis.
-   **Infinite Context Retention**: The system explicitly rejects the goal of maintaining a single, unbroken conversational thread forever.
