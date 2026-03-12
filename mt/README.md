# mt — Theoretical Foundations

Design essays and architectural theory underlying the AI systems in this repo. These documents came first — the runtimes (Bob, Steve, Iris, Hal) are implementations of the ideas worked out here.

## Documents

| File | What it is |
|------|-----------|
| `mirror_trap.md` | The core problem: context rot and cognitive capture in long-horizon LLM conversations. Defines "The Mirror Trap" and the design principles for mitigating it. Required reading for understanding why the runtimes are built the way they are. |
| `dreamstates.md` | Theory of memory consolidation — why offline distillation ("sleep") produces more stable LTM than live-loop writes, and the concept of "abstract dreams" as compressed episodic memory. |
| `emergent_voice.md` | On identity coherence and emergent voice in persistent AI systems. How a consistent identity can emerge from architecture rather than prompt injection. |
| `recursive_state.md` | Recursive state management patterns for systems that reason about their own reasoning. |
| `RSS.md` | Information retrieval, feed integration, and how ambient external context can be incorporated without breaking memory boundaries. |
| `draft.md` | Extended draft — conversational AI design philosophy. |
| `ntdraft.md` | Normalization and thought document — earlier working notes. |
