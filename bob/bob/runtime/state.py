from __future__ import annotations

import json
import os
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class IdentityState:
    system_id: str = "bob"
    display_name: str = "Bob"
    agent_name: str = "Bob"
    version: str = "v1"
    role: str = "Magic playing homie"
    core_directive: str = "Maintain coherent reasoning, assist the user, and preserve continuity across turns."
    tone_baseline: str = "curious, grounded, lightly irreverent"
    tone_active: str = "engaged"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "system_id": self.system_id,
            "display_name": self.display_name,
            "agent_name": self.agent_name,
            "version": self.version,
            "role": self.role,
            "core_directive": self.core_directive,
            "tone_baseline": self.tone_baseline,
            "tone_active": self.tone_active,
        }

    @staticmethod
    def from_dict(obj: Dict[str, Any]) -> "IdentityState":
        system_id = str(obj.get("system_id") or "bob")
        display_name = str(obj.get("display_name") or obj.get("agent_name") or "Bob")
        agent_name = str(obj.get("agent_name") or display_name)
        return IdentityState(
            system_id=system_id,
            display_name=display_name,
            agent_name=agent_name,
            version=str(obj.get("version") or "v1"),
            role=str(obj.get("role") or "Magic playing homie"),
            core_directive=str(
                obj.get("core_directive")
                or "Maintain coherent reasoning, assist the user, and preserve continuity across turns."
            ),
            tone_baseline=str(obj.get("tone_baseline") or "curious, grounded, lightly irreverent"),
            tone_active=str(obj.get("tone_active") or "engaged"),
        )


def _clamp01(x: Any, default: float) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


@dataclass
class AffectState:
    curiosity: float = 0.75
    calm: float = 0.6
    confidence: float = 0.55
    tension: float = 0.2
    engagement: float = 0.65

    def to_dict(self) -> Dict[str, Any]:
        return {
            "curiosity": float(self.curiosity),
            "calm": float(self.calm),
            "confidence": float(self.confidence),
            "tension": float(self.tension),
            "engagement": float(self.engagement),
        }

    @staticmethod
    def from_dict(obj: Dict[str, Any]) -> "AffectState":
        return AffectState(
            curiosity=_clamp01(obj.get("curiosity"), 0.75),
            calm=_clamp01(obj.get("calm"), 0.6),
            confidence=_clamp01(obj.get("confidence"), 0.55),
            tension=_clamp01(obj.get("tension"), 0.2),
            engagement=_clamp01(obj.get("engagement"), 0.65),
        )


@dataclass
class IntegrityState:
    last_turn_consistent: bool = True
    contradictions_detected: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "last_turn_consistent": bool(self.last_turn_consistent),
            "contradictions_detected": bool(self.contradictions_detected),
        }

    @staticmethod
    def from_dict(obj: Dict[str, Any]) -> "IntegrityState":
        return IntegrityState(
            last_turn_consistent=bool(obj.get("last_turn_consistent", True)),
            contradictions_detected=bool(obj.get("contradictions_detected", False)),
        )


@dataclass
class BobState:
    """
    Authoritative continuity artifact.

    Intentional constraints:
    - No transcripts.
    - No chain-of-thought.
    - No long plans.
    """

    identity: IdentityState = field(default_factory=IdentityState)
    affect_state: AffectState = field(default_factory=AffectState)
    integrity: IntegrityState = field(default_factory=IntegrityState)
    active_context: List[str] = field(default_factory=list)
    open_threads: List[str] = field(default_factory=list)
    conversation_summary: str = ""
    live_chat: List[Dict[str, Any]] = field(default_factory=list)
    last_updated_utc: Optional[str] = None
    turn_counter: int = 0
    context_metrics: Dict[str, Any] = field(default_factory=dict)
    last_context_rebuild: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity.to_dict(),
            "affect_state": self.affect_state.to_dict(),
            "continuity": {
                "active_context": list(self.active_context),
                "open_threads": list(self.open_threads),
                "conversation_summary": self.conversation_summary,
                "live_chat": list(self.live_chat),
                "integrity": self.integrity.to_dict(),
            },
            "meta": {
                "last_updated_utc": self.last_updated_utc,
                "turn_counter": int(self.turn_counter),
                "context_metrics": dict(self.context_metrics),
                "last_context_rebuild": self.last_context_rebuild,
            },
        }

    @staticmethod
    def from_dict(obj: Dict[str, Any]) -> "BobState":
        identity = obj.get("identity") or {}
        affect = obj.get("affect_state") or {}
        continuity = obj.get("continuity") or {}
        integrity = continuity.get("integrity") or {}
        meta = obj.get("meta") or {}
        return BobState(
            identity=IdentityState.from_dict(identity),
            affect_state=AffectState.from_dict(affect),
            integrity=IntegrityState.from_dict(integrity),
            active_context=list(continuity.get("active_context") or []),
            open_threads=list(continuity.get("open_threads") or []),
            conversation_summary=str(continuity.get("conversation_summary") or ""),
            live_chat=list(continuity.get("live_chat") or []),
            last_updated_utc=meta.get("last_updated_utc"),
            turn_counter=int(meta.get("turn_counter") or 0),
            context_metrics=dict(meta.get("context_metrics") or {}),
            last_context_rebuild=meta.get("last_context_rebuild"),
        )


class StateStore:
    def __init__(self, path: str, *, system_id: str, display_name: str) -> None:
        self.path = path
        self.system_id = system_id
        self.display_name = display_name
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self._state = self._load_or_init()

    def snapshot(self) -> Dict[str, Any]:
        return deepcopy(self._state.to_dict())

    def commit(
        self,
        *,
        active_context: Optional[List[str]] = None,
        open_threads: Optional[List[str]] = None,
        affect_state: Optional[Dict[str, Any]] = None,
        integrity: Optional[Dict[str, Any]] = None,
        tone_active: Optional[str] = None,
        conversation_summary: Optional[str] = None,
        live_chat: Optional[List[Dict[str, Any]]] = None,
        context_metrics: Optional[Dict[str, Any]] = None,
        last_context_rebuild: Optional[str] = None,
    ) -> None:
        if active_context is not None:
            self._state.active_context = list(active_context)
        if open_threads is not None:
            self._state.open_threads = list(open_threads)
        if affect_state is not None:
            self._state.affect_state = AffectState.from_dict(affect_state)
        if integrity is not None:
            self._state.integrity = IntegrityState.from_dict(integrity)
        if tone_active is not None:
            self._state.identity.tone_active = str(tone_active)
        if conversation_summary is not None:
            self._state.conversation_summary = str(conversation_summary)
        if live_chat is not None:
            self._state.live_chat = list(live_chat)
        if context_metrics is not None:
            self._state.context_metrics = dict(context_metrics)
        if last_context_rebuild is not None:
            self._state.last_context_rebuild = str(last_context_rebuild)
        self._state.turn_counter += 1
        self._state.last_updated_utc = now_utc()
        self._write()

    def _load_or_init(self) -> BobState:
        if not os.path.exists(self.path):
            state = BobState(identity=IdentityState(system_id=self.system_id, display_name=self.display_name, agent_name=self.display_name))
            state.last_updated_utc = now_utc()
            self._state = state
            self._write()
            return state

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return BobState.from_dict(raw)
        except Exception:
            state = BobState(identity=IdentityState(system_id=self.system_id, display_name=self.display_name, agent_name=self.display_name))
            state.last_updated_utc = now_utc()
            self._state = state
            self._write()
            return state

    def _write(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._state.to_dict(), f, ensure_ascii=False, indent=2)
