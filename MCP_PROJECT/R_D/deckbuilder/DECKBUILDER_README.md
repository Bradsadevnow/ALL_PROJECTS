# MTG Commander Deckbuilder

A complete Commander deckbuilding system that replaces the previous chat interface. This is a design-time collaboration tool between human and model for Magic: The Gathering Commander deck construction.

## Features

### Core Deckbuilding
- 🃏 **Commander-focused design** - Built specifically for Commander format
- 🎨 **Multi-panel interface** - Deck management, configuration, card management, lookup, and AI collaboration
- 💾 **Local persistence** - Save and load decks with full state preservation
- 🎯 **Per-deck isolation** - No global memory, no cross-deck bleed
- 📊 **Real-time validation** - Color identity checking and deck legality validation

### AI Collaboration
- 🤖 **Design partner model** - AI acts as a design collaborator, not a recommender
- 🧠 **Specialized context windows** - 5 separate context windows for different types of information
- 🔄 **Smart context management** - Automatic chat rebuilding when budget is reached
- 🚫 **No unprompted suggestions** - Model only responds to explicit requests or cuts
- 📚 **Bounded STM personalization** - Session-only abstract signals with required decay

### Card Management
- 🔍 **Scryfall integration** - Real-time card lookups with intelligent caching
- 🎨 **Card art caching** - Automatic download and caching of card artwork for session display
- 🎨 **Color validation** - Automatic color identity compliance checking
- 📝 **Rich metadata** - Track reasons, notes, and design decisions for each card
- ❌ **Rejected cards tracking** - Persistent list of cut cards with reasons
- 📊 **Card statistics** - Usage tracking and cache statistics

### Card Art Features
- 🖼️ **Automatic art download** - Card artwork is automatically downloaded when cards are looked up
- 🎨 **Medium art display** - Medium-sized card art displayed throughout the interface
- 💾 **Local caching** - Artwork is cached locally in `card_art_cache/` directory for fast access
- 🔄 **Session persistence** - Artwork remains available throughout the session
- 📊 **Cache management** - Intelligent cache with statistics and cleanup
- 🌐 **Multiple sizes** - Support for different art sizes (normal, large, etc.)

### Export & Integration
- 📤 **JSON export** - Complete deck export with metadata
- 🔄 **Context state export** - Debug and analysis of context management
- 📱 **Web interface** - Gradio-based responsive web UI
- 🔌 **LM Studio integration** - Connects to local AI models

## Architecture

### Core Components

1. **Deckbuilder Models** (`deckbuilder_models.py`)
   - `DeckState` - Authoritative deck state (never auto-filled)
   - `CardEntry` - Individual card with metadata
   - `RejectedCard` - Explicitly rejected cards
   - `DeckManager` - Manages multiple decks and persistence

2. **Scryfall Client** (`scryfall_client.py`)
   - Real-time card data fetching
   - Intelligent caching with TTL
   - Rate limiting and error handling
   - Color identity validation
   - Card art download and caching
   - Artwork display integration

3. **Context Manager** (`deckbuilder_context.py`)
   - 5 specialized context windows
   - Token counting and budget management
   - Automatic chat rebuilding
   - Per-deck context isolation

4. **Main Application** (`deckbuilder_app.py`)
   - Gradio web interface
   - AI collaboration integration
   - Complete UI workflow

### Context Windows

The system uses 5 specialized context windows:

1. **Live Chat** (30k tokens) - Raw conversation, rebuilt when full
2. **Working Deck Surface** (20k tokens) - Authoritative decklist + notes, never summarized
3. **Rejected Cards List** (15k tokens) - Explicitly rejected cards with reasons
4. **Lookup Index** (5k tokens) - Cards that have been looked up
5. **Conversation Summary** (1-2k tokens) - Rebuilt when chat resets

## Installation

### Requirements

- Python 3.8+
- LM Studio running with GPT-OSS 20B model
- LM Studio API accessible at 192.168.1.128:1234
- Internet connection for Scryfall API

### Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure LM Studio is running:**
   - Start LM Studio with GPT-OSS 20B loaded
   - Enable the "Local Server" in LM Studio settings
   - Verify the API is accessible at http://192.168.1.128:1234

3. **Start the application:**
   ```bash
   python main.py
   ```

## Usage

### Creating a New Deck

1. **Navigate to "Deck Management" tab**
2. **Enter commander name** and select color identity
3. **Click "Create Deck"**
4. **Configure deck strategy and constraints** in the "Deck Configuration" tab

### Adding Cards

1. **Go to "Card Management" tab**
2. **Enter card name** in the "Add Card" section
3. **Provide reason and notes** for the card choice
4. **Click "Add Card"**
5. **System validates color identity** automatically

### Card Lookup

1. **Navigate to "Card Lookup" tab**
2. **Enter card name** and click "Look Up Card"
3. **View card details** including stats, abilities, and pricing
4. **Card is automatically added to lookup index**

### AI Collaboration

1. **Go to "AI Collaboration" tab**
2. **Ask design questions** like:
   - "What are some good ramp spells for this deck?"
   - "How can I improve my mana curve?"
   - "What are the weaknesses of this strategy?"
3. **Model responds within deck context** - never makes unprompted suggestions
4. **Chat context is managed automatically** - rebuilt when needed

### Exporting

1. **Navigate to "Export" tab**
2. **Click "Export Deck"**
3. **View complete JSON export** including:
   - Full deck state
   - Design notes and constraints
   - Scryfall usage statistics
   - Context management data

## Design Philosophy

### Strict Invariants

This system follows strict design invariants:

- **Everything is deck-specific** - No global state, no cross-deck memory
- **UI is the only writer of state** - No auto-filling, no inference
- **No unprompted suggestions** - Model only responds to explicit requests
- **Per-deck STM only** - Personalization signals are in-memory, decaying, and reversible
- **Explicit constraints** - All preferences must be declared by the user

### Personalization Scope Contract (Locked)

Personalization is constrained to these domains only:

1. **Conversation** (STM, fast decay)
2. **Tools & Information Retrieval** (STM, medium decay)
3. **Opt-In Context Signals - Apple** (STM, required decay)

Hard guarantees:

- No personalization domain writes directly to long-term memory
- No personalization domain can override explicit user instructions
- No raw cross-domain sharing; only abstracted STM signals are used
- Out-of-scope signals (identifiers, location, social graph, biometric/health, inferred identity) are rejected

### Model Role

The AI model acts as a **design partner**, not a recommender:

- ✅ **Can do:** Explain, evaluate, compare, challenge, ask clarifying questions
- ❌ **Cannot do:** Invent goals, make unprompted suggestions, mutate deck state
- ✅ **Responds to:** Explicit constraints, cut requests, design questions
- ❌ **Ignores:** Implicit preferences, unspoken goals, assumed knowledge

### Context Management

The system uses sophisticated context management:

- **5 specialized windows** for different types of information
- **Automatic rebuilding** when chat hits budget limits
- **Persistent storage** for authoritative deck state only (not personalization signals)
- **Smart caching** for card data and lookups
- **Token counting** to prevent context overflow

## File Structure

```
deckbuilder/
├── main.py                    # Entry point - launches DeckbuilderApp
├── deckbuilder_app.py         # Main application and Gradio interface
├── deckbuilder_models.py      # Data models and deck management
├── deckbuilder_context.py     # Context management for deckbuilding
├── scryfall_client.py         # Scryfall API integration with caching
├── lm_studio_client.py        # LM Studio API client (existing)
├── context_manager.py         # Original context manager (existing)
├── requirements.txt           # Python dependencies
└── deck_data/                 # Local deck storage (created at runtime)
    └── [deck_id].json         # Individual deck files
```

## Troubleshooting

### Connection Issues
- **Check LM Studio**: Ensure LM Studio is running and API server is enabled
- **Verify IP/Port**: Confirm 192.168.1.128:1234 is correct for your setup
- **Network Access**: Ensure your machine can reach the LM Studio server

### Scryfall API Issues
- **Rate Limiting**: System includes rate limiting (10 requests/second)
- **Caching**: Card data is cached to reduce API calls
- **Fallback**: Graceful handling of API failures

### Card Art Issues
- **Art download**: Automatic when cards are looked up in "Card Lookup" tab
- **Cache directory**: Artwork stored in `card_art_cache/` directory
- **Network issues**: Art may fail to download if Scryfall API is unavailable
- **Display**: Art appears in lookup tab and persists for session duration
- **Cleanup**: Art cache can be manually cleared if needed

### Context Management
- **Chat rebuilding**: Automatic when 30k token limit is reached
- **Token counting**: Accurate counting with tiktoken
- **Memory management**: Efficient handling of large context windows

### Deck Validation
- **Color identity**: Automatic validation of card colors
- **Card limits**: Enforces 99-card limit (commander separate)
- **Duplicate prevention**: Prevents adding the same card twice

## Development

### Adding New Features

1. **Follow the strict invariants** - no global memory, UI-controlled state
2. **Use existing context windows** - don't create new ones without justification
3. **Maintain per-deck isolation** - no cross-deck data sharing
4. **Respect the model role** - keep it as a design partner, not a recommender

### Testing

The system includes comprehensive error handling and validation:

- **Input validation** for all user inputs
- **API error handling** for external services
- **State validation** for deck legality
- **Context management** for token limits

### Performance

- **Caching**: Scryfall data is cached with TTL
- **Token counting**: Efficient token counting with fallbacks
- **Context rebuilding**: Smart rebuilding to maintain conversation flow
- **Memory management**: Proper cleanup and resource management

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the logs in the console
3. Verify your LM Studio and Scryfall API configuration
4. Ensure all dependencies are installed correctly

## Future Enhancements

- [ ] Advanced card search and filtering
- [ ] Deck comparison and analysis tools
- [ ] Integration with deck tracking services
- [ ] Mobile-responsive interface improvements
- [ ] Advanced statistics and analytics
- [ ] Multi-user collaboration features