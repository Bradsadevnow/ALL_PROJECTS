# AI Projects

A collection of AI systems, research tooling, and game engines built around large language models. The work spans agentic runtimes with multi-tier memory systems, a deterministic MTG rules engine with schema-constrained AI, mechanistic interpretability research, and supporting theory.

The theoretical foundations are in [`mt/`](mt/) — the runtimes are implementations of those ideas.

---

## Agentic Runtimes

### [Bob](bob/)
AI opponent for Magic: The Gathering. Combines a deterministic rules engine with LLM decision-making — the AI selects from a schema of legal actions, making hallucinated illegal plays structurally impossible. Includes TURBOTIME (optional agentic tool-use layer), tiered memory with human-in-the-loop LTM approval, and append-only audit logs.

### [Steve / Bob 2](bob_2/)
Full-stack embodied AI companion. FastAPI backend + React frontend communicating via SSE. Gemini 2.0 Flash, ChromaDB long-term memory, SQLite STM, offline sleep cycle consolidation. Addresses "The Mirror Trap" via bounded epochs, drift mitigation, and runtime-owned state authority.

### [Iris](iris/)
Continuous agentic runtime with a 28-parameter emotive physics engine. Emotions shift via inertial clamping — creating moods, not instant jumps. Epoch lifecycle (Orientation → Planning → Synthesis), Mid-Term Memory with subconscious resonance retrieval, Firestore state, handoff seeds for zero-drift session continuity, and a glassmorphic React dashboard.

### [Iris 2.0](Iris_2.0/)
Evolution of Iris focused on the compression problem — how to distill a growing conversation history into dense, durable LTM. Adds a token-aware compression pipeline, server-side refinement pass, and append-only event ledger for deterministic replay.

### [Hal](hal-main/)
Research-grade agent exploring dual-perspective memory retrieval. Uses Qdrant's **named vectors** to store each memory with two embeddings — factual/semantic and emotional/tonal — enabling hybrid search across both axes simultaneously. OpenAI or OpenRouter backend, Tkinter desktop UI.

### [Android Chatbot](yet_another_unnamed_chatbot_but_this_time_its_on_android_baby/)
Mobile-first chatbot (Flet → Android APK) with the same cortex/thalamus/hippocampus architecture as the desktop runtimes. Gemini backend, Qdrant memory, offline sleep cycle consolidation.

---

## MTG Systems

### [MTG Core](mtg_core/)
Authoritative, deterministic Magic: The Gathering rules engine. ~4,400 lines of game logic: full priority system, stack resolution, combat, 45+ card effects, triggered/activated/continuous abilities, state-based actions. Generates player-scoped legal action schemas for AI, CLI, TUI, and GUI control surfaces. The engine layer shared by Bob and MTG Web.

### [RulesBot](rulesbot/)
MCP server exposing the MTG Comprehensive Rules as a queryable LLM tool. Parses the official PDF into a structured JSON tree; rule lookups use direct hierarchical search rather than vector retrieval — the right tool for a static, well-structured document.

### [MCP Project](MCP_PROJECT/)
MCP R&D and context-aware MTG deckbuilder. Explores the MCP protocol for domain-specific tool surfaces — Scryfall integration, EDHREC, local LLM support via LM Studio.

---

## Mechanistic Interpretability

### [T-Scan](t-scan/)
Research toolkit for probing LLM internals. Activation logging via forward hooks, windowed circuit discovery (Pearson/Cosine/Energy correlation trifecta), dimension perturbation UI (Gradio), and a Godot 4 3D viewer for per-token neuron/edge graphs. Built on Llama 3B.

### [T-Scan 2: T-Scan Harder](tscan_2_tscan_harder/)
T-Scan applied at scale — 88+ experimental runs across "Fletcher" persona vs. baseline helpful-assistant prompt groups, investigating whether stable universal activation patterns persist across diverse input contexts.

---

## Theory & Architecture Docs

### [mt/](mt/)
Design essays that preceded the implementations. Core documents: **The Mirror Trap** (context rot and cognitive capture), **Dreamstates** (offline memory consolidation theory), **Emergent Voice** (identity coherence via architecture). Read these to understand *why* the runtimes are built the way they are.

### [ai_system/](ai_system/)
Technical specification and architecture documentation for the Steve runtime. Includes `ARCHITECTURE.md`, `SPEC.v2.md`, and `project_scope.md` with formal safety invariants.

---

## Web & Portfolio

### [MTG Web](mtg_web/)
React/TypeScript web frontend for MTG Core.

### [Landing](landing/)
Portfolio site. React, TypeScript, Tailwind CSS, Framer Motion.

---

## Cross-Cutting Concepts

Most projects share a common set of architectural patterns developed across iterations:

**Memory architecture**: STM (SQLite, append-only, bounded TTL) → LTM (vector DB, written only by offline sleep cycle). The live conversational loop never writes LTM directly.

**Drift mitigation**: Early session anchors are preserved immutably. LTM consolidation happens offline via objective prompts, not through reinforcement of the live context.

**Runtime authority**: The model reasons; the runtime commits. State changes require engine validation — the LLM cannot hallucinate its way to a committed state.

**Audit trails**: Append-only ledgers (`turns.jsonl`, `ai_trace.jsonl`) make every session reproducible from logs.

**Schema-constrained decisions**: In game contexts, the LLM selects from a computed schema of legal actions. Illegal choices aren't rejected — they're never offered.
