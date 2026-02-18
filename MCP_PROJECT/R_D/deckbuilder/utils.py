import json
import os
from typing import Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def save_chat_history(context_manager, filename: str = None) -> str:
    """Save chat history to a JSON file."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_history_{timestamp}.json"
    
    try:
        history_data = {
            "saved_at": datetime.now().isoformat(),
            "total_tokens": context_manager.get_total_tokens(),
            "messages": context_manager.get_message_history()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, indent=2, default=str)
        
        logger.info(f"Chat history saved to {filename}")
        return filename
    
    except Exception as e:
        logger.error(f"Error saving chat history: {e}")
        return ""

def load_chat_history(context_manager, filename: str) -> bool:
    """Load chat history from a JSON file."""
    try:
        if not os.path.exists(filename):
            logger.error(f"File {filename} does not exist")
            return False
        
        with open(filename, 'r', encoding='utf-8') as f:
            history_data = json.load(f)
        
        # Rebuild context from history
        context_manager.rebuild_context_from_history(history_data.get("messages", []))
        
        logger.info(f"Chat history loaded from {filename}")
        return True
    
    except Exception as e:
        logger.error(f"Error loading chat history: {e}")
        return False

def format_token_count(tokens: int) -> str:
    """Format token count with commas and context."""
    return f"{tokens:,} tokens"

def get_connection_status_text(is_connected: bool) -> str:
    """Get formatted connection status text."""
    if is_connected:
        return "🟢 Connected to LM Studio"
    else:
        return "🔴 Not connected to LM Studio"

def validate_lm_studio_url(url: str) -> bool:
    """Validate that the LM Studio URL is properly formatted."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False

def create_default_config() -> Dict[str, Any]:
    """Create default configuration for the application."""
    return {
        "lm_studio_url": "http://192.168.1.128:1234",
        "max_tokens": 40000,
        "collapse_threshold": 0.8,
        "target_tokens_after_collapse": 24000,
        "default_temperature": 0.7,
        "default_max_response_tokens": 2000,
        "auto_collapse": True
    }

def load_config(config_file: str = "config.json") -> Dict[str, Any]:
    """Load configuration from file or create default config."""
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_file}")
            return config
        else:
            config = create_default_config()
            save_config(config, config_file)
            logger.info(f"Default configuration created and saved to {config_file}")
            return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return create_default_config()

def save_config(config: Dict[str, Any], config_file: str = "config.json") -> bool:
    """Save configuration to file."""
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Configuration saved to {config_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False

def estimate_tokens_from_chars(text: str) -> int:
    """Estimate token count from character count (rough approximation)."""
    # Rough estimate: 4 characters per token
    return max(1, len(text) // 4)

def format_time_ago(timestamp: datetime) -> str:
    """Format a timestamp as 'time ago' text."""
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days} day(s) ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600} hour(s) ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60} minute(s) ago"
    else:
        return "just now"