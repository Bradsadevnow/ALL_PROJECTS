from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class TurnRecord:
    ts_utc: str
    session_id: str
    turn_number: int
    user_input: str
    final_output: str
    think: str = ""
    tools: Optional[Any] = None
    memory_candidates: Optional[Any] = None
    state_before: Optional[Dict[str, Any]] = None
    state_after: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ts_utc": self.ts_utc,
            "session_id": self.session_id,
            "turn_number": self.turn_number,
            "user_input": self.user_input,
            "final_output": self.final_output,
            "think": self.think,
            "tools": self.tools,
            "memory_candidates": self.memory_candidates,
            "state_before": self.state_before,
            "state_after": self.state_after,
        }


class JsonlLogger:
    def __init__(self, path: str) -> None:
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def append(self, record: Dict[str, Any]) -> None:
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
