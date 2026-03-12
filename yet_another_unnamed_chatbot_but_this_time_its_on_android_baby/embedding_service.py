import logging
from google import genai
from typing import Optional

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self._embedding_cache = {}

    def embed(self, text: str, cache_key: Optional[str] = None) -> list[float]:
        """Generates an embedding for the given text."""
        if cache_key and cache_key in self._embedding_cache:
            return self._embedding_cache[cache_key]
            
        try:
            # Using recommended embedding model for Gemini
            result = self.client.models.embed_content(
                model="models/gemini-embedding-001",
                contents=text
            )
            embedding = result.embeddings[0].values
            
            if cache_key:
                self._embedding_cache[cache_key] = embedding
            return embedding
        except Exception as e:
            try:
                # Fallback to the old standard model if the experimental one fails
                result = self.client.models.embed_content(
                    model="models/embedding-001",
                    contents=text
                )
                embedding = result.embeddings[0].values
                
                if cache_key:
                    self._embedding_cache[cache_key] = embedding
                return embedding
            except Exception as inner_e:
                logger.error(f"Embedding request failed: {inner_e}")
                raise

    def clear_cache(self):
        """Clears the embedding cache."""
        self._embedding_cache.clear()
