# MTG Core — Deterministic Rules Engine

A complete, authoritative Magic: The Gathering rules engine for Phase 1. Designed as the engine layer for AI opponents and playtesting tools — it owns all game state and exposes a legal-action schema to any control surface (AI, CLI, TUI, GUI).

## Design Principles

- **Engine owns state**: No control surface can mutate game state directly. All actions go through the engine's validation and resolution pipeline.
- **Player-scoped visibility**: The engine generates `VisibleState` snapshots that hide opponent hand/library. AI only sees what a real player would see.
- **Schema-constrained AI**: The AI selects from a schema of legal actions — it cannot propose illegal moves. Hallucinations about game state are structurally impossible.
- **Deterministic replay**: Every action, trigger, and resolution is logged to `runtime/ai_trace.jsonl`. Any game can be replayed from logs.

## What It Implements

**Keywords**: flying, vigilance, double strike, first strike, haste, lifelink, deathtouch, trample, reach, flash, defender, hexproof, menace

**Triggered abilities**: ETB, dies, attacks, attacks-or-blocks, combat-damage-to-player, dealt-damage, becomes-target, upkeep, cast-spell, and more

**Activated abilities**: Mana costs, tap, discard, sacrifice, pay-life; sorcery-speed vs. instant-speed restrictions

**Continuous effects**: P/T modifiers, lords, keyword grants/removals, cost reduction, damage prevention

**Spell systems**: X costs, alternate costs, additional costs, flashback

**Combat**: First strike/double strike damage split, trample assignment, deathtouch + lifelink interaction, menace blocking restriction, flying/reach

**State-based actions**: Lethal damage, 0 toughness, deathtouch-marked, aura/equipment legality

45+ card effects implemented via data-driven rules — no hardcoded per-card behavior.

## Structure

| File | Role |
|------|------|
| `engine.py` | Full rules engine, action validation, state mutation (~4,400 lines) |
| `action_surface.py` | Legal action enumeration from VisibleState |
| `game_state.py` | Core types: zones, phases, permanents, stack |
| `cards.py` | Card model, Scryfall-derived schema, keyword/ability parsing |
| `ai_live.py` | LLM action selection with schema normalization |
| `ai_pregame.py` | Mulligan/bottom decisions (strict JSON I/O) |
| `ai_broker.py` | Async background loop for LLM calls |
| `run_game.py` | Game entry point |

**Data:**
- `data/cards_phase1.json` — Scryfall-derived card database
- `data/decks_phase1.json` — Decklist definitions

**Control surfaces:**
- `cli_base.py` — Terminal action selection
- `tui_base.py` — Textual TUI
- `dpg_ui.py` — Dear PyGui playtest interface (mouse-driven)
- `server/` — Web API surface

## Known Phase-1 Constraints (by design)

- Exactly two players
- No replacement effects; no comprehensive layer system (single derived continuous-effects pass)
- Trigger ordering is engine-defined (no APNAP player choice)
- Combat damage assignment to multiple blockers is engine-defined
- `Step.DAMAGE` is a placeholder; damage resolves at end of `DECLARE_BLOCKERS`

## Usage

```bash
cd mtg_core
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# TUI (default)
python run_game.py

# CLI
python run_game.py --ui cli

# DPG (mouse-driven GUI)
python run_game.py --ui dpg
```

Requires an OpenAI-compatible API endpoint. Set `OPENAI_API_KEY` (or configure `OPENROUTER_API_KEY` for OpenRouter).
