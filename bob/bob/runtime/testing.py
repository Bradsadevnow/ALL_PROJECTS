from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Generator, List


@dataclass(frozen=True)
class FakeLLMResponsePlan:
    think: str = "SITUATION:\n- test\n\nPLAN:\n- test\n\nTOOL REQUESTS:\n- NONE\n\nMEMORY CANDIDATES:\n- NONE"
    respond: str = "Hello from Bob."


class FakeChatClient:
    """
    Deterministic, no-network stand-in for an OpenAI-compatible chat client.

    Intended for unit tests of orchestration, logging, and state semantics.
    """

    def __init__(self, plan: FakeLLMResponsePlan | None = None) -> None:
        self.plan = plan or FakeLLMResponsePlan()
        self.calls: List[Dict[str, Any]] = []

    def chat_text(self, *, messages: list[dict[str, Any]], temperature: float, max_tokens: int, timeout_s: int) -> str:
        self.calls.append(
            {
                "kind": "chat_text",
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "timeout_s": timeout_s,
            }
        )

        # Decide which stage based on user content
        user_blob = ""
        for m in messages:
            if m.get("role") == "user":
                user_blob += str(m.get("content") or "")

        if "THINK/RECALL" in user_blob or "INTERNAL WINDOW" in user_blob:
            return self.plan.think
        # Default to think if unknown
        return self.plan.think

    def chat_text_stream(
        self, *, messages: list[dict[str, Any]], temperature: float, max_tokens: int, timeout_s: int
    ) -> Generator[str, None, None]:
        self.calls.append(
            {
                "kind": "chat_text_stream",
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "timeout_s": timeout_s,
            }
        )
        # Stream one character chunk to emulate incremental UI updates
        for ch in self.plan.respond:
            yield ch
