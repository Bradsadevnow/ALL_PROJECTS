from typing import List, Dict, Any

class TokenTracker:
    def __init__(self, trigger_threshold: int = 240000, hard_cap: int = 250000):
        self.trigger_threshold = trigger_threshold
        self.hard_cap = hard_cap
        self.total_usage = 0

    def add_usage(self, tokens: int):
        self.total_usage += tokens

    def is_threshold_reached(self) -> bool:
        return self.total_usage >= self.trigger_threshold

    def is_hard_cap_exceeded(self) -> bool:
        return self.total_usage >= self.hard_cap

    def get_usage_report(self) -> Dict[str, Any]:
        return {
            "total_usage": self.total_usage,
            "threshold": self.trigger_threshold,
            "hard_cap": self.hard_cap,
            "remaining": max(0, self.hard_cap - self.total_usage)
        }

    def estimate_tokens(self, text: str) -> int:
        """Rough estimation: 1 token ~= 4 characters."""
        return len(text) // 4
