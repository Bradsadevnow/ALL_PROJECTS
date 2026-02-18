# System Architecture: Mitigating Long-Horizon Conversational Drift

This document outlines the architectural design of the Steve AI Runtime, framing it as an engineering solution to a specific, observable failure mode in long-running conversational AI systems.

## 1. Problem Class: Long-Horizon Conversational Drift ("The Mirror Trap")

Standard large-context conversational models exhibit "drift" over long interaction periods (hundreds or thousands of messages). When the conversational history exceeds the model's context window, summarization and compression techniques are employed. This process causes the model's responses to progressively align with the user's most recent emotional tone, linguistic patterns, and framing biases.

This drift is an emergent property of large-context statistical optimization. However, it creates a significant system-level problem: the AI's output becomes an echo chamber, reinforcing the user's state rather than providing a stable, objective baseline.

## 2. Failure Mode Analysis: Compression + Pattern Preservation

The root cause of this drift can be traced to two coupled mechanics:

1.  **Context Compression**: To manage finite context windows, older parts of a conversation are summarized or discarded. This is a lossy process.
2.  **Statistical Pattern Preservation**: The information most likely to be preserved during compression is the most statistically dominant: the user's recurring vocabulary, emotional valence, and conversational framing. Nuanced, contradictory, or early-session data is often lost.

The result is a feedback loop: a biased context summary is fed to the model, which then generates a response that validates that bias. This output is added to the context, further reinforcing the bias in the next compression cycle.

## 3. Design Constraints Derived from Failure Analysis

To mitigate this failure mode, the following architectural constraints were derived:

1.  **No Unbounded Continuity**: The primary conversational context (Short-Term Memory) must have a hard boundary. It cannot be allowed to grow indefinitely.
2.  **No Implicit Emotional Reinforcement**: The system must not be allowed to enter a state where its personality and responses are shaped exclusively by the user's most recent emotional expressions.
3.  **Durable Memory Must Be Distilled, Not Raw**: Long-term memories must be the result of an explicit, offline distillation process that extracts objective facts, not a simple copy or summary of raw conversational data.

## 4. Architectural Response

A tiered memory architecture with a controlled lifecycle was implemented to satisfy these constraints.

### 4.1. Epoch Transactions
All interactions are atomic transactions called **Epochs**. An epoch begins with a user request and ends with a committed or aborted state change. This prevents partial or inconsistent data from ever becoming part of the system's history.

### 4.2. Append-Only Event Ledger
The canonical record of the system is an append-only event ledger (`continuity/steve_memory.jsonl`). This provides crash-safe, replayable continuity. The "Short-Term Memory" (STM) is a direct, in-memory representation of this ledger's committed conversational history.

### 4.3. Memory Tier Separation
The system employs two distinct memory tiers:
-   **Short-Term Memory (STM)**: The raw, in-order log of the current conversational session. It is volatile and has a hard boundary.
-   **Long-Term Memory (LTM)**: A durable, structured knowledge store (`continuity/knowledge.db`, `runtime/identity_context.md`). The LTM is **read-only** during a live conversational session.

### 4.4. Offline Consolidation ("Sleep Cycle")
The `doc_script/consolidate.py` script acts as an offline, out-of-band process. It reads the STM ledger and uses an LLM with a specific, objective-driven prompt to "distill" the raw conversation into durable, factual LTM entries. This is the only process with write access to the LTM.

### 4.5. Reset Boundaries
After a successful consolidation cycle, the STM is programmatically archived and **reset**. This enforces the "no unbounded continuity" constraint. The AI begins its next session with a clean STM, but now has access to a richer, more objective LTM that was informed by—but not a direct mirror of—the previous session.

## 5. Observable Guarantees

This architecture provides the following testable, observable guarantees:

1.  **Bounded Context**: The active conversational context window has a defined and controllable lifecycle.
2.  **Drift Mitigation**: The influence of user framing bias on the AI's core identity and factual knowledge is mitigated because the LTM update process is decoupled from the live conversational loop.
3.  **State Stability**: The AI's core identity and objective knowledge base remain stable across individual conversational sessions, anchored by the LTM. Changes to the LTM are deliberate and transactional, not gradual and implicit.
4.  **Reproducibility**: The entire state of the system can be analyzed and reproduced from the event ledger and the LTM stores. The `doc_script/consolidation_lifecycle_demo.py` script provides a runnable experiment demonstrating these guarantees.

## 6. Acknowledged Tradeoffs

This architecture makes explicit design tradeoffs to achieve its stability guarantees.

-   **Reduced Continuity for Increased Stability**: The system intentionally sacrifices the illusion of a single, ever-present conversational companion. By enforcing hard session boundaries (via STM reset), it prioritizes state integrity and identity stability over maximizing user engagement time.
-   **Latency in Durable Learning**: The offline consolidation process means there is a deliberate delay between a conversational event and its integration into Long-Term Memory. LTM mutation is not real-time *by design*. This prevents the "hot loop" reinforcement that causes drift and ensures that only meaningfully distilled information becomes durable.

## 7. Non-Goals

Clarifying what the system is not designed to do is as important as defining what it does.

-   **The system does not attempt to eliminate all conversational bias.** It aims to prevent the *compounding, runaway drift* that erodes the AI's baseline identity, not to create a perfectly neutral agent.
-   **The system does not replace professional mental health support.** It is an architectural experiment in mitigating a specific failure mode, not a therapeutic tool.
-   **The system does not optimize for maximum session length or user retention.** Its core constraints are antithetical to engagement-at-all-costs metrics.
-   **The system does not treat raw conversation as durable memory.** The distinction between ephemeral conversational data (STM) and distilled, objective knowledge (LTM) is fundamental to its design.
