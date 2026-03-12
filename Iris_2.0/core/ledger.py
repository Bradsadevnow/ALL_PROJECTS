import json
import time
import os
from typing import List, Optional
from core.lifecycle import EventEnvelope, EventType

class EventLedger:
    def __init__(self, file_path: str):
        self.file_path = file_path
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

    def append(self, event: EventEnvelope):
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(event.model_dump_json() + "\n")

    def read_all(self) -> List[EventEnvelope]:
        if not os.path.exists(self.file_path):
            return []
        
        events = []
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    events.append(EventEnvelope.model_validate_json(line))
        return events

    def clear(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
