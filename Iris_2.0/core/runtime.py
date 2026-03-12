import asyncio
import uuid
import time
from typing import Optional
from core.lifecycle import EpochLifecycleState, EventEnvelope, EventType
from core.ledger import EventLedger

class Epoch:
    def __init__(self, epoch_id: Optional[str] = None):
        self.epoch_id = epoch_id or str(uuid.uuid4())
        self.state = EpochLifecycleState.IDLE
        self.start_time = time.time()
        self.events = []

    def open(self):
        self.state = EpochLifecycleState.EPOCH_OPEN

    def execute(self):
        self.state = EpochLifecycleState.EPOCH_EXECUTING

    def commit(self):
        self.state = EpochLifecycleState.EPOCH_COMMITTED

    def abort(self):
        self.state = EpochLifecycleState.EPOCH_ABORTED

class IrisRuntime:
    def __init__(self, ledger_path: str):
        self.ledger = EventLedger(ledger_path)
        self._epoch_lock = asyncio.Lock()
        self.current_epoch: Optional[Epoch] = None
        self.lifecycle_state = EpochLifecycleState.IDLE
        self.stm = [] # Short-Term Memory (committed messages)

    async def start_epoch(self) -> Epoch:
        if self._epoch_lock.locked():
            raise RuntimeError("Runtime locked: An epoch is already in progress.")
        
        await self._epoch_lock.acquire()
        self.current_epoch = Epoch()
        self.current_epoch.open()
        self.lifecycle_state = EpochLifecycleState.EPOCH_OPEN
        
        # Log start
        self.ledger.append(EventEnvelope(
            event_type=EventType.EPOCH_STARTED,
            epoch_id=self.current_epoch.epoch_id,
            timestamp=time.time(),
            payload={"message": "Epoch started"}
        ))
        
        return self.current_epoch

    async def commit_epoch(self, payload: dict):
        if not self.current_epoch:
            return
        
        self.current_epoch.commit()
        self.lifecycle_state = EpochLifecycleState.IDLE
        
        self.ledger.append(EventEnvelope(
            event_type=EventType.EPOCH_COMMITTED,
            epoch_id=self.current_epoch.epoch_id,
            timestamp=time.time(),
            payload=payload
        ))
        
        self.stm.append(payload)
        self.current_epoch = None
        self._epoch_lock.release()

    async def abort_epoch(self, reason: str):
        if not self.current_epoch:
            return
            
        self.current_epoch.abort()
        self.lifecycle_state = EpochLifecycleState.IDLE
        
        self.ledger.append(EventEnvelope(
            event_type=EventType.EPOCH_ABORTED,
            epoch_id=self.current_epoch.epoch_id,
            timestamp=time.time(),
            payload={"reason": reason}
        ))
        
        self.current_epoch = None
        self._epoch_lock.release()

    def _recover_from_logs(self):
        """Rebuild STM from the event ledger."""
        print("Rehydrating Iris's Short-Term Memory...")
        events = self.ledger.read_all()
        committed_payloads = {}
        
        for event in events:
            if event.event_type == EventType.EPOCH_COMMITTED:
                committed_payloads[event.epoch_id] = event.payload
            elif event.event_type == EventType.EPOCH_ABORTED:
                if event.epoch_id in committed_payloads:
                    del committed_payloads[event.epoch_id]
        
        # STM is the list of payloads from committed epochs
        self.stm = list(committed_payloads.values())
        print(f"Rehydrated {len(self.stm)} committed interactions.")
