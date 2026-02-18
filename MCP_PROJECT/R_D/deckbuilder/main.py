import logging
from deckbuilder_app import DeckbuilderApp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main entry point - launches the Deckbuilder application."""
    logger.info("Starting MTG Commander Deckbuilder")
    app = DeckbuilderApp()
    demo = app.create_interface()
    
    # Launch the app
    demo.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,
        share=False,  # Set to True if you want to create a public link
        debug=True
    )

if __name__ == "__main__":
    main()
