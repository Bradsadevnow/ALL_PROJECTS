"""
Deckbuilder data models for Magic: The Gathering Commander deck construction.
Follows the strict invariants: per-deck state, no global memory, UI-controlled state only.
"""

import json
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Optional, Set, Any
from dataclasses import dataclass, asdict, field
from enum import Enum

from personalization_policy import (
    PersonalizationDomain,
    DEFAULT_DOMAIN_TTLS_SECONDS,
    SignalRecord,
    validate_signal,
)


logger = logging.getLogger(__name__)


class Color(Enum):
    """Magic: The Gathering colors."""
    WHITE = "W"
    BLUE = "U"
    BLACK = "B"
    RED = "R"
    GREEN = "G"


class DeckStrategy(Enum):
    """Common Commander deck strategies."""
    AGGRO = "aggro"
    CONTROL = "control"
    COMBO = "combo"
    RAMP = "ramp"
    PRISON = "prison"
    VOLTRON = "voltron"
    MELF = "melf"
    STAX = "stax"
    TURBO_STAX = "turbo_stax"
    REANIMATOR = "reanimator"
    TOKENS = "tokens"
    MATH = "math"
    POLITICS = "politics"
    OTHER = "other"


@dataclass
class CardEntry:
    """Represents a card in the deck with metadata."""
    name: str
    count: int = 1
    reason: str = ""  # Why this card was chosen
    notes: str = ""   # Additional design notes
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CardEntry':
        """Create from dictionary."""
        data = data.copy()
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class RejectedCard:
    """Represents a card that was explicitly rejected or cut."""
    name: str
    reason: str  # Why it was rejected/cut
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RejectedCard':
        """Create from dictionary."""
        data = data.copy()
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class DeckConstraints:
    """Constraints and preferences for deck building."""
    max_power_level: Optional[int] = None  # 1-10 scale
    budget_limit: Optional[float] = None   # USD
    banned_patterns: List[str] = field(default_factory=list)  # e.g., "no infinite combos"
    social_contract: List[str] = field(default_factory=list)  # e.g., "no stax", "casual only"
    time_limit_minutes: Optional[int] = None  # Max game length preference
    complexity_limit: Optional[int] = None   # 1-10 scale
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeckConstraints':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class DesignNotes:
    """Design context and notes for the deck."""
    vibe: str = ""  # "jank", "competitive", "thematic", etc.
    goals: List[str] = field(default_factory=list)  # Specific design goals
    known_weakspots: List[str] = field(default_factory=list)  # Acknowledged weaknesses
    inspiration: str = ""  # What inspired this deck
    target_meta: str = ""  # What meta it's designed for
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DesignNotes':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class DeckState:
    """
    Authoritative deck state - written ONLY by the UI.
    Never inferred, never auto-filled, never learned.
    """
    deck_id: str
    commander: str
    color_identity: Set[Color]
    strategy: DeckStrategy
    constraints: DeckConstraints
    design_notes: DesignNotes
    cards: List[CardEntry]  # 99 cards (commander separate)
    rejected_cards: List[RejectedCard]
    created_at: datetime
    last_modified: datetime
    
    def __post_init__(self):
        # Validate deck structure
        if len(self.cards) > 99:
            raise ValueError("Deck cannot have more than 99 cards (commander separate)")
        
        # Validate commander is not in main deck
        commander_names = [card.name.lower() for card in self.cards]
        if self.commander.lower() in commander_names:
            raise ValueError("Commander cannot be in the main deck")
    
    @property
    def total_cards(self) -> int:
        """Total cards in deck including commander."""
        return len(self.cards) + 1
    
    @property
    def colors_str(self) -> str:
        """Color identity as string (e.g., 'WUBRG')."""
        return ''.join(sorted([c.value for c in self.color_identity]))
    
    def add_card(self, card_name: str, reason: str = "", notes: str = "") -> bool:
        """Add a card to the deck (UI-controlled operation)."""
        if len(self.cards) >= 99:
            return False
        
        # Check for duplicates
        for card in self.cards:
            if card.name.lower() == card_name.lower():
                return False  # Card already in deck
        
        new_card = CardEntry(
            name=card_name,
            reason=reason,
            notes=notes
        )
        self.cards.append(new_card)
        self.last_modified = datetime.now()
        return True
    
    def remove_card(self, card_name: str) -> bool:
        """Remove a card from the deck (UI-controlled operation)."""
        for i, card in enumerate(self.cards):
            if card.name.lower() == card_name.lower():
                self.cards.pop(i)
                self.last_modified = datetime.now()
                return True
        return False
    
    def cut_card(self, card_name: str, reason: str) -> bool:
        """Cut a card from the deck and add to rejected list."""
        if self.remove_card(card_name):
            rejected = RejectedCard(name=card_name, reason=reason)
            self.rejected_cards.append(rejected)
            return True
        return False
    
    def update_commander(self, commander_name: str, colors: Set[Color]) -> None:
        """Update commander and color identity (UI-controlled)."""
        self.commander = commander_name
        self.color_identity = colors
        self.last_modified = datetime.now()
    
    def update_strategy(self, strategy: DeckStrategy) -> None:
        """Update deck strategy (UI-controlled)."""
        self.strategy = strategy
        self.last_modified = datetime.now()
    
    def update_constraints(self, constraints: DeckConstraints) -> None:
        """Update deck constraints (UI-controlled)."""
        self.constraints = constraints
        self.last_modified = datetime.now()
    
    def update_design_notes(self, design_notes: DesignNotes) -> None:
        """Update design notes (UI-controlled)."""
        self.design_notes = design_notes
        self.last_modified = datetime.now()
    
    def validate_legality(self) -> List[str]:
        """Validate deck legality and return list of issues."""
        issues = []
        
        # Check card count
        if len(self.cards) != 99:
            issues.append(f"Deck must have exactly 99 cards, currently has {len(self.cards)}")
        
        # Check for basic lands (should be in main deck, not commander)
        if self.commander.lower() in ['plains', 'island', 'swamp', 'mountain', 'forest']:
            issues.append("Commander cannot be a basic land")
        
        # Check color identity compliance (simplified - would need card data for full validation)
        # This is where Scryfall integration would validate actual card colors
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'deck_id': self.deck_id,
            'commander': self.commander,
            'color_identity': [c.value for c in self.color_identity],
            'strategy': self.strategy.value,
            'constraints': self.constraints.to_dict(),
            'design_notes': self.design_notes.to_dict(),
            'cards': [card.to_dict() for card in self.cards],
            'rejected_cards': [card.to_dict() for card in self.rejected_cards],
            'created_at': self.created_at.isoformat(),
            'last_modified': self.last_modified.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeckState':
        """Create from dictionary."""
        data = data.copy()
        
        # Convert color identity back to enum
        data['color_identity'] = {Color(c) for c in data['color_identity']}
        
        # Convert strategy back to enum
        data['strategy'] = DeckStrategy(data['strategy'])
        
        # Convert nested objects
        data['constraints'] = DeckConstraints.from_dict(data['constraints'])
        data['design_notes'] = DesignNotes.from_dict(data['design_notes'])
        data['cards'] = [CardEntry.from_dict(card) for card in data['cards']]
        data['rejected_cards'] = [RejectedCard.from_dict(card) for card in data['rejected_cards']]
        
        # Convert timestamps
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_modified'] = datetime.fromisoformat(data['last_modified'])
        
        return cls(**data)
    
    @classmethod
    def create_new(cls, commander: str, colors: Set[Color]) -> 'DeckState':
        """Create a new deck state."""
        return cls(
            deck_id=str(uuid.uuid4()),
            commander=commander,
            color_identity=colors,
            strategy=DeckStrategy.OTHER,
            constraints=DeckConstraints(),
            design_notes=DesignNotes(),
            cards=[],
            rejected_cards=[],
            created_at=datetime.now(),
            last_modified=datetime.now()
        )


@dataclass
class DesignSession:
    """
    Per-deck design session with strict, bounded STM personalization.
    In-memory only by policy (not persisted to disk).
    """
    deck_id: str
    stm_signals: Dict[str, List[SignalRecord]] = field(default_factory=lambda: {
        PersonalizationDomain.CONVERSATION.value: [],
        PersonalizationDomain.TOOLS_IR.value: [],
        PersonalizationDomain.OPT_IN_CONTEXT_APPLE.value: [],
    })
    last_updated: datetime = field(default_factory=datetime.now)

    def add_signal(self, domain: PersonalizationDomain, key: str, value: Any) -> bool:
        """Add a validated STM personalization signal."""
        is_valid, reason = validate_signal(domain, key, value)
        if not is_valid:
            logger.debug(f"Rejected personalization signal ({domain.value}:{key}) due to {reason}")
            return False

        ttl_seconds = DEFAULT_DOMAIN_TTLS_SECONDS[domain]
        signal = SignalRecord.create(domain=domain, key=key, value=value, ttl_seconds=ttl_seconds)

        domain_key = domain.value
        if domain_key not in self.stm_signals:
            self.stm_signals[domain_key] = []

        self._prune_expired()
        self.stm_signals[domain_key].append(signal)

        # Keep only the most recent 20 signals per domain to remain bounded.
        self.stm_signals[domain_key] = self.stm_signals[domain_key][-20:]
        self.last_updated = datetime.now()
        return True

    def _prune_expired(self) -> None:
        """Prune expired signals across all domains."""
        now = datetime.now()
        for domain_key, records in self.stm_signals.items():
            self.stm_signals[domain_key] = [r for r in records if not r.is_expired(now)]
    
    def get_preferences(self) -> Dict[str, Any]:
        """Get active, abstracted STM preferences by domain."""
        self._prune_expired()

        def latest_by_key(records: List[SignalRecord]) -> Dict[str, Any]:
            ordered: Dict[str, Any] = {}
            for record in records:
                ordered[record.key] = record.value
            return ordered

        return {
            'conversation': latest_by_key(self.stm_signals[PersonalizationDomain.CONVERSATION.value]),
            'tools_ir': latest_by_key(self.stm_signals[PersonalizationDomain.TOOLS_IR.value]),
            'opt_in_context_apple': latest_by_key(self.stm_signals[PersonalizationDomain.OPT_IN_CONTEXT_APPLE.value]),
        }

    def clear_signals(self) -> None:
        """Clear all personalization signals (reversible by design)."""
        for domain_key in list(self.stm_signals.keys()):
            self.stm_signals[domain_key] = []
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for debugging/export only (not persisted)."""
        self._prune_expired()
        return {
            'deck_id': self.deck_id,
            'stm_signals': {
                domain_key: [record.to_dict() for record in records]
                for domain_key, records in self.stm_signals.items()
            },
            'last_updated': self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DesignSession':
        """
        Create from dictionary.
        Session persistence is intentionally ignored for STM-only policy.
        """
        deck_id = data.get('deck_id')
        if not deck_id:
            raise ValueError("Missing deck_id for DesignSession")
        return cls(deck_id=deck_id)


class DeckManager:
    """Manages multiple deck states and sessions."""
    
    def __init__(self, data_dir: str = "deck_data"):
        self.data_dir = data_dir
        self.ensure_data_dir()
        self.active_deck_id: Optional[str] = None
        self.decks: Dict[str, DeckState] = {}
        self.sessions: Dict[str, DesignSession] = {}
    
    def ensure_data_dir(self) -> None:
        """Ensure data directory exists."""
        import os
        os.makedirs(self.data_dir, exist_ok=True)
    
    def create_new_deck(self, commander: str, colors: Set[Color]) -> str:
        """Create a new deck and return its ID."""
        deck = DeckState.create_new(commander, colors)
        self.decks[deck.deck_id] = deck
        self.sessions[deck.deck_id] = DesignSession(deck.deck_id)
        self.active_deck_id = deck.deck_id
        self.save_deck(deck.deck_id)
        return deck.deck_id
    
    def get_active_deck(self) -> Optional[DeckState]:
        """Get the currently active deck."""
        if self.active_deck_id and self.active_deck_id in self.decks:
            return self.decks[self.active_deck_id]
        return None
    
    def get_active_session(self) -> Optional[DesignSession]:
        """Get the currently active design session."""
        if self.active_deck_id and self.active_deck_id in self.sessions:
            return self.sessions[self.active_deck_id]
        return None
    
    def switch_deck(self, deck_id: str) -> bool:
        """Switch to a different deck."""
        if deck_id in self.decks:
            self.active_deck_id = deck_id
            return True
        return False
    
    def save_deck(self, deck_id: Optional[str] = None) -> None:
        """Save a deck to disk."""
        deck_id = deck_id or self.active_deck_id
        if not deck_id or deck_id not in self.decks:
            return
        
        deck = self.decks[deck_id]
        data = {
            'deck': deck.to_dict(),
        }
        
        filepath = f"{self.data_dir}/{deck_id}.json"
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_deck(self, deck_id: str) -> bool:
        """Load a deck from disk."""
        filepath = f"{self.data_dir}/{deck_id}.json"
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            deck = DeckState.from_dict(data['deck'])
            # Session is intentionally reset at load to enforce STM-only personalization.
            _legacy_session = data.get('session')
            session = DesignSession(deck_id)
            
            self.decks[deck_id] = deck
            self.sessions[deck_id] = session
            self.active_deck_id = deck_id
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Error loading deck {deck_id}: {e}")
            return False
    
    def list_decks(self) -> List[Dict[str, Any]]:
        """List all saved decks."""
        decks = []
        for deck_id in self.decks:
            deck = self.decks[deck_id]
            decks.append({
                'id': deck_id,
                'commander': deck.commander,
                'colors': deck.colors_str,
                'strategy': deck.strategy.value,
                'created': deck.created_at.strftime("%Y-%m-%d %H:%M"),
                'modified': deck.last_modified.strftime("%Y-%m-%d %H:%M"),
                'card_count': len(deck.cards)
            })
        return sorted(decks, key=lambda x: x['modified'], reverse=True)
    
    def delete_deck(self, deck_id: str) -> bool:
        """Delete a deck and its data."""
        if deck_id not in self.decks:
            return False
        
        # Remove from memory
        del self.decks[deck_id]
        if deck_id in self.sessions:
            del self.sessions[deck_id]
        
        # Remove from disk
        import os
        filepath = f"{self.data_dir}/{deck_id}.json"
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # Switch active deck if needed
        if self.active_deck_id == deck_id:
            if self.decks:
                self.active_deck_id = list(self.decks.keys())[0]
            else:
                self.active_deck_id = None
        
        return True