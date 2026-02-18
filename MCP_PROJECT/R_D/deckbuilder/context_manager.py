import tiktoken
from typing import List, Dict, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class Message:
    """Represents a chat message."""
    role: str
    content: str
    timestamp: datetime
    token_count: int = 0

class ContextManager:
    """Manages conversation context with token counting and collapse functionality."""
    
    def __init__(self, max_tokens: int = 40000, collapse_threshold: float = 0.8):
        """
        Initialize the context manager.
        
        Args:
            max_tokens: Maximum token limit for context window
            collapse_threshold: When to trigger collapse (e.g., 0.8 = 80% of max)
        """
        self.max_tokens = max_tokens
        self.collapse_threshold = collapse_threshold
        self.target_tokens = int(max_tokens * 0.6)  # Target to reduce to after collapse
        self.messages: List[Message] = []
        self.tokenizer = tiktoken.get_encoding("cl100k_base")  # Common encoding for most models
        
        # System message for context summarization
        self.summarization_prompt = """Please provide a concise summary of the following conversation, focusing on:
1. Key topics discussed
2. Important decisions or conclusions
3. User's main questions and concerns
4. Any specific instructions or preferences mentioned

Keep the summary under 500 words and maintain the essential context needed to continue the conversation meaningfully.

Conversation:
"""
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        try:
            return len(self.tokenizer.encode(text))
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Fallback estimation: ~4 chars per token
            return max(1, len(text) // 4)
    
    def add_message(self, role: str, content: str) -> int:
        """Add a message and return its token count."""
        token_count = self.count_tokens(content)
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now(),
            token_count=token_count
        )
        self.messages.append(message)
        return token_count
    
    def get_total_tokens(self) -> int:
        """Get total token count of all messages."""
        return sum(msg.token_count for msg in self.messages)
    
    def should_collapse(self) -> bool:
        """Check if context should be collapsed."""
        total_tokens = self.get_total_tokens()
        return total_tokens > (self.max_tokens * self.collapse_threshold)
    
    def get_context_for_api(self) -> List[Dict[str, str]]:
        """Get messages formatted for API calls."""
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]
    
    def collapse_context(self, lm_client) -> bool:
        """
        Collapse context by summarizing old messages.
        
        Args:
            lm_client: LM Studio client for generating summaries
            
        Returns:
            bool: True if collapse was successful
        """
        if not self.should_collapse():
            return True
        
        logger.info(f"Collapsing context: {self.get_total_tokens()} tokens > {self.max_tokens * self.collapse_threshold}")
        
        # Find the point where we need to start summarizing
        current_tokens = 0
        collapse_point = 0
        
        # Work backwards from the end to find where to start summarizing
        for i in range(len(self.messages) - 1, -1, -1):
            current_tokens += self.messages[i].token_count
            if current_tokens > self.target_tokens:
                collapse_point = i + 1
                break
        
        if collapse_point == 0:
            # Too much context, keep only the most recent messages
            collapse_point = len(self.messages) // 2
        
        # Extract messages to summarize
        messages_to_summarize = self.messages[:collapse_point]
        remaining_messages = self.messages[collapse_point:]
        
        # Build conversation text for summarization
        conversation_text = ""
        for msg in messages_to_summarize:
            conversation_text += f"{msg.role.upper()}: {msg.content}\n\n"
        
        # Create summarization prompt
        summarization_messages = [
            {"role": "system", "content": self.summarization_prompt},
            {"role": "user", "content": conversation_text}
        ]
        
        try:
            # Generate summary
            summary_chunks = []
            for chunk in lm_client.chat_completion(
                messages=summarization_messages,
                model="gpt-oss-20b",
                max_tokens=1000,
                temperature=0.3,
                stream=False
            ):
                summary_chunks.append(chunk)
            
            summary = "".join(summary_chunks)
            
            # Create new system message with summary
            summary_message = Message(
                role="system",
                content=f"Conversation Summary (up to this point):\n\n{summary}",
                timestamp=datetime.now(),
                token_count=self.count_tokens(summary)
            )
            
            # Replace old messages with summary
            self.messages = [summary_message] + remaining_messages
            
            logger.info(f"Context collapsed successfully. New token count: {self.get_total_tokens()}")
            return True
            
        except Exception as e:
            logger.error(f"Error during context collapse: {e}")
            return False
    
    def clear_context(self):
        """Clear all messages from context."""
        self.messages.clear()
        logger.info("Context cleared")
    
    def get_message_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get message history for display."""
        messages = self.messages
        if limit:
            messages = messages[-limit:]
        
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "token_count": msg.token_count
            }
            for msg in messages
        ]
    
    def rebuild_context_from_history(self, history: List[Dict[str, Any]]):
        """Rebuild context from saved history."""
        self.messages.clear()
        for msg_data in history:
            message = Message(
                role=msg_data["role"],
                content=msg_data["content"],
                timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                token_count=msg_data.get("token_count", 0)
            )
            self.messages.append(message)