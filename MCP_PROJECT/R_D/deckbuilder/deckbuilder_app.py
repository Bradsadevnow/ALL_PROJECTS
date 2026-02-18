"""
Main Deckbuilder application - replaces the current chat interface.
Provides a complete Commander deckbuilding experience with AI collaboration.
"""

import gradio as gr
import json
import logging
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from deckbuilder_models import DeckManager, DeckState, DeckStrategy, Color, CardEntry, RejectedCard
from scryfall_client import ScryfallClient
from deckbuilder_context import DeckbuilderContextManager
from lm_studio_client import LMStudioClient

logger = logging.getLogger(__name__)

class DeckbuilderApp:
    """Main Deckbuilder application class."""
    
    def __init__(self):
        self.deck_manager = DeckManager()
        self.scryfall_client = ScryfallClient()
        self.lm_client = LMStudioClient()
        self.context_manager: Optional[DeckbuilderContextManager] = None
        
        # Initialize connection
        self.is_connected = self.lm_client.test_connection()
        if self.is_connected:
            logger.info("Successfully connected to LM Studio")
        else:
            logger.error("Failed to connect to LM Studio")
        
        # Load existing decks
        self._load_existing_decks()
    
    def _load_existing_decks(self) -> None:
        """Load existing decks from disk."""
        loaded_decks = 0
        data_dir = self.deck_manager.data_dir

        if not os.path.isdir(data_dir):
            return

        for filename in os.listdir(data_dir):
            if not filename.endswith('.json'):
                continue

            deck_id = filename.replace('.json', '')
            if self.deck_manager.load_deck(deck_id):
                loaded_decks += 1

        if loaded_decks:
            logger.info(f"Loaded {loaded_decks} deck(s) from disk")

        # Keep startup in a no-active-deck state for the home-first UX
        self.deck_manager.active_deck_id = None
    
    def get_status_info(self) -> str:
        """Get current status information."""
        status = "🟢 Connected" if self.is_connected else "🔴 Disconnected"
        
        active_deck = self.deck_manager.get_active_deck()
        if active_deck:
            deck_info = f" | Deck: {active_deck.commander} ({active_deck.colors_str}) - {len(active_deck.cards)}/99 cards"
        else:
            deck_info = " | No active deck"
        
        return f"{status}{deck_info}"

    def get_breadcrumb(self) -> str:
        """Get the current breadcrumb/state display."""
        active_deck = self.deck_manager.get_active_deck()
        if active_deck:
            return f"Home → {active_deck.commander}"
        return "Home"
    
    def create_new_deck(self, commander: str, colors: List[str]) -> Tuple[str, str, List[Dict]]:
        """Create a new deck and return updated UI state."""
        if not commander.strip():
            return "Please enter a commander name.", self.get_status_info(), []
        
        try:
            color_set = {Color(c) for c in colors}
            deck_id = self.deck_manager.create_new_deck(commander, color_set)
            
            # Initialize context manager
            deck_state = self.deck_manager.get_active_deck()
            self.context_manager = DeckbuilderContextManager(deck_state, self.scryfall_client)
            
            return f"Created new deck with commander: {commander}", self.get_status_info(), self._get_deck_list()
            
        except Exception as e:
            logger.error(f"Error creating deck: {e}")
            return f"Error creating deck: {str(e)}", self.get_status_info(), []
    
    def switch_deck(self, deck_id: str) -> Tuple[str, str, List[Dict]]:
        """Switch to a different deck."""
        if self.deck_manager.switch_deck(deck_id):
            deck_state = self.deck_manager.get_active_deck()
            self.context_manager = DeckbuilderContextManager(deck_state, self.scryfall_client)
            return f"Switched to deck: {deck_state.commander}", self.get_status_info(), self._get_deck_list()
        else:
            return "Failed to switch deck.", self.get_status_info(), []
    
    def delete_deck(self, deck_id: str) -> Tuple[str, List[Dict]]:
        """Delete a deck."""
        if self.deck_manager.delete_deck(deck_id):
            return "Deck deleted successfully.", self._get_deck_list()
        else:
            return "Failed to delete deck.", self._get_deck_list()

    def _get_deck_choices(self) -> List[Tuple[str, str]]:
        """Get deck choices for dropdowns as (label, value)."""
        choices: List[Tuple[str, str]] = []
        for deck_info in self.deck_manager.list_decks():
            label = (
                f"{deck_info['commander']} ({deck_info['colors'] or 'Colorless'})"
                f" • {deck_info['card_count']}/99 • Updated {deck_info['modified']}"
            )
            choices.append((label, deck_info['id']))
        return choices

    def _get_home_deck_rows(self) -> List[List[Any]]:
        """Get existing deck rows for home table display."""
        rows: List[List[Any]] = []
        for deck_info in self.deck_manager.list_decks():
            rows.append([
                deck_info['commander'],
                deck_info['colors'] or 'Colorless',
                deck_info['strategy'],
                deck_info['card_count'],
                deck_info['modified']
            ])
        return rows

    def _workspace_visibility_updates(self) -> Tuple[Any, Any]:
        """Get visibility updates for workspace and empty-state views."""
        has_active = self.deck_manager.get_active_deck() is not None
        return gr.update(visible=has_active), gr.update(visible=not has_active)

    def refresh_home_decks(self) -> Tuple[List[List[Any]], Any]:
        """Refresh home deck table and selector choices."""
        return (
            self._get_home_deck_rows(),
            gr.update(choices=self._get_deck_choices(), value=self.deck_manager.active_deck_id)
        )

    def open_existing_deck(self, deck_id: str) -> Tuple[str, str, List[Dict], List[Dict], Any, List[List[Any]], Any, Any]:
        """Open a deck from the home flow."""
        if not deck_id:
            workspace_visible, workspace_empty_visible = self._workspace_visibility_updates()
            return (
                "Select a deck to open.",
                self.get_status_info(),
                [],
                [],
                gr.update(choices=self._get_deck_choices()),
                self._get_home_deck_rows(),
                workspace_visible,
                workspace_empty_visible
            )

        if not self.deck_manager.switch_deck(deck_id):
            workspace_visible, workspace_empty_visible = self._workspace_visibility_updates()
            return (
                "Could not open that deck.",
                self.get_status_info(),
                [],
                [],
                gr.update(choices=self._get_deck_choices()),
                self._get_home_deck_rows(),
                workspace_visible,
                workspace_empty_visible
            )

        deck_state = self.deck_manager.get_active_deck()
        self.context_manager = DeckbuilderContextManager(deck_state, self.scryfall_client)
        workspace_visible, workspace_empty_visible = self._workspace_visibility_updates()

        return (
            f"Opened deck: {deck_state.commander}",
            self.get_status_info(),
            self._get_deck_list(),
            self._get_rejected_list(),
            gr.update(choices=self._get_deck_choices(), value=deck_id),
            self._get_home_deck_rows(),
            workspace_visible,
            workspace_empty_visible
        )

    def delete_existing_deck_home(self, deck_id: str) -> Tuple[str, str, List[Dict], List[Dict], Any, List[List[Any]], Any, Any]:
        """Delete a deck from the home flow."""
        if not deck_id:
            workspace_visible, workspace_empty_visible = self._workspace_visibility_updates()
            return (
                "Select a deck to delete.",
                self.get_status_info(),
                self._get_deck_list(),
                self._get_rejected_list(),
                gr.update(choices=self._get_deck_choices()),
                self._get_home_deck_rows(),
                workspace_visible,
                workspace_empty_visible
            )

        deleted = self.deck_manager.delete_deck(deck_id)
        active_deck = self.deck_manager.get_active_deck()

        if active_deck:
            self.context_manager = DeckbuilderContextManager(active_deck, self.scryfall_client)
        else:
            self.context_manager = None
        workspace_visible, workspace_empty_visible = self._workspace_visibility_updates()

        message = "Deck deleted." if deleted else "Could not delete deck."
        return (
            message,
            self.get_status_info(),
            self._get_deck_list(),
            self._get_rejected_list(),
            gr.update(choices=self._get_deck_choices(), value=None),
            self._get_home_deck_rows(),
            workspace_visible,
            workspace_empty_visible
        )

    def lookup_card_home(self, card_name: str) -> Tuple[str, Optional[str], str, Any, Any, str]:
        """Lookup card from home flow and expose commander action if applicable."""
        if not card_name.strip():
            return "Please enter a card name.", None, "", gr.update(visible=False), gr.update(visible=False), ""

        card_data = self.scryfall_client.search_card(card_name)
        if not card_data:
            return f"Card not found: {card_name}", None, "", gr.update(visible=False), gr.update(visible=False), ""

        summary = self.scryfall_client.get_card_summary(card_data)
        art_path = self.scryfall_client.get_card_art_path(card_name, "normal")
        is_commander = self._is_commander_card(card_data)

        if is_commander:
            summary += "\n\n✅ Commander candidate detected. You can create a new deck from this result."
            return (
                f"Card found: {card_name}",
                art_path,
                summary,
                gr.update(visible=True),
                gr.update(visible=True),
                card_data.name
            )

        return (
            f"Card found: {card_name}",
            art_path,
            summary,
            gr.update(visible=False),
            gr.update(visible=True),
            ""
        )

    def create_deck_from_home_lookup(self, commander_name: str) -> Tuple[str, str, List[Dict], List[Dict], Any, List[List[Any]], Any, Any]:
        """Create deck from home lookup commander action."""
        message, status, deck_list = self.create_deck_from_commander(commander_name)
        workspace_visible, workspace_empty_visible = self._workspace_visibility_updates()
        return (
            message,
            status,
            deck_list,
            self._get_rejected_list(),
            gr.update(choices=self._get_deck_choices(), value=self.deck_manager.active_deck_id),
            self._get_home_deck_rows(),
            workspace_visible,
            workspace_empty_visible
        )
    
    def search_card_for_addition(self, card_name: str) -> Tuple[str, Optional[str], str, str, bool]:
        """Search for a card and return details for confirmation."""
        if not card_name.strip():
            return "Please enter a card name.", None, "", "", False
        
        card_data = self.scryfall_client.search_card(card_name)
        if card_data:
            summary = self.scryfall_client.get_card_summary(card_data)
            art_path = self.scryfall_client.get_card_art_path(card_name, "normal")
            colors_str = self.scryfall_client.get_color_abbreviations(card_data.colors)
            
            # Check color identity validation
            active_deck = self.deck_manager.get_active_deck()
            is_valid = True
            if active_deck:
                is_valid = self.scryfall_client.validate_color_identity(card_name, active_deck.color_identity)
            
            return f"Card found: {card_name}", art_path, summary, colors_str, is_valid
        else:
            return f"Card not found: {card_name}", None, "", "", False
    
    def update_confirmation_ui(self, search_result: str, art_path: Optional[str], summary: str, colors_str: str, is_valid: bool) -> Tuple[bool, str, Optional[str], str, str]:
        """Update the confirmation UI based on search results."""
        show_confirmation = "Card found" in search_result
        
        if show_confirmation:
            status_text = f"{search_result}\nColors: {colors_str}\nValid for deck: {'Yes' if is_valid else 'No'}"
        else:
            status_text = search_result
        
        return show_confirmation, status_text, art_path, summary, colors_str
    
    def confirm_add_card(self, card_name: str, reason: str = "", notes: str = "") -> Tuple[str, List[Dict], str]:
        """Confirm and add a card to the current deck."""
        active_deck = self.deck_manager.get_active_deck()
        if not active_deck:
            return "No active deck selected.", [], self.get_status_info()
        
        # Validate color identity
        if not self.scryfall_client.validate_color_identity(card_name, active_deck.color_identity):
            return f"Card '{card_name}' has colors not allowed in this deck.", self._get_deck_list(), self.get_status_info()
        
        # Check if card already exists
        for card in active_deck.cards:
            if card.name.lower() == card_name.lower():
                return f"Card '{card_name}' is already in the deck.", self._get_deck_list(), self.get_status_info()
        
        # Add card
        if active_deck.add_card(card_name, reason, notes):
            self.deck_manager.save_deck()
            if self.context_manager:
                self.context_manager.update_deck_state(active_deck)
                self.context_manager.add_lookup_index(card_name, 'added')
            
            # Download medium art for display
            self.scryfall_client.get_card_medium_art_path(card_name)
            
            return f"Added '{card_name}' to deck.", self._get_deck_list(), self.get_status_info()
        else:
            return "Failed to add card (deck may be full).", self._get_deck_list(), self.get_status_info()
    
    def add_card_to_deck(self, card_name: str, reason: str = "", notes: str = "") -> Tuple[str, List[Dict], str]:
        """Add a card to the current deck."""
        active_deck = self.deck_manager.get_active_deck()
        if not active_deck:
            return "No active deck selected.", [], self.get_status_info()
        
        # Validate color identity
        if not self.scryfall_client.validate_color_identity(card_name, active_deck.color_identity):
            return f"Card '{card_name}' has colors not allowed in this deck.", self._get_deck_list(), self.get_status_info()
        
        # Check if card already exists
        for card in active_deck.cards:
            if card.name.lower() == card_name.lower():
                return f"Card '{card_name}' is already in the deck.", self._get_deck_list(), self.get_status_info()
        
        # Add card
        if active_deck.add_card(card_name, reason, notes):
            self.deck_manager.save_deck()
            if self.context_manager:
                self.context_manager.update_deck_state(active_deck)
                self.context_manager.add_lookup_index(card_name, 'added')
            
            # Download medium art for display
            self.scryfall_client.get_card_medium_art_path(card_name)
            
            return f"Added '{card_name}' to deck.", self._get_deck_list(), self.get_status_info()
        else:
            return "Failed to add card (deck may be full).", self._get_deck_list(), self.get_status_info()
    
    def remove_card_from_deck(self, card_name: str) -> Tuple[str, List[Dict], str]:
        """Remove a card from the current deck."""
        active_deck = self.deck_manager.get_active_deck()
        if not active_deck:
            return "No active deck selected.", [], self.get_status_info()
        
        if active_deck.remove_card(card_name):
            self.deck_manager.save_deck()
            if self.context_manager:
                self.context_manager.update_deck_state(active_deck)
            return f"Removed '{card_name}' from deck.", self._get_deck_list(), self.get_status_info()
        else:
            return f"Card '{card_name}' not found in deck.", self._get_deck_list(), self.get_status_info()
    
    def cut_card_from_deck(self, card_name: str, reason: str) -> Tuple[str, List[Dict], str]:
        """Cut a card from the deck and add to rejected list."""
        active_deck = self.deck_manager.get_active_deck()
        if not active_deck:
            return "No active deck selected.", [], self.get_status_info()
        
        if active_deck.cut_card(card_name, reason):
            self.deck_manager.save_deck()
            if self.context_manager:
                self.context_manager.update_deck_state(active_deck)
                self.context_manager.add_rejected_card(card_name, reason)
            return f"Cut '{card_name}' from deck: {reason}", self._get_deck_list(), self.get_status_info()
        else:
            return f"Failed to cut '{card_name}' from deck.", self._get_deck_list(), self.get_status_info()
    
    def update_deck_config(self, strategy: str, max_power: str, budget: str, banned_patterns: str, social_contract: str) -> Tuple[str, str]:
        """Update deck configuration."""
        active_deck = self.deck_manager.get_active_deck()
        if not active_deck:
            return "No active deck selected.", self.get_status_info()
        
        try:
            # Update strategy
            if strategy:
                active_deck.update_strategy(DeckStrategy(strategy))
            
            # Update constraints
            constraints = active_deck.constraints
            if max_power:
                constraints.max_power_level = int(max_power)
            if budget:
                constraints.budget_limit = float(budget)
            if banned_patterns:
                constraints.banned_patterns = [p.strip() for p in banned_patterns.split(',') if p.strip()]
            if social_contract:
                constraints.social_contract = [s.strip() for s in social_contract.split(',') if s.strip()]
            
            active_deck.update_constraints(constraints)
            self.deck_manager.save_deck()
            
            if self.context_manager:
                self.context_manager.update_deck_state(active_deck)
            
            return "Deck configuration updated.", self.get_status_info()
            
        except Exception as e:
            return f"Error updating configuration: {str(e)}", self.get_status_info()
    
    def update_design_notes(self, vibe: str, goals: str, weakspots: str, inspiration: str, target_meta: str) -> Tuple[str, str]:
        """Update design notes."""
        active_deck = self.deck_manager.get_active_deck()
        if not active_deck:
            return "No active deck selected.", self.get_status_info()
        
        try:
            design_notes = active_deck.design_notes
            design_notes.vibe = vibe
            design_notes.goals = [g.strip() for g in goals.split(',') if g.strip()]
            design_notes.known_weakspots = [w.strip() for w in weakspots.split(',') if w.strip()]
            design_notes.inspiration = inspiration
            design_notes.target_meta = target_meta
            
            active_deck.update_design_notes(design_notes)
            self.deck_manager.save_deck()
            
            if self.context_manager:
                self.context_manager.update_deck_state(active_deck)
            
            return "Design notes updated.", self.get_status_info()
            
        except Exception as e:
            return f"Error updating design notes: {str(e)}", self.get_status_info()
    
    def lookup_card(self, card_name: str) -> Tuple[str, str, Optional[str]]:
        """Look up a card using Scryfall."""
        if not card_name.strip():
            return "Please enter a card name.", "", None
        
        card_data = self.scryfall_client.search_card(card_name)
        if card_data:
            summary = self.scryfall_client.get_card_summary(card_data)
            art_path = self.scryfall_client.get_card_art_path(card_name, "normal")
            
            if self.context_manager:
                self.context_manager.add_lookup_index(card_name, 'looked_up')
            
            # Check if this is a commander and prompt to create deck
            is_commander = self._is_commander_card(card_data)
            if is_commander:
                summary += "\n\n⚠️ This appears to be a Commander! Would you like to create a new deck with this commander?"
            
            return f"Card found: {card_name}", summary, art_path
        else:
            return f"Card not found: {card_name}", "", None
    
    def _is_commander_card(self, card_data: 'CardData') -> bool:
        """Check if a card is a commander."""
        # Check type line for "Legendary Creature" or "Legendary Planeswalker"
        type_line = card_data.type_line.lower()
        is_legendary = "legendary" in type_line
        
        # Check if it's a creature or planeswalker
        is_creature_or_planeswalker = ("creature" in type_line or "planeswalker" in type_line)
        
        # Additional check for partner commanders
        has_partner = "partner" in card_data.oracle_text.lower() if card_data.oracle_text else False
        
        return is_legendary and is_creature_or_planeswalker or has_partner
    
    def create_deck_from_commander(self, commander_name: str) -> Tuple[str, str, List[Dict]]:
        """Create a new deck using the commander's colors."""
        if not commander_name.strip():
            return "Please enter a commander name.", self.get_status_info(), []
        
        card_data = self.scryfall_client.search_card(commander_name)
        if not card_data:
            return f"Commander not found: {commander_name}", self.get_status_info(), []
        
        # Extract colors from card data
        colors = [Color(c) for c in card_data.colors]
        
        # Create the deck
        try:
            deck_id = self.deck_manager.create_new_deck(commander_name, set(colors))
            
            # Initialize context manager
            deck_state = self.deck_manager.get_active_deck()
            self.context_manager = DeckbuilderContextManager(deck_state, self.scryfall_client)
            
            return f"Created new deck with commander: {commander_name}", self.get_status_info(), self._get_deck_list()
            
        except Exception as e:
            logger.error(f"Error creating deck from commander: {e}")
            return f"Error creating deck: {str(e)}", self.get_status_info(), []
    
    def get_ai_response(self, user_input: str) -> Tuple[str, str]:
        """Get AI response for deckbuilding collaboration."""
        if not self.is_connected:
            return "Error: Not connected to LM Studio.", self.get_status_info()
        
        active_deck = self.deck_manager.get_active_deck()
        if not active_deck:
            return "Please create or select a deck first.", self.get_status_info()
        
        if not user_input.strip():
            return "Please enter a message.", self.get_status_info()
        
        try:
            # Add user message to context
            if self.context_manager:
                self.context_manager.add_chat_message("user", user_input)

                # Pull bounded STM personalization signals (if any)
                personalization_signals = None
                active_session = self.deck_manager.get_active_session()
                if active_session:
                    personalization_signals = active_session.get_preferences()
                
                # Get context for API call
                context_messages = self.context_manager.get_context_for_api(
                    personalization_signals=personalization_signals
                )
                
                # Generate response
                response_chunks = []
                for chunk in self.lm_client.chat_completion(
                    messages=context_messages,
                    model="gpt-oss-20b",
                    max_tokens=1500,
                    temperature=0.7,
                    stream=False
                ):
                    response_chunks.append(chunk)
                
                response = "".join(response_chunks)
                
                # Add assistant response to context
                self.context_manager.add_chat_message("assistant", response)
                
                # Check if context needs rebuilding
                if self.context_manager.chat_rebuild_needed:
                    self.context_manager.rebuild_chat_context(self.lm_client)
                
                return response, self.get_status_info()
            else:
                return "Context manager not initialized.", self.get_status_info()
                
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return f"Error generating response: {str(e)}", self.get_status_info()
    
    def clear_chat(self) -> Tuple[List[Dict], str]:
        """Clear chat history."""
        if self.context_manager:
            self.context_manager.clear_chat()
        return [], self.get_status_info()
    
    def export_deck(self) -> str:
        """Export current deck as JSON."""
        active_deck = self.deck_manager.get_active_deck()
        if not active_deck:
            return "No active deck to export."
        
        export_data = {
            "export_date": datetime.now().isoformat(),
            "deck": active_deck.to_dict(),
            "scryfall_stats": self.scryfall_client.get_stats()
        }
        
        return json.dumps(export_data, indent=2, default=str)
    
    def _get_deck_list(self) -> List[Dict]:
        """Get current deck list for display."""
        active_deck = self.deck_manager.get_active_deck()
        if not active_deck:
            return []
        
        deck_list = []
        for card in active_deck.cards:
            deck_list.append({
                'name': card.name,
                'reason': card.reason,
                'notes': card.notes,
                'timestamp': card.timestamp.strftime('%Y-%m-%d %H:%M')
            })
        
        return deck_list
    
    def _get_rejected_list(self) -> List[Dict]:
        """Get rejected cards list for display."""
        active_deck = self.deck_manager.get_active_deck()
        if not active_deck:
            return []
        
        rejected_list = []
        for card in active_deck.rejected_cards:
            rejected_list.append({
                'name': card.name,
                'reason': card.reason,
                'timestamp': card.timestamp.strftime('%Y-%m-%d %H:%M')
            })
        
        return rejected_list
    
    def create_interface(self):
        """Create the Gradio interface."""
        has_active_deck = self.deck_manager.get_active_deck() is not None

        with gr.Blocks(title="MTG Commander Deckbuilder") as demo:
            gr.Markdown("""
            # 🃏 MTG Commander Deckbuilder
            A design-time collaboration tool between human and model for Commander deck construction.
            """)

            status_display = gr.Textbox(label="Status", value=self.get_status_info(), interactive=False)
            breadcrumb_display = gr.Textbox(label="Location", value=self.get_breadcrumb(), interactive=False)

            with gr.Tabs(selected="home") as main_tabs:
                with gr.Tab("Home", id="home"):
                    gr.Markdown("## Start Screen")
                    with gr.Row():
                        home_load_btn = gr.Button("Load Existing Deck", variant="primary")
                        home_search_btn = gr.Button("Search Scryfall", variant="primary")

                    with gr.Column(visible=False) as home_load_panel:
                        home_deck_table = gr.Dataframe(
                            label="Deck List",
                            value=self._get_home_deck_rows(),
                            headers=["Commander", "Colors", "Strategy", "Card Count", "Last Modified"],
                            datatype=["str", "str", "str", "number", "str"],
                            interactive=False
                        )
                        deck_selector = gr.Dropdown(
                            label="Select Deck",
                            choices=self._get_deck_choices(),
                            value=self.deck_manager.active_deck_id
                        )
                        with gr.Row():
                            refresh_home_btn = gr.Button("Refresh List")
                            open_deck_btn = gr.Button("Open Deck", variant="primary")
                            delete_deck_btn = gr.Button("Delete Deck", variant="secondary")
                        open_workspace_btn_home = gr.Button("Open Workspace")
                        home_action_output = gr.Textbox(label="Home Result")

                with gr.Tab("Search Scryfall", id="scryfall"):
                    with gr.Row():
                        with gr.Column():
                            lookup_home_input = gr.Textbox(label="Card Name", placeholder="Search card by name...")
                            lookup_home_btn = gr.Button("Search", variant="primary")
                            lookup_status = gr.Textbox(label="Search Status")
                            lookup_hidden_commander = gr.Textbox(visible=False)
                            with gr.Row():
                                create_from_lookup_btn = gr.Button("Create New Deck from this Commander", visible=False, variant="primary")
                                research_only_btn = gr.Button("Just Research This Card", visible=False, variant="secondary")
                            back_to_home_search_btn = gr.Button("Back to Home")
                            lookup_action_output = gr.Textbox(label="Action Result")
                        with gr.Column():
                            lookup_home_art = gr.Image(label="Card Art", type="filepath", interactive=False)
                            lookup_home_details = gr.Textbox(label="Card Details", lines=12)

                with gr.Tab("Workspace", id="workspace"):
                    with gr.Row():
                        back_to_home_workspace_btn = gr.Button("Back to Home")
                        open_search_from_workspace_btn = gr.Button("Search Scryfall")

                    with gr.Column(visible=not has_active_deck) as workspace_empty:
                        gr.Markdown("### Load or create a deck first.")

                    with gr.Column(visible=has_active_deck) as workspace_content:
                        with gr.Tabs():
                            with gr.Tab("Card Management"):
                                with gr.Row():
                                    with gr.Column():
                                        add_card_name = gr.Textbox(label="Card Name")
                                        add_card_reason = gr.Textbox(label="Why this card?")
                                        add_card_notes = gr.Textbox(label="Notes")
                                        add_card_btn = gr.Button("Add Card", variant="primary")
                                        add_card_output = gr.Textbox(label="Add Result")
                                    with gr.Column():
                                        remove_card_name = gr.Textbox(label="Card Name to Remove")
                                        cut_reason = gr.Textbox(label="Cut Reason")
                                        with gr.Row():
                                            remove_btn = gr.Button("Remove Card")
                                            cut_btn = gr.Button("Cut Card", variant="secondary")
                                        remove_output = gr.Textbox(label="Remove/Cut Result")
                                with gr.Row():
                                    deck_display = gr.Dataframe(
                                        label="Deck Cards (99)",
                                        value=self._get_deck_list(),
                                        headers=["Name", "Reason", "Notes", "Added"],
                                        datatype=["str", "str", "str", "str"]
                                    )
                                    rejected_display = gr.Dataframe(
                                        label="Rejected Cards",
                                        value=self._get_rejected_list(),
                                        headers=["Name", "Reason", "Cut Date"],
                                        datatype=["str", "str", "str"]
                                    )

                            with gr.Tab("AI Collaboration"):
                                chat_output = gr.Textbox(label="AI Response", lines=10)
                                msg = gr.Textbox(label="Your message", lines=3)
                                with gr.Row():
                                    submit_btn = gr.Button("Send", variant="primary")
                                    clear_chat_output_btn = gr.Button("Clear Output", variant="secondary")

                            with gr.Tab("Deck Configuration"):
                                strategy_dropdown = gr.Dropdown(label="Strategy", choices=[s.value for s in DeckStrategy], value="other")
                                max_power_input = gr.Number(label="Max Power Level (1-10)", value=5)
                                budget_input = gr.Number(label="Budget Limit (USD)", value=0)
                                banned_patterns_input = gr.Textbox(label="Banned Patterns")
                                social_contract_input = gr.Textbox(label="Social Contract")
                                config_update_btn = gr.Button("Update Configuration")
                                config_output = gr.Textbox(label="Configuration Result")

                                vibe_input = gr.Textbox(label="Vibe")
                                goals_input = gr.Textbox(label="Design Goals")
                                weakspots_input = gr.Textbox(label="Known Weakspots")
                                inspiration_input = gr.Textbox(label="Inspiration")
                                target_meta_input = gr.Textbox(label="Target Meta")
                                notes_update_btn = gr.Button("Update Design Notes")
                                notes_output = gr.Textbox(label="Notes Result")

                            with gr.Tab("Export"):
                                export_btn = gr.Button("Export Deck", variant="primary")
                                export_output = gr.Textbox(label="Exported Deck (JSON)", lines=15, visible=False)

            home_load_btn.click(fn=lambda: gr.update(visible=True), outputs=[home_load_panel])
            home_search_btn.click(fn=lambda: gr.update(selected="scryfall"), outputs=[main_tabs])
            open_workspace_btn_home.click(fn=lambda: gr.update(selected="workspace"), outputs=[main_tabs])
            back_to_home_search_btn.click(fn=lambda: gr.update(selected="home"), outputs=[main_tabs])
            back_to_home_workspace_btn.click(fn=lambda: gr.update(selected="home"), outputs=[main_tabs])
            open_search_from_workspace_btn.click(fn=lambda: gr.update(selected="scryfall"), outputs=[main_tabs])

            refresh_home_btn.click(fn=self.refresh_home_decks, outputs=[home_deck_table, deck_selector])

            open_deck_btn.click(
                fn=self.open_existing_deck,
                inputs=[deck_selector],
                outputs=[home_action_output, status_display, deck_display, rejected_display, deck_selector, home_deck_table, workspace_content, workspace_empty]
            ).then(fn=self.get_breadcrumb, outputs=[breadcrumb_display]).then(
                fn=lambda: gr.update(selected="workspace"), outputs=[main_tabs]
            )

            delete_deck_btn.click(
                fn=self.delete_existing_deck_home,
                inputs=[deck_selector],
                outputs=[home_action_output, status_display, deck_display, rejected_display, deck_selector, home_deck_table, workspace_content, workspace_empty]
            ).then(fn=self.get_breadcrumb, outputs=[breadcrumb_display])

            lookup_home_btn.click(
                fn=self.lookup_card_home,
                inputs=[lookup_home_input],
                outputs=[lookup_status, lookup_home_art, lookup_home_details, create_from_lookup_btn, research_only_btn, lookup_hidden_commander]
            )

            create_from_lookup_btn.click(
                fn=self.create_deck_from_home_lookup,
                inputs=[lookup_hidden_commander],
                outputs=[lookup_action_output, status_display, deck_display, rejected_display, deck_selector, home_deck_table, workspace_content, workspace_empty]
            ).then(fn=self.get_breadcrumb, outputs=[breadcrumb_display]).then(
                fn=lambda: gr.update(selected="workspace"), outputs=[main_tabs]
            )

            research_only_btn.click(
                fn=lambda: "Research mode: no deck created. Continue browsing Scryfall results.",
                outputs=[lookup_action_output]
            )

            add_card_btn.click(
                fn=self.add_card_to_deck,
                inputs=[add_card_name, add_card_reason, add_card_notes],
                outputs=[add_card_output, deck_display, status_display]
            ).then(fn=self.refresh_home_decks, outputs=[home_deck_table, deck_selector])

            remove_btn.click(
                fn=self.remove_card_from_deck,
                inputs=[remove_card_name],
                outputs=[remove_output, deck_display, status_display]
            ).then(fn=self.refresh_home_decks, outputs=[home_deck_table, deck_selector])

            cut_btn.click(
                fn=self.cut_card_from_deck,
                inputs=[remove_card_name, cut_reason],
                outputs=[remove_output, deck_display, status_display]
            ).then(fn=self.refresh_home_decks, outputs=[home_deck_table, deck_selector])

            msg.submit(fn=self.get_ai_response, inputs=[msg], outputs=[chat_output, status_display])
            submit_btn.click(fn=self.get_ai_response, inputs=[msg], outputs=[chat_output, status_display])
            clear_chat_output_btn.click(fn=lambda: "", outputs=[chat_output])

            config_update_btn.click(
                fn=self.update_deck_config,
                inputs=[strategy_dropdown, max_power_input, budget_input, banned_patterns_input, social_contract_input],
                outputs=[config_output, status_display]
            )

            notes_update_btn.click(
                fn=self.update_design_notes,
                inputs=[vibe_input, goals_input, weakspots_input, inspiration_input, target_meta_input],
                outputs=[notes_output, status_display]
            )

            export_btn.click(fn=self.export_deck, outputs=[export_output]).then(
                fn=lambda: gr.update(visible=True), outputs=[export_output]
            )

        return demo

def main():
    """Main entry point."""
    app = DeckbuilderApp()
    demo = app.create_interface()
    
    # Launch the app
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )

if __name__ == "__main__":
    main()