# AI Project Technical Deep Dives

This document provides a low-level "detailed dig" into the architectural mechanics of your AI project suite.

---

## 🏗️ The Steve Architecture (ai_system/steve)
**Focus**: *State Authority & Continuity Stability*

*   **The Epoch Transaction**: Steve treats every interaction as a database-like transaction.
    *   **Workflow**: `IDLE` → `OPEN` → `EXECUTING` (Internal Voice) → `COMMITTED/ABORTED`.
    *   **Authoritative Runtime**: The LLM is stateless; the runtime injects conversation history (STM) and identity (LTM) into every prompt, ensuring the model cannot hallucinate its own identity or past actions.
*   **The Mirror Trap Mitigation**: 
    *   Enforces a hard **250k token STM boundary**.
    *   Uses an **offline Sleep Cycle** (`consolidate.py`) which is the *only* process allowed to mutate the Long-Term Memory (Identity MD, Facts DB, Dreams).
    *   This prevents the "echo chamber" effect common in long-context models.

## 🃏 The Bob Engine (bob/mtg_core)
**Focus**: *Deterministic Rule Enforcement & Visible State*

*   **Action Surfaces**: Unlike standard game AI that tries to "read" the rules, Bob's engine (`engine.py`) is the source of truth.
    *   **VisibleState Contract**: The engine builds a `VisibleState` specific to the AI's perspective (hidden info enforced).
    *   **Legal Action Schema**: `action_surface.py` enumerates every legal move based on the current context. The LLM simply picks from this valid list.
*   **Zero-Hallucination Invariant**: Because the LLM never touches the game state directly and can only select from a pre-validated schema, it is physically impossible for the AI to make an illegal play.

## 🧠 The Halcyon Brain (hal-main)
**Focus**: *Neuro-Inspired Emotional Retrieval*

*   **Named Vector Architecture**: Uses Qdrant's named vectors to create a multi-modal memory retrieval system.
    *   **`content` vector**: Standard semantic search.
    *   **`emotional` vector**: Encodes the *feeling* of a conversation.
*   **Hybrid Search**: `hippocampus.py` queries both vectors and merges results with a custom decay function, allowing the agent to "remember" not just what was said, but how it felt, enabling more empathic/reactive responses.

## 🔬 T-Scan Interpretability (t-scan)
**Focus**: *Mechanistic Circuit Discovery*

*   **Windowed Probes**: `monolith_circuits.py` uses a sliding window (default 25 tokens) to compute Pearson correlations between neuron activations.
*   **Circuit Extraction**: 
    *   Identifies "monoliths"—clusters of neurons that fire in stable, correlated patterns over a window. 
    *   Supports real-time perturbation ("Dim Poking") to see how suppressing a specific "hero dimension" affects the model's output distribution.
*   **3D Spatial Rendering**: Token-by-token circuits are exported to JSON and rendered in **Godot 4**, turning abstract high-dimensional data into a navigable 3D graph.

## ⚖️ MCP Personalization (MCP_PROJECT)
**Focus**: *Ethical Scoping & Signal Abstraction*

*   **Domain Isolation**: Personalization is strictly limited to four domains: Chat, Tools, Context, and Apple signals.
*   **Abstraction Layer**: Raw data (URLs, specific facts) is discarded. Only abstracted signals (e.g., "preference for brevity," "repetition tolerance") are used to shape the agent's behavior, ensuring user privacy and system explainability.
