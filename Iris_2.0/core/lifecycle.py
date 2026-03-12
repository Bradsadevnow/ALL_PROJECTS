import enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class EpochLifecycleState(str, enum.Enum):
    IDLE = "IDLE"
    EPOCH_OPEN = "EPOCH_OPEN"
    EPOCH_EXECUTING = "EPOCH_EXECUTING"
    EPOCH_COMMITTED = "EPOCH_COMMITTED"
    EPOCH_ABORTED = "EPOCH_ABORTED"

class EmotiveState(BaseModel):
    curiosity: float = 0.5  # Cognition FB
    determination: float = 0.5  # Transaction FB
    frustration: float = 0.1  # Entropy Sensor
    calmness: float = 0.9  # Language FB

class IrisInternalVoice(BaseModel):
    thought: str
    emotive_state: EmotiveState
    final_response: str

class EventType(str, enum.Enum):
    EPOCH_STARTED = "EpochStarted"
    TOOL_FINISHED = "ToolFinished"
    EPOCH_COMMITTED = "EpochCommitted"
    EPOCH_ABORTED = "EpochAborted"

class EventEnvelope(BaseModel):
    event_type: EventType
    epoch_id: str
    timestamp: float
    payload: Dict[str, Any]
