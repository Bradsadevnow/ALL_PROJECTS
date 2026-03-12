import sqlite3
import os
from typing import List, Dict, Any

class MediumTermMemory:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mtm_resonances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    epoch_id TEXT,
                    thought TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Index for faster keyword search (though we'll use LIKE for simplicity)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_thought ON mtm_resonances(thought)")

    def add_thought(self, epoch_id: str, thought: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO mtm_resonances (epoch_id, thought) VALUES (?, ?)",
                (epoch_id, thought)
            )

    def search_resonances(self, query: str, limit: int = 3) -> List[str]:
        """Search for keyword matches in past thoughts."""
        # Simple keyword matching for "Subconscious Resonance"
        keywords = query.split()
        if not keywords:
            return []
            
        # Build a simple LIKE query
        where_clause = " OR ".join(["thought LIKE ?" for _ in keywords])
        params = [f"%{kw}%" for kw in keywords]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                f"SELECT thought FROM mtm_resonances WHERE {where_clause} ORDER BY timestamp DESC LIMIT ?",
                (*params, limit)
            )
            return [row[0] for row in cursor.fetchall()]
