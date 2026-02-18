"""
Deckbuilder-specific context management.
Adapts the existing context system for deckbuilding with specialized windows.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Generator
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from deckbuilder_models import DeckState
from scryfall_client import ScryfallClient, CardData

logger = logging.getLogger(__name__)

class ContextWindowType(Enum):
    """Types of context windows in the deckbuilding system."""
    LIVE_CHAT = "live_chat"           # 30k tokens - Raw conversation
    WORKING_DECK = "working_deck"     # 20k tokens - Authoritative decklist + notes
    REJECTED_CARDS = "rejected_cards" # 15k tokens - Explicitly rejected cards
    LOOKUP_INDEX = "lookup_index"     # 5k tokens - Cards that have been looked up
    CONVERSATION_SUMMARY = "conversation_summary"  # 1-2k tokens - Rebuilt when chat resets


@dataclass
class ContextWindow:
    """Represents a specific context window with its own budget and content."""
    window_type: ContextWindowType
    max_tokens: int
    content: List[Dict[str, Any]]
    current_tokens: int = 0
    
    def add_content(self, item: Dict[str, Any], token_count: int) -> bool:
        """Add content to window if within token limit."""
        if self.current_tokens + token_count > self.max_tokens:
            return False
        
        self.content.append(item)
        self.current_tokens += token_count
        return True
    
    def get_content(self) -> List[Dict[str, Any]]:
        """Get current content."""
        return self.content.copy()
    
    def clear_content(self) -> None:
        """Clear content (for rebuildable windows only)."""
        if self.window_type in [ContextWindowType.LIVE_CHAT, ContextWindowType.CONVERSATION_SUMMARY]:
            self.content.clear()
            self.current_tokens = 0
    
    def get_token_usage(self) -> float:
        """Get token usage percentage."""
        return self.current_tokens / self.max_tokens if self.max_tokens > 0 else 0


class DeckbuilderContextManager:
    """
    Manages multiple context windows for deckbuilding.
    Follows the strict invariants: per-deck, no global memory, UI-controlled state.
    """
    
    def __init__(self, deck_state: DeckState, scryfall_client: ScryfallClient):
        self.deck_state = deck_state
        self.scryfall_client = scryfall_client
        
        # Initialize context windows with specific budgets
        self.windows = {
            ContextWindowType.LIVE_CHAT: ContextWindow(
                window_type=ContextWindowType.LIVE_CHAT,
                max_tokens=30000,
                content=[]
            ),
            ContextWindowType.WORKING_DECK: ContextWindow(
                window_type=ContextWindowType.WORKING_DECK,
                max_tokens=20000,
                content=[]
            ),
            ContextWindowType.REJECTED_CARDS: ContextWindow(
                window_type=ContextWindowType.REJECTED_CARDS,
                max_tokens=15000,
                content=[]
            ),
            ContextWindowType.LOOKUP_INDEX: ContextWindow(
                window_type=ContextWindowType.LOOKUP_INDEX,
                max_tokens=5000,
                content=[]
            ),
            ContextWindowType.CONVERSATION_SUMMARY: ContextWindow(
                window_type=ContextWindowType.CONVERSATION_SUMMARY,
                max_tokens=2000,
                content=[]
            )
        }
        
        # Token counting
        self.tokenizer = None  # Will be initialized when needed
        self.total_tokens = 0
        
        # State tracking
        self.chat_rebuild_needed = False
        self.deck_modified = False
        
        # Initialize working deck content
        self._update_working_deck_window()
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        try:
            if self.tokenizer is None:
                import tiktoken
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
            
            return len(self.tokenizer.encode(text))
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Fallback estimation
            return max(1, len(text) // 4)
    
    def add_chat_message(self, role: str, content: str) -> bool:
        """Add a message to the live chat window."""
        token_count = self.count_tokens(content)
        
        if self.windows[ContextWindowType.LIVE_CHAT].add_content({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }, token_count):
            self._recalculate_total_tokens()
            return True
        
        # Chat window full - mark for rebuild
        self.chat_rebuild_needed = True
        return False
    
    def get_chat_messages(self) -> List[Dict[str, Any]]:
        """Get current chat messages."""
        return self.windows[ContextWindowType.LIVE_CHAT].get_content()
    
    def rebuild_chat_context(self, lm_client) -> bool:
        """
        Rebuild chat context when it hits the budget.
        Summarizes conversation and rebuilds from summary.
        """
        if not self.chat_rebuild_needed:
            return True
        
        logger.info("Rebuilding chat context...")
        
        # Get current chat content
        chat_content = self.windows[ContextWindowType.LIVE_CHAT].get_content()
        if not chat_content:
            self.chat_rebuild_needed = False
            return True
        
        # Build conversation text for summarization
        conversation_text = ""
        for msg in chat_content:
            conversation_text += f"{msg['role'].upper()}: {msg['content']}\n\n"
        
        # Create summarization prompt
        summarization_prompt = f"""Please provide a concise summary of the following deckbuilding conversation, focusing on:

1. Key design decisions made
2. Cards added or removed
3. Strategy discussions
4. Constraints and preferences mentioned
5. Any unresolved questions or issues

Keep the summary under 1000 words and maintain the essential context needed to continue the deckbuilding session meaningfully.

Conversation:
{conversation_text}"""
        
        try:
            # Generate summary using the model
            summary_chunks = []
            for chunk in lm_client.chat_completion(
                messages=[{"role": "user", "content": summarization_prompt}],
                model="gpt-oss-20b",
                max_tokens=1500,
                temperature=0.3,
                stream=False
            ):
                summary_chunks.append(chunk)
            
            summary = "".join(summary_chunks)
            
            # Clear chat window and add summary
            self.windows[ContextWindowType.LIVE_CHAT].clear_content()
            summary_tokens = self.count_tokens(summary)
            self.windows[ContextWindowType.LIVE_CHAT].add_content({
                'role': 'system',
                'content': f"Conversation Summary:\n\n{summary}",
                'timestamp': datetime.now().isoformat()
            }, summary_tokens)
            
            # Add conversation summary window
            self.windows[ContextWindowType.CONVERSATION_SUMMARY].clear_content()
            self.windows[ContextWindowType.CONVERSATION_SUMMARY].add_content({
                'summary': summary,
                'timestamp': datetime.now().isoformat()
            }, self.count_tokens(summary))
            
            self.chat_rebuild_needed = False
            self._recalculate_total_tokens()
            
            logger.info("Chat context rebuilt successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error rebuilding chat context: {e}")
            return False
    
    def _update_working_deck_window(self) -> None:
        """Update the working deck window with current deck state."""
        # Clear existing content
        self.windows[ContextWindowType.WORKING_DECK].clear_content()
        
        # Build deck representation
        deck_content = {
            'deck_id': self.deck_state.deck_id,
            'commander': self.deck_state.commander,
            'color_identity': [c.value for c in self.deck_state.color_identity],
            'strategy': self.deck_state.strategy.value,
            'constraints': self.deck_state.constraints.to_dict(),
            'design_notes': self.deck_state.design_notes.to_dict(),
            'cards': [card.to_dict() for card in self.deck_state.cards],
            'card_count': len(self.deck_state.cards),
            'last_modified': self.deck_state.last_modified.isoformat()
        }
        
        content_str = json.dumps(deck_content, indent=2)
        token_count = self.count_tokens(content_str)
        
        self.windows[ContextWindowType.WORKING_DECK].add_content(deck_content, token_count)
        self._recalculate_total_tokens()
    
    def update_deck_state(self, deck_state: DeckState) -> None:
        """Update deck state and refresh working deck window."""
        self.deck_state = deck_state
        self.deck_modified = True
        self._update_working_deck_window()
    
    def add_rejected_card(self, card_name: str, reason: str) -> None:
        """Add a rejected card to the rejected cards window."""
        rejected_entry = {
            'name': card_name,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
        
        content_str = f"{card_name}: {reason}"
        token_count = self.count_tokens(content_str)
        
        # Add to rejected cards window
        self.windows[ContextWindowType.REJECTED_CARDS].add_content(rejected_entry, token_count)
        
        # Also add to lookup index if not already there
        if not any(item['name'] == card_name for item in self.windows[ContextWindowType.LOOKUP_INDEX].content):
            self.windows[ContextWindowType.LOOKUP_INDEX].add_content({
                'name': card_name,
                'type': 'rejected'
            }, self.count_tokens(card_name))
        
        self._recalculate_total_tokens()
    
    def add_lookup_index(self, card_name: str, card_type: str = 'looked_up') -> None:
        """Add a card to the lookup index."""
        if not any(item['name'] == card_name for item in self.windows[ContextWindowType.LOOKUP_INDEX].content):
            self.windows[ContextWindowType.LOOKUP_INDEX].add_content({
                'name': card_name,
                'type': card_type,
                'timestamp': datetime.now().isoformat()
            }, self.count_tokens(card_name))
            self._recalculate_total_tokens()
    
    def get_context_for_api(self, personalization_signals: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get all context windows formatted for API calls.
        This is the main method used when calling the model.
        """
        context_messages = []

        # Add bounded STM personalization signals (abstract only, non-authoritative)
        if personalization_signals:
            context_messages.append({
                'role': 'system',
                'content': (
                    "Session Personalization Signals (STM-only, abstract, non-authoritative):\n"
                    f"{json.dumps(personalization_signals, indent=2)}"
                )
            })
        
        # Add conversation summary if available (non-authoritative)
        summary_window = self.windows[ContextWindowType.CONVERSATION_SUMMARY]
        if summary_window.content:
            context_messages.append({
                'role': 'system',
                'content': f"Conversation Summary (non-authoritative):\n{summary_window.content[0]['summary']}"
            })
        
        # Add working deck surface (authoritative)
        deck_window = self.windows[ContextWindowType.WORKING_DECK]
        if deck_window.content:
            deck_data = deck_window.content[0]
            deck_summary = f"""Current Deck State (Authoritative):
Commander: {deck_data['commander']}
Colors: {', '.join(deck_data['color_identity'])}
Strategy: {deck_data['strategy']}
Cards in deck: {deck_data['card_count']}/99
Constraints: {json.dumps(deck_data['constraints'], indent=2)}
Design Notes: {json.dumps(deck_data['design_notes'], indent=2)}"""
            
            context_messages.append({
                'role': 'system',
                'content': deck_summary
            })
        
        # Add rejected cards list
        rejected_window = self.windows[ContextWindowType.REJECTED_CARDS]
        if rejected_window.content:
            rejected_list = "\n".join([
                f"- {item['name']}: {item['reason']}"
                for item in rejected_window.content[-10:]  # Last 10 rejections
            ])
            context_messages.append({
                'role': 'system',
                'content': f"Recently Rejected Cards:\n{rejected_list}"
            })
        
        # Add lookup index
        lookup_window = self.windows[ContextWindowType.LOOKUP_INDEX]
        if lookup_window.content:
            looked_up = [item['name'] for item in lookup_window.content if item['type'] == 'looked_up']
            rejected_index = [item['name'] for item in lookup_window.content if item['type'] == 'rejected']
            
            index_summary = f"""Lookup Index:
Looked up: {', '.join(looked_up[-5:])}  # Last 5 looked up
Rejected: {', '.join(rejected_index[-5:])}  # Last 5 rejected"""
            
            context_messages.append({
                'role': 'system',
                'content': index_summary
            })
        
        # Add current chat messages
        chat_window = self.windows[ContextWindowType.LIVE_CHAT]
        context_messages.extend(chat_window.get_content())
        
        return context_messages
    
    def get_token_usage_report(self) -> Dict[str, Any]:
        """Get detailed token usage report."""
        window_reports = {}
        total_tokens = 0
        
        for window_type, window in self.windows.items():
            usage = window.get_token_usage()
            window_reports[window_type.value] = {
                'current_tokens': window.current_tokens,
                'max_tokens': window.max_tokens,
                'usage_percentage': usage * 100,
                'content_count': len(window.content)
            }
            total_tokens += window.current_tokens
        
        return {
            'total_tokens': total_tokens,
            'max_total_tokens': sum(window.max_tokens for window in self.windows.values()),
            'windows': window_reports,
            'chat_rebuild_needed': self.chat_rebuild_needed,
            'deck_modified': self.deck_modified
        }
    
    def should_collapse(self) -> bool:
        """Check if any window needs collapsing (should not happen with proper budgets)."""
        for window in self.windows.values():
            if window.get_token_usage() > 0.95:  # 95% threshold
                return True
        return False
    
    def clear_chat(self) -> None:
        """Clear chat history (preserves other windows)."""
        self.windows[ContextWindowType.LIVE_CHAT].clear_content()
        self.windows[ContextWindowType.CONVERSATION_SUMMARY].clear_content()
        self.chat_rebuild_needed = False
        self._recalculate_total_tokens()
    
    def _recalculate_total_tokens(self) -> None:
        """Recalculate total token usage."""
        self.total_tokens = sum(window.current_tokens for window in self.windows.values())
    
    def get_working_deck_summary(self) -> str:
        """Get a summary of the current working deck."""
        return f"""Current Deck:
Commander: {self.deck_state.commander}
Colors: {self.deck_state.colors_str}
Strategy: {self.deck_state.strategy.value}
Cards: {len(self.deck_state.cards)}/99
Last Modified: {self.deck_state.last_modified.strftime('%Y-%m-%d %H:%M')}"""
    
    def export_context_state(self) -> Dict[str, Any]:
        """Export current context state for debugging or persistence."""
        return {
            'deck_id': self.deck_state.deck_id,
            'windows': {
                window_type.value: {
                    'content': window.content,
                    'current_tokens': window.current_tokens,
                    'max_tokens': window.max_tokens
                }
                for window_type, window in self.windows.items()
            },
            'total_tokens': self.total_tokens,
            'chat_rebuild_needed': self.chat_rebuild_needed,
            'deck_modified': self.deck_modified,
            'exported_at': datetime.now().isoformat()
        }