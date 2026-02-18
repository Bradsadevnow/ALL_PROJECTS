# Steve AI Runtime

An embodied AI companion built on an event-driven, stateful architecture that enables long-term memory and complex tool use. Steve is a collaborator for creative and technical projects, focusing on Magic: The Gathering, music, and gaming.

For a deep dive into the engineering philosophy behind this system—specifically how it mitigates "The Mirror Trap"—please see [ARCHITECTURE.md](./ARCHITECTURE.md).

## Features

- **Advanced MTG Deck Builder**: A collaborative, context-aware deck construction surface with Scryfall and EDHREC integration. The AI can propose, justify, and execute changes to decks.
- **Tiered Memory System**: Combines perfect short-term recall with a long-term memory (LTM) for identity, facts, and abstract "dreams," enabling genuine learning and evolution.
- **Offline "Sleep Cycle"**: Periodically, an offline script processes conversation logs to distill new information into the LTM. This resets the short-term context to prevent **Long-Horizon Conversational Drift** ("The Mirror Trap").
- **Rich Tool Suite**:
    - **Internet**: Search Google and fetch content from whitelisted domains.
    - **RSS**: Manage and read from RSS feed subscriptions.
    - **Music**: Control a local music library, search for tracks, and acquire new music.
    - **Steam**: View your game library, including installed and recently played games.
- **Structured, Reliable AI**: Forces the language model to output structured JSON, ensuring reliable and predictable tool execution.

## Core Architecture

The Steve AI Runtime is not a standard chatbot. Its design is guided by a core principle: **the runtime is the authority, not the model.** (See [SPEC.v2.md](./SPEC.v2.md) for details).

- **Epoch-Based State Machine**: Every interaction is an "epoch" that is atomically committed to state. This ensures data integrity and allows for complex, multi-turn operations (like the AI using multiple tools in a row) to be safely executed.
- **Event-Driven**: The backend (Python, FastAPI) and frontend (React, Vite) communicate via a real-time stream of server-sent events (SSE), allowing the UI to be a live projection of the AI's internal state.

## Safety Guarantees

This system enforces specific engineering invariants to ensure stability and safety (see [project_scope.md](./project_scope.md)):

1.  **Bounded Context Lifecycle**: Context accumulation is capped and reset. Infinite context retention is explicitly rejected to prevent emotional drift.
2.  **Runtime Authority**: The model cannot hallucinate state changes. Only the runtime can commit an "Epoch" to history.
3.  **Drift Mitigation**: Long-term memory is updated only via an objective, offline distillation process, not by the live conversational loop.

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Create a `.env` file or export these variables:
   ```ini
   GOOGLE_API_KEY="your_gemini_key"
   STEAM_API_KEY="276E50......" # Optional
   STEAM_ID="your_64bit_steam_id" # Optional default
   ```

3. **Run the Application**
   Open two terminal windows:

   **Terminal 1 (Backend)**
   ```bash
   uvicorn server.main:app --reload
   ```

   **Terminal 2 (Frontend)**
   ```bash
   cd client
   npm run dev
   ```

   ## Screenshots

![Screenshot from 2026-02-12 09-16-26.png](readme_assets/Screenshot%20from%202026-02-12%2009-16-26.png)
_Screenshot showing the dream text. this is generated directly from the system/user interaction._

![Screenshot from 2026-02-12 09-16-50.png](readme_assets/Screenshot%20from%202026-02-12%2009-16-50.png)
_Screenshot showing some of the user-extracted data from the interaction._

![Screenshot from 2026-02-12 09-17-13.png](readme_assets/Screenshot%20from%202026-02-12%2009-17-13.png)
_Screenshot showing the integrated music library._

![Screenshot from 2026-02-12 13-17-23.png](readme_assets/Screenshot%20from%202026-02-12%2013-17-23.png)
_Screenshot showing emphasis on collaborative devopment._

![Screenshot from 2026-02-12 13-17-36.png](readme_assets/Screenshot%20from%202026-02-12%2013-17-36.png)
_Screenshot showing real-time synthesis of toolcall and conversation data, allowing for seamless collaboration._

![Screenshot from 2026-02-12 13-20-11.png](readme_assets/Screenshot%20from%202026-02-12%2013-20-11.png)
_Screenshot showing more toolcall/reasoning and response chaining._

![Screenshot from 2026-02-12 13-20-33.png](readme_assets/Screenshot%20from%202026-02-12%2013-20-33.png)
_Screenshot showing more real-time collaboration._

![Screenshot from 2026-02-12 15-55-38.png](readme_assets/Screenshot%20from%202026-02-12%2015-55-38.png)
_Screenshot showing the system captures not only suggestion, but reasoning traces from the model._

![Screenshot from 2026-02-12 16-09-07.png](readme_assets/Screenshot%20from%202026-02-12%2016-09-07.png)
_Screenshot showing correction and collaborative deck building._

![Screenshot from 2026-02-12 17-08-35.png](readme_assets/Screenshot%20from%202026-02-12%2017-08-35.png)
_Screenshot showing more real-time collaborative development._
