"""
Test script for the Deckbuilder system.
Verifies that all components work together correctly.
"""

import logging
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deckbuilder_models import DeckManager, DeckState, DeckStrategy, Color
from personalization_policy import PersonalizationDomain
from scryfall_client import ScryfallClient
from deckbuilder_context import DeckbuilderContextManager
from lm_studio_client import LMStudioClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_deck_models():
    """Test the deck models."""
    logger.info("Testing deck models...")
    
    # Create a new deck
    deck_manager = DeckManager()
    deck_id = deck_manager.create_new_deck("Jeskai Ascendancy", {Color.BLUE, Color.WHITE, Color.RED})
    
    deck = deck_manager.get_active_deck()
    assert deck is not None, "Deck should be created"
    assert deck.commander == "Jeskai Ascendancy", "Commander should be set"
    assert len(deck.color_identity) == 3, "Should have 3 colors"
    
    # Test adding cards
    assert deck.add_card("Lightning Bolt", "Fast removal", "Classic burn spell"), "Should add card"
    assert len(deck.cards) == 1, "Should have 1 card"
    
    # Test cutting cards
    assert deck.cut_card("Lightning Bolt", "Too aggressive for this deck"), "Should cut card"
    assert len(deck.cards) == 0, "Should have 0 cards"
    assert len(deck.rejected_cards) == 1, "Should have 1 rejected card"
    
    logger.info("✓ Deck models test passed")

def test_scryfall_client():
    """Test the Scryfall client."""
    logger.info("Testing Scryfall client...")
    
    client = ScryfallClient()
    
    # Test connection
    card_data = client.search_card("Lightning Bolt")
    if card_data:
        assert card_data.name == "Lightning Bolt", "Should find Lightning Bolt"
        assert card_data.colors == ["R"], "Should have red color"
        logger.info("✓ Scryfall client test passed")
    else:
        logger.warning("⚠ Scryfall client test skipped (no internet or API issues)")

def test_context_manager():
    """Test the context manager."""
    logger.info("Testing context manager...")
    
    # Create a test deck
    deck_manager = DeckManager()
    deck_id = deck_manager.create_new_deck("Niv-Mizzet, Parun", {Color.BLUE, Color.RED})
    deck = deck_manager.get_active_deck()
    
    # Create context manager
    scryfall_client = ScryfallClient()
    context_manager = DeckbuilderContextManager(deck, scryfall_client)
    
    # Test adding chat messages
    assert context_manager.add_chat_message("user", "Hello"), "Should add user message"
    assert context_manager.add_chat_message("assistant", "Hi there"), "Should add assistant message"
    
    # Test context for API
    context = context_manager.get_context_for_api()
    assert len(context) > 0, "Should have context messages"
    
    # Test token usage
    usage = context_manager.get_token_usage_report()
    assert usage['total_tokens'] > 0, "Should have token usage"
    
    logger.info("✓ Context manager test passed")

def test_personalization_policy_stm_only():
    """Test strict STM-only personalization behavior."""
    logger.info("Testing personalization policy (STM-only)...")

    deck_manager = DeckManager()
    deck_id = deck_manager.create_new_deck("Atraxa, Praetors' Voice", {Color.WHITE, Color.BLUE, Color.BLACK, Color.GREEN})
    session = deck_manager.get_active_session()

    assert session is not None, "Active session should exist"

    # Allowed signal should be accepted
    accepted = session.add_signal(
        PersonalizationDomain.CONVERSATION,
        "verbosity_tolerance",
        "concise"
    )
    assert accepted, "Allowed conversation signal should be accepted"

    # Out-of-scope signal key should be rejected
    rejected = session.add_signal(
        PersonalizationDomain.CONVERSATION,
        "location_preference",
        "nearby"
    )
    assert not rejected, "Out-of-scope signal should be rejected"

    prefs = session.get_preferences()
    assert prefs["conversation"].get("verbosity_tolerance") == "concise", "Accepted signal should be present"
    assert "location_preference" not in prefs["conversation"], "Rejected signal should not be present"

    # Persist and reload should not carry personalization signals
    deck_manager.save_deck(deck_id)
    loaded_manager = DeckManager(data_dir=deck_manager.data_dir)
    assert loaded_manager.load_deck(deck_id), "Deck should load"

    loaded_session = loaded_manager.get_active_session()
    assert loaded_session is not None, "Loaded session should exist"
    loaded_prefs = loaded_session.get_preferences()
    assert loaded_prefs["conversation"] == {}, "Conversation personalization should not persist"
    assert loaded_prefs["tools_ir"] == {}, "Tools/IR personalization should not persist"
    assert loaded_prefs["opt_in_context_apple"] == {}, "Opt-in context personalization should not persist"

    logger.info("✓ Personalization STM-only test passed")

def test_lm_studio_client():
    """Test the LM Studio client."""
    logger.info("Testing LM Studio client...")
    
    client = LMStudioClient()
    connected = client.test_connection()
    
    if connected:
        models = client.get_models()
        logger.info(f"Available models: {models}")
        logger.info("✓ LM Studio client test passed")
    else:
        logger.warning("⚠ LM Studio client test failed (check connection)")

def test_full_integration():
    """Test full integration."""
    logger.info("Testing full integration...")
    
    try:
        from deckbuilder_app import DeckbuilderApp
        app = DeckbuilderApp()
        
        # Test status
        status = app.get_status_info()
        logger.info(f"App status: {status}")
        
        # Test creating a deck
        result, status, deck_list = app.create_new_deck("Niv-Mizzet, Parun", ["U", "R"])
        logger.info(f"Create deck result: {result}")
        
        # Test adding a card
        result, deck_list, status = app.add_card_to_deck("Lightning Bolt", "Fast removal", "Classic burn")
        logger.info(f"Add card result: {result}")
        
        logger.info("✓ Full integration test passed")
        
    except Exception as e:
        logger.error(f"Full integration test failed: {e}")
        raise

def main():
    """Run all tests."""
    logger.info("Starting Deckbuilder tests...")
    
    try:
        test_deck_models()
        test_scryfall_client()
        test_context_manager()
        test_personalization_policy_stm_only()
        test_lm_studio_client()
        test_full_integration()
        
        logger.info("🎉 All tests passed!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()