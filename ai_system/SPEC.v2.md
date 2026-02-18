# Steve AI Runtime: Technical Specification (v2)

This document provides a comprehensive overview of the Steve AI Runtime, detailing its architecture, data flow, and core components as they are currently implemented. It serves as the single source of truth for the project.

## 1. Core Architecture: Epoch-Authoritative State Machine

The system is a **Stateful Runtime** built around a **Stateless Language Model**. Its fundamental principle is that the runtime is the sole authority on the state of the AI. All interactions are processed within an atomic unit called an **Epoch**. State changes are only finalized when an epoch is successfully "committed."

- **Epoch**: A complete user interaction cycle, from user input to a final, committed AI response.
- **Turn**: A single step of model execution within an epoch. An epoch can have multiple turns to support tool chaining.
- **Event Ledger**: The append-only log file (`continuity/steve_memory.jsonl`) that serves as the single source of truth for all events. The system can be fully rehydrated from this ledger.

### 1.1. Structured Intent (`SteveInternalVoice`)

For reliability, the model is required to respond with a JSON object conforming to the `SteveInternalVoice` schema. This ensures predictable model output.

- `thought`: The model's internal monologue or reasoning (not shown to the user).
- `emotive_state`: A string representing the AI's current emotional disposition.
- `tool_calls`: A list of tools the model intends to execute, including their names and arguments.
- `final_response`: The message to be delivered to the user.

### 1.2. Epoch Lifecycle

The system enforces a strict lifecycle for each epoch, ensuring data integrity.

1.  `IDLE`: The system is waiting for user input.
2.  `OPEN`: A user has submitted input, and a new epoch has begun.
3.  `EXECUTING`: The model is thinking or executing tools. This phase can contain multiple turns.
4.  `COMMITTED`: The epoch has completed successfully. The user input and the final AI response are appended to the permanent conversation history.
5.  `ABORTED`: The epoch failed due to an error or cancellation. No changes are made to the conversation history.

### 1.3. Ethereal Data & Redaction

To prevent context window bloat, large data payloads from tool calls (e.g., `edhrec.get_recommendations`) are marked as "ethereal." The full data is available to the model during the active epoch, but it is replaced with a placeholder note in the permanent event log.

## 2. Tiered Memory System

The AI's memory is organized into a two-tiered system to enable both immediate conversational recall and long-term learning and identity.

### 2.1. Short-Term Memory (STM)

- **Source**: `continuity/steve_memory.jsonl`
- **Function**: The authoritative, chronological log of all committed conversations. The entire STM is injected into the model's context for every new epoch, providing perfect recall within a session.

### 2.2. Long-Term Memory (LTM)

The LTM is the distilled essence of past conversations, managed by an offline "sleep cycle" script (`doc_script/consolidate.py`).

-   **Identity (`runtime/identity_context.md`)**: A first-person narrative document that defines the AI's personality, self-concept, and core directives. The consolidation script uses an LLM to update this file by integrating the "implications" of recent conversations.
-   **Knowledge (`continuity/knowledge.db`)**: An SQLite database containing durable, factual information about the user, projects, and the world. The consolidation script uses an LLM to extract these facts from conversations and save them to the database.
-   **Dreams (`runtime/dreams/`)**: Abstract, metaphorical syntheses of conversational themes. The consolidation script uses an LLM to generate these and saves them as individual markdown files.

### 2.3. The Sleep Cycle (`consolidate.py`)

This offline process runs on the event logs to distill STM into LTM.

1.  **Aggregate**: It gathers all conversation events from logs that have not yet been processed.
2.  **Process**: It uses an LLM to perform three actions on the new text: update identity, extract facts, and generate a dream.
3.  **Reset**: It calls the server's `/management/reset` endpoint, which archives the processed event logs and clears the in-memory STM. This prevents the context window from growing indefinitely while ensuring knowledge is retained in the LTM.

## 3. Tool Suite

The runtime provides the model with a rich set of tools to interact with data and external systems.

| Tool Namespace    | Implemented Functions                                                                                                     |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `scryfall`        | `get_card_details`, `search`                                                                                              |
| `edhrec`          | `get_recommendations`                                                                                                     |
| `rss`             | `subscribe`, `unsubscribe`, `list`, `fetch`, `check`                                                                      |
| `internet`        | `search`, `fetch` (for whitelisted domains), `list_allowed`                                                               |

| `steam`           | `get_library`, `get_recent_games`, `get_installed`, `resolve_id`                                                          |
| `memory`          | `remember_fact`, `search_facts`, `forget_fact`                                                                            |

## 4. API Endpoints (`server/main.py`)

Communication between the frontend and the backend is handled via a REST API and a Server-Sent Events (SSE) stream.

### Core & Events
- `GET /`: System status.
- `POST /start-epoch`: Submit user input.
- `GET /events`: SSE stream for all real-time system events.
- `GET /snapshot`: JSON dump of the agent's live runtime state.
- `POST /management/reset`: Triggers the memory archive and reset process.

### Long-Term Memory
- `GET /identity`: Read the identity context.
- `POST /identity`: Update the identity context.
- `GET /knowledge`: List facts from the knowledge database.
- `DELETE /knowledge/{fact_id}`: Delete a fact.
- `GET /dreams`: List dream files.
- `GET /dreams/{filename}`: Read a dream file.
- `DELETE /dreams/{filename}`: Delete a dream file.

### Tools & Services
- `GET /media-status`, `POST /control-media`, `GET /music/library`: Endpoints for the music system.
- `GET /deck/list`, `POST /deck/create`, `POST /deck/load`, `GET /deck/state`, `POST /deck/approve`, `POST /deck/reject`: Endpoints for the Deck Forge.

## 5. Client ("The Surface")

The frontend is a React-based Single-Page Application (SPA) designed as a "Collaborative Workspace."

-   **Architecture**: Built with Vite, React, and TailwindCSS.
-   **Communication**: Uses `fetch` for REST calls and the `EventSource` API for the SSE stream.
-   **Core Modules**:
    -   **Neural Link**: The main chat interface.
    -   **Deck Forge**: A visual workspace for creating and managing MTG decks, including a review system for AI-proposed changes.
    -   **Media HUD**: UI for controlling the music player.
    -   **The Cortex**: A system monitor for viewing the AI's identity, knowledge, and dreams.
