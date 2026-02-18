"""
Scryfall API client for Magic: The Gathering card data.
Provides caching and rate limiting for efficient card lookups.
"""

import requests
import json
import time
import logging
import os
import threading
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class CardData:
    """Represents a Magic card with all relevant data."""
    name: str
    mana_cost: str
    cmc: float
    colors: List[str]
    color_identity: List[str]
    type_line: str
    oracle_text: str
    power: Optional[str] = None
    toughness: Optional[str] = None
    loyalty: Optional[str] = None
    rarity: str = ""
    set_name: str = ""
    set_code: str = ""
    collector_number: str = ""
    image_uris: Dict[str, str] = None
    prices: Dict[str, Optional[str]] = None
    legalities: Dict[str, str] = None
    keywords: List[str] = None
    edhrec_rank: Optional[int] = None
    scryfall_uri: str = ""
    oracle_id: str = ""
    
    def __post_init__(self):
        if self.image_uris is None:
            self.image_uris = {}
        if self.prices is None:
            self.prices = {}
        if self.legalities is None:
            self.legalities = {}
        if self.keywords is None:
            self.keywords = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CardData':
        """Create from dictionary."""
        return cls(**data)


class ScryfallCache:
    """Thread-safe cache for Scryfall card data."""
    
    def __init__(self, cache_file: str = "scryfall_cache.json", max_age_hours: int = 24):
        self.cache_file = cache_file
        self.max_age = timedelta(hours=max_age_hours)
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()
        self.load_cache()
    
    def load_cache(self) -> None:
        """Load cache from file."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
                logger.info(f"Loaded {len(self.cache)} cards from cache")
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            self.cache = {}
    
    def save_cache(self) -> None:
        """Save cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def get(self, card_name: str) -> Optional[CardData]:
        """Get card from cache if not expired."""
        with self.lock:
            if card_name.lower() in self.cache:
                cached_data = self.cache[card_name.lower()]
                cached_time = datetime.fromisoformat(cached_data['cached_at'])
                
                if datetime.now() - cached_time < self.max_age:
                    return CardData.from_dict(cached_data['data'])
                else:
                    # Remove expired entry
                    del self.cache[card_name.lower()]
            return None
    
    def set(self, card_name: str, card_data: CardData) -> None:
        """Set card in cache."""
        with self.lock:
            self.cache[card_name.lower()] = {
                'cached_at': datetime.now().isoformat(),
                'data': card_data.to_dict()
            }
            self.save_cache()


class ScryfallClient:
    """Client for Scryfall API with caching and rate limiting."""
    
    def __init__(self, cache_file: str = "scryfall_cache.json"):
        self.base_url = "https://api.scryfall.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GPT-OSS-Deckbuilder/1.0',
            'Accept': 'application/json'
        })
        
        # Rate limiting: Scryfall allows 10 requests per second
        self.last_request_time = 0.0
        self.min_request_interval = 0.1  # 100ms between requests
        
        # Cache
        self.cache = ScryfallCache(cache_file)
        
        # Card art cache directory
        self.art_cache_dir = "card_art_cache"
        os.makedirs(self.art_cache_dir, exist_ok=True)
        
        # Statistics
        self.stats = {
            'requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'art_downloads': 0,
            'art_cache_hits': 0
        }
    
    def _rate_limit(self) -> None:
        """Enforce rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def search_card(self, query: str) -> Optional[CardData]:
        """
        Search for a card by name or query.
        Returns the first exact match or best match.
        """
        # Check cache first
        cached = self.cache.get(query)
        if cached:
            self.stats['cache_hits'] += 1
            return cached
        
        self.stats['cache_misses'] += 1
        
        try:
            self._rate_limit()
            
            # First try exact name search
            response = self.session.get(f"{self.base_url}/cards/named", params={
                'fuzzy': query,
                'exact': query
            })
            
            if response.status_code == 200:
                data = response.json()
                card_data = self._parse_card_data(data)
                self.cache.set(query, card_data)
                self.stats['requests'] += 1
                return card_data
            
            # If exact search fails, try fuzzy search
            response = self.session.get(f"{self.base_url}/cards/search", params={
                'q': f'name:"{query}"'
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    card_data = self._parse_card_data(data['data'][0])
                    self.cache.set(query, card_data)
                    self.stats['requests'] += 1
                    return card_data
            
            logger.warning(f"Card not found: {query}")
            return None
            
        except Exception as e:
            logger.error(f"Error searching for card {query}: {e}")
            return None
    
    def get_card_by_set(self, set_code: str, collector_number: str) -> Optional[CardData]:
        """Get a card by set code and collector number."""
        try:
            self._rate_limit()
            
            response = self.session.get(f"{self.base_url}/cards/{set_code}/{collector_number}")
            
            if response.status_code == 200:
                data = response.json()
                card_data = self._parse_card_data(data)
                self.cache.set(f"{set_code} {collector_number}", card_data)
                self.stats['requests'] += 1
                return card_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting card {set_code} {collector_number}: {e}")
            return None
    
    def search_multiple_cards(self, card_names: List[str]) -> Dict[str, Optional[CardData]]:
        """Search for multiple cards efficiently."""
        results = {}
        
        for name in card_names:
            results[name] = self.search_card(name)
        
        return results
    
    def _parse_card_data(self, data: Dict[str, Any]) -> CardData:
        """Parse Scryfall API response into CardData object."""
        # Handle card faces for split cards, adventures, etc.
        if 'card_faces' in data and len(data['card_faces']) > 0:
            # Use the first face for basic info, but combine oracle text
            main_face = data['card_faces'][0]
            other_face = data['card_faces'][1] if len(data['card_faces']) > 1 else None
            
            # Combine oracle text from all faces
            oracle_text = main_face.get('oracle_text', '')
            if other_face and other_face.get('oracle_text'):
                oracle_text += f"\n\n{other_face['oracle_text']}"
            
            # Combine keywords
            keywords = main_face.get('keywords', [])
            if other_face and other_face.get('keywords'):
                keywords.extend(other_face['keywords'])
            
            card_data = CardData(
                name=data.get('name', ''),
                mana_cost=data.get('mana_cost', ''),
                cmc=data.get('cmc', 0),
                colors=data.get('colors', []),
                color_identity=data.get('color_identity', []),
                type_line=data.get('type_line', ''),
                oracle_text=oracle_text,
                power=main_face.get('power'),
                toughness=main_face.get('toughness'),
                loyalty=main_face.get('loyalty'),
                rarity=data.get('rarity', ''),
                set_name=data.get('set_name', ''),
                set_code=data.get('set', ''),
                collector_number=data.get('collector_number', ''),
                image_uris=data.get('image_uris', {}),
                prices=data.get('prices', {}),
                legalities=data.get('legalities', {}),
                keywords=list(set(keywords)),  # Remove duplicates
                edhrec_rank=data.get('edhrec_rank'),
                scryfall_uri=data.get('scryfall_uri', ''),
                oracle_id=data.get('oracle_id', '')
            )
        else:
            # Regular single-faced card
            card_data = CardData(
                name=data.get('name', ''),
                mana_cost=data.get('mana_cost', ''),
                cmc=data.get('cmc', 0),
                colors=data.get('colors', []),
                color_identity=data.get('color_identity', []),
                type_line=data.get('type_line', ''),
                oracle_text=data.get('oracle_text', ''),
                power=data.get('power'),
                toughness=data.get('toughness'),
                loyalty=data.get('loyalty'),
                rarity=data.get('rarity', ''),
                set_name=data.get('set_name', ''),
                set_code=data.get('set', ''),
                collector_number=data.get('collector_number', ''),
                image_uris=data.get('image_uris', {}),
                prices=data.get('prices', {}),
                legalities=data.get('legalities', {}),
                keywords=data.get('keywords', []),
                edhrec_rank=data.get('edhrec_rank'),
                scryfall_uri=data.get('scryfall_uri', ''),
                oracle_id=data.get('oracle_id', '')
            )
        
        return card_data
    
    def validate_color_identity(self, card_name: str, allowed_colors: Set[str]) -> bool:
        """Check if a card's color identity is legal for a deck."""
        card_data = self.search_card(card_name)
        if not card_data:
            return False
        
        # Convert color identity to set for comparison
        card_colors = set(card_data.color_identity)
        allowed_colors_set = set(allowed_colors)
        
        # Card is legal if all its colors are in the allowed set
        return card_colors.issubset(allowed_colors_set)
    
    def get_color_abbreviations(self, colors: List[str]) -> str:
        """Get color abbreviations (e.g., ['W', 'U'] -> 'WU')."""
        color_map = {
            'White': 'W', 'Blue': 'U', 'Black': 'B', 'Red': 'R', 'Green': 'G',
            'W': 'W', 'U': 'U', 'B': 'B', 'R': 'R', 'G': 'G'
        }
        
        abbrevs = []
        for color in colors:
            if color in color_map:
                abbrevs.append(color_map[color])
        
        return ''.join(sorted(abbrevs))
    
    def get_card_summary(self, card_data: CardData) -> str:
        """Get a concise summary of a card for display."""
        parts = []
        
        # Name and mana cost
        parts.append(f"**{card_data.name}**")
        if card_data.mana_cost:
            parts.append(f"({card_data.mana_cost})")
        
        # Type line
        if card_data.type_line:
            parts.append(f"- {card_data.type_line}")
        
        # Power/Toughness or Loyalty
        if card_data.power and card_data.toughness:
            parts.append(f"- {card_data.power}/{card_data.toughness}")
        elif card_data.loyalty:
            parts.append(f"- Loyalty: {card_data.loyalty}")
        
        # Key abilities (first sentence of oracle text)
        if card_data.oracle_text:
            first_sentence = card_data.oracle_text.split('.')[0] + '.'
            if len(first_sentence) > 100:
                first_sentence = first_sentence[:97] + "..."
            parts.append(f"- {first_sentence}")
        
        return ' '.join(parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            'total_requests': self.stats['requests'],
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'cache_hit_rate': self.stats['cache_hits'] / max(1, self.stats['cache_hits'] + self.stats['cache_misses'])
        }
    
    def clear_cache(self) -> None:
        """Clear the cache."""
        with self.cache.lock:
            self.cache.cache.clear()
            self.cache.save_cache()
        logger.info("Cache cleared")
    
    def _get_art_cache_path(self, card_name: str, image_url: str) -> str:
        """Get the cache path for a card art image."""
        # Create a hash of the image URL to ensure unique filenames
        url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
        safe_name = "".join(c for c in card_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')[:50]  # Limit filename length
        return os.path.join(self.art_cache_dir, f"{safe_name}_{url_hash}.jpg")
    
    def download_card_art(self, card_data: CardData, size: str = "normal") -> Optional[str]:
        """
        Download card art and return local file path.
        Returns None if no art available or download fails.
        """
        if not card_data.image_uris or size not in card_data.image_uris:
            return None
        
        image_url = card_data.image_uris[size]
        cache_path = self._get_art_cache_path(card_data.name, image_url)
        
        # Check if already cached
        if os.path.exists(cache_path):
            self.stats['art_cache_hits'] += 1
            return cache_path
        
        try:
            self._rate_limit()
            
            # Download the image
            response = self.session.get(image_url, stream=True, timeout=10)
            if response.status_code == 200:
                with open(cache_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                self.stats['art_downloads'] += 1
                logger.info(f"Downloaded art for {card_data.name} to {cache_path}")
                return cache_path
            else:
                logger.warning(f"Failed to download art for {card_data.name}: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading art for {card_data.name}: {e}")
            return None
    
    def get_card_art_path(self, card_name: str, size: str = "normal") -> Optional[str]:
        """Get local path to card art, downloading if necessary."""
        card_data = self.search_card(card_name)
        if not card_data:
            return None
        
        return self.download_card_art(card_data, size)
    
    def get_card_medium_art_path(self, card_name: str) -> Optional[str]:
        """Get local path to medium-sized card art, downloading if necessary."""
        return self.get_card_art_path(card_name, "normal")
    
    def get_art_stats(self) -> Dict[str, Any]:
        """Get art download statistics."""
        total_art_files = len([f for f in os.listdir(self.art_cache_dir) if f.endswith('.jpg')])
        return {
            'art_downloads': self.stats['art_downloads'],
            'art_cache_hits': self.stats['art_cache_hits'],
            'total_cached_art': total_art_files,
            'cache_directory': self.art_cache_dir
        }
