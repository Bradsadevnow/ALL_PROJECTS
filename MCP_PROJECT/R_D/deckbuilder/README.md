# MTG Commander Deckbuilder

This repository now runs a **Commander deckbuilding application** (Gradio UI) with Scryfall lookups, deck persistence, and LM Studio collaboration.

> Primary detailed docs: `DECKBUILDER_README.md`

## Current Capabilities (Codebase Sweep)

### App / UI (`deckbuilder_app.py`)
- Home-first flow: load/open/delete existing decks
- Scryfall search flow with commander detection and "create deck from commander"
- Workspace gated by active deck
- Card management (add/remove/cut) with rejected-card tracking
- Deck configuration + design notes updates
- AI collaboration tab (LM Studio-backed)
- Deck export as JSON

### Deck/Data Models (`deckbuilder_models.py`)
- Authoritative deck state (`DeckState`) persisted per deck JSON
- Per-deck session object (`DesignSession`) for **STM-only personalization signals**
- Personalization signals are:
  - bounded
  - decaying
  - reversible
  - **not persisted** to disk

### Personalization Policy (`personalization_policy.py`)
- Locked allowed domains:
  1. conversation
  2. tools_ir
  3. opt_in_context_apple
- Hard key validation per domain
- Out-of-scope signal rejection
- TTL-based decay windows per domain

### Context Management (`deckbuilder_context.py`)
- 5-window context strategy:
  - live_chat
  - working_deck
  - rejected_cards
  - lookup_index
  - conversation_summary
- Chat rebuild/summarization when budget is reached
- Non-authoritative injection of abstract personalization signals

### Integrations
- `scryfall_client.py`: cached card lookup, color validation, art download/cache
- `lm_studio_client.py`: model discovery + chat completion requests

### Tests
- `test_deckbuilder.py` includes:
  - deck model tests
  - context manager tests
  - STM-only personalization policy tests
  - LM Studio connectivity checks (warning-only when unavailable)
  - full integration smoke test

## TODO Status (Current)

### UX Redesign (`UX_REDESIGN_TODO.md`)
- [x] Gather redesign plan
- [x] Analyze current UI/UX implementation
- [x] Identify navigation/layout modules
- [x] Draft new launch-flow structure
- [x] Add Home tab / landing panel
- [x] Move load/deck logic into Home flow
- [x] Gate workspace until deck is active
- [x] Add breadcrumb/state display
- [x] Update workspace navigation buttons
- [x] Run tests and validate functionality
- [ ] Verify UI changes meet user expectations

### Open Enhancements
- See `DECKBUILDER_README.md` "Future Enhancements" for backlog items.

## Run

```bash
python main.py
```

Or:

```bash
bash run_app.sh
```