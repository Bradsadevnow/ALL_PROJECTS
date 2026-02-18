# AI Project Portfolio Summary

This repository contains a sophisticated ecosystem of AI-related projects, ranging from embodied conversational agents and deterministic game solvers to neuro-inspired memory systems and mechanistic interpretability tools.

---TRIGGER

## 🤖 Conversational & Embodied Agents

### **Steve AI (ai_system & steve)**
Steve is a stateful, continuity-focused AI companion designed to persist identity and memory across long-term interactions. It is a "collaborator" rather than a simple chatbot.

*   **Core Philosophy**: Mitigates "The Mirror Trap" (Long-Horizon Conversational Drift) through periodic "Sleep Cycles" that distill context into long-term memory.
*   **Architecture**:
    *   **Epoch-Based State Machine**: Interactions are atomic "Epoch" transactions (Commit/Abort).
    *   **Tiered Memory**: Short-Term Memory (STM - 250k token cap), Medium-Term Memory (MTM - decaying "Subconscious" reasoning traces), and Long-Term Memory (LTM - fact storage).
    *   **Event-Driven**: Uses Server-Sent Events (SSE) for a real-time React UI.
*   **Capabilities**: Advanced MTG deck building, music library management, RSS feed reading, and Steam integration.
*   **Tech Stack**: Python (FastAPI), React (Vite), ChromaDB, SQLite, Scryfall/EDHREC APIs.

### **Halcyon (hal-main)**
A neuro-inspired agent focusing on "Emotional Memory" and reflection.

*   **Unique Feature**: Uses Qdrant's **named vectors** for dual-perspective memory search:
    *   **Content Vector**: Factual/semantic similarity.
    *   **Emotional Vector**: Tonal/feeling similarity.
*   **Architecture**: Modeled after brain structures (`thalamus.py`, `cortex.py`, `hippocampus.py`).
*   **Tech Stack**: Python, Qdrant (Vector DB), Tkinter (Desktop UI).

---

## 🃏 Game-Specific AI (Magic: The Gathering)

### **Bob (bob)**
A deterministic MTG player/tutor that combines a hardcoded rules engine with LLM decision-making.

*   **Engineering Invariant**: **No Hallucinations**. The AI cannot make illegal plays because the `mtg_core` engine generates a schema of only legal actions for the AI to choose from.
*   **Key Components**:
    *   **`mtg_core`**: Enforces Phase-1 MTG rules (combat, keywords, triggers).
    *   **Human-in-the-Loop**: Long-term memory writes require explicit human approval via an audit ledger.

---

## 🔬 AI Research & Theory

### **T-Scan (t-scan)**
A research artifact for **Mechanistic Interpretability**, probing the internal hidden states of LLMs.

*   **Functionality**: Probes Llama 3B/3.2 activations and identifies correlated dimensions ("circuits").
*   **Visualization**: Renders per-token neuron/edge graphs as navigable 3D structures in the **Godot Engine**.
*   **Components**: Activations hooks, pearson/cosine correlation scans, and a "Dim Poke" UI for perturbing specific dimensions.

### **MT Research Notes (mt)**
A collection of theoretical design documents and design patterns for advanced AI systems.

*   **Key Concepts**:
    *   **The Mirror Trap**: Research on preventing AI from becoming a "mirror" of the user's latest context.
    *   **Recursive State**: Theoretical frameworks for state management in high-agency agents.
    *   **Dreamstates**: Concepts for offline distillation and memory consolidation.

---

## 🛠️ Infrastructure & R&D

### **MCP_PROJECT (R_D)**
Focused on the development of personalized AI services within strict privacy and scope boundaries.

*   **Personalization Domains**: Constraints AI learning to four specific domains (Conversation, Tools, Context, Apple signals) to ensure ethical defensibility and explainability.
*   **Domain Integrity**: Hard rules preventing direct writes to LTM and requiring abstracted signals only.
