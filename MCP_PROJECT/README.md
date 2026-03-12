# MCP Project — Model Context Protocol R&D

Research and tooling for MCP (Model Context Protocol) integrations. The primary artifact is a context-aware MTG deckbuilder that connects an LLM to Scryfall and EDHREC via MCP tool calls.

## What's Here

### `R_D/` — Runtime and Tooling

An earlier-generation AI runtime with MCP-oriented tool definitions. Shares architectural patterns with the Bob/Steve systems (orchestrator, sleep cycle, STM store) but focuses on surfacing tools to an LLM via the MCP protocol.

Key files:
- `tools.py` — MCP tool definitions
- `schema.py` — Data schema
- `store.py` — Persistent storage
- `orchestrator.py` — Turn orchestration
- `sleep.py` / `stm_store.py` — Memory consolidation
- `scryfall.py` — Scryfall API client
- `steam.py` — Steam library integration

### `R_D/deckbuilder/` — MTG Deckbuilder App

A collaborative, context-aware deck construction surface:
- **Scryfall integration** (`scryfall_client.py`): Card search, oracle text, pricing
- **Context management** (`context_manager.py`, `deckbuilder_context.py`): Maintains deck state across turns
- **Local LLM support** (`lm_studio_client.py`): Connects to LM Studio for local inference

See [`R_D/deckbuilder/README.md`](R_D/deckbuilder/README.md) for setup details.

## MCP Pattern

The MCP protocol lets an LLM call structured tools during reasoning — the server exposes a tool schema, the LLM decides when to call them, and results are injected back into context. This project explores that pattern for domain-specific applications (MTG) where the tool surface needs to be rich and the context management non-trivial.
