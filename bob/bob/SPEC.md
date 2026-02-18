# Bob Runtime — implementation-aligned spec (code is source of truth)

This document describes what the `bob/` runtime currently does.

## Identity and config
- Canonical system id: `bob`
- Display name default: `Bob`
- Config source: `bob/config.py` (`BobConfig`)

### Model endpoints
- Local chat model (default LM Studio style):
  - `BOB_LOCAL_BASE_URL` (default `http://localhost:1234/v1`)
  - `BOB_LOCAL_API_KEY` (default `lm-studio`)
  - `BOB_LOCAL_MODEL` (default `openai/gpt-oss-20b`)
- Remote chat model:
  - `BOB_CHAT_BASE_URL` (fallback `OPENAI_BASE_URL`)
  - `BOB_CHAT_API_KEY` (fallback `OPENAI_API_KEY`)
  - `BOB_CHAT_MODEL` (default `gpt-4o-mini`)
- Remote MTG model:
  - `BOB_MTG_BASE_URL` (fallback `OPENAI_BASE_URL`)
  - `BOB_MTG_API_KEY` (fallback `OPENAI_API_KEY`)
  - `BOB_MTG_MODEL` (default `BOB_CHAT_MODEL`, else `gpt-5`)
- Routing flag: `BOB_ROUTE_MTG_REMOTE`

### OpenAI-compatible client behavior
`bob/models/openai_client.py` uses `POST .../chat/completions` with:
- streaming and non-streaming paths
- token-parameter fallback (`max_completion_tokens` -> `max_tokens`) on 400/422 unknown-field style errors
- SSE `data:` parsing for stream responses

## Authoritative state and logs

### State file
`runtime/state.json` (via `StateStore`) includes more than just continuity bullets:
- `identity`
- `affect_state`
- `continuity`:
  - `active_context`
  - `open_threads`
  - `conversation_summary`
  - `live_chat`
  - `integrity`
- `meta`:
  - `last_updated_utc`
  - `turn_counter`
  - `context_metrics`
  - `last_context_rebuild`

### Turn log
`runtime/turns.jsonl` (append-only) stores `TurnRecord` fields:
- `ts_utc`, `session_id`, `turn_number`
- `user_input`, `final_output`
- `think` (empty for base orchestrator; populated in TURBOTIME)
- `tools`
- `memory_candidates`
- `state_before`, `state_after`

## Runtime modes

## 1) Base chat orchestrator (`bob/runtime/orchestrator.py`)
Current flow:
1. Load state snapshot.
2. Manage context budget (`ContextWindowManager`) and optionally rebuild summary.
3. Build chat-first prompt from summary + recent live chat + current user input.
4. Stream assistant response from selected model.
5. Update continuity (`active_context`, `open_threads`) via continuity prompt + JSON parser/fallback.
6. Commit state and append turn log.

Important: in this path, STM is instantiated but not used for recall/write, and memory candidates are currently empty.

## 2) TURBOTIME orchestrator (`bob/turbotime/orchestrator.py`)
Current flow:
1. Stage 1 orientation call.
2. Stage 2 planning call.
3. Parse tool requests from Stage 2 text.
4. Execute allowed tool(s).
5. Optional Stage 2 integration call with tool results.
6. Stage 3 streamed user-facing response.
7. Continuity update + state/log commit.

Notes:
- TURBOTIME writes `think` into the turn log (`STAGE1` + `STAGE2`).
- `memory_candidates` is currently set to `[]`.
- Tool execution can be enabled per selected public tool and is logged.

## Context window system
Implemented in `bob/runtime/context_window.py`:
- deterministic token counting via local tokenizer artifacts (`bob/model_tokenizer/tokenizer.json`)
- budget buckets: system, summary, live chat, tool injections, current user input, reserve
- pressure detection and live-chat trimming
- summary rebuild/retention strategy controlled by config

## Memory subsystem (current behavior)

### LTM (implemented + active)
- Candidate schema: `MemoryCandidate` (`text`, `type`, `tags`, `ttl_days`, `source`, `why_store`)
- Approval ledger: append-only JSONL (`ApprovalLedger`)
- Apply decisions: `apply_approval_decisions(...)`
- Storage backend in use: `FileLTMStore` (JSONL append-only)

### STM (implemented substrate, currently not active in chat turn execution)
`bob/memory/stm_store.py` provides:
- Chroma-backed store with JSONL fallback
- TTL pruning
- injection refresh window
- access/session counters
- promotion candidate marking/status tracking

But base and TURBOTIME chat turn pipelines currently do not call `stm.query(...)` or `stm.add_turn(...)` in `run_turn_stream`.

### Practice pipeline
`/practice` (CLI) and Gradio “Load practice candidates” can generate candidate memories for human approval.
No direct auto-write to LTM occurs without approval decisions.

## Tooling and sandbox
- Sandbox config:
  - `BOB_TOOL_SANDBOX_ENABLED`
  - `BOB_TOOL_ROOTS`
- `ToolSandbox.check_path(...)` enforces allowed roots when sandbox is enabled.
- TURBOTIME tool registry exposes public tool names:
  - `scryfall.lookup`
  - `steam.game_lookup`
  - `game.knowledge_search`
  - `news.headline_search`
- In current TURBOTIME execution, selected enabled tools are executed with `bypass_sandbox=True`.

## Interfaces
- CLI (`bob/cli.py`): chat loop + `/mtg play`, `/turbotime`, `/practice`, inline memory approval.
- Gradio UI (`bob/ui/gradio_app.py`): chat, STM views, memory approval/editor, TURBOTIME selector, DPG launcher.

## MTG boundary
`bob/` orchestrates and routes; authoritative MTG rules/state/action legality remain in `mtg_core/`.

## Known implementation reality (not aspirational)
- No automatic LTM commit exists.
- Memory proposals are currently driven by practice/manual flows (not emitted by normal turn execution).
- Continuity state is compact but includes summary/live_chat and metadata beyond just `active_context/open_threads`.
