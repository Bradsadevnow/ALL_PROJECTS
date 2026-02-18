from __future__ import annotations

import asyncio
import json
import threading
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI


class AIBroker:
    """
    Runs a single asyncio event loop in a background thread and executes all
    OpenAI async requests on it.

    Why:
    - Avoids per-turn asyncio.run(...) loop creation/teardown
    - Centralizes timeout behavior and reduces "hang forever" risk

    Note:
    We intentionally use chat.completions here for maximum OpenAI-compatible
    endpoint support (e.g., LM Studio). Some local providers can return payloads
    that the SDK's Responses parser does not handle well.
    """

    def __init__(self) -> None:
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._ready = threading.Event()
        self._client: Optional[AsyncOpenAI] = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return

        self._thread = threading.Thread(target=self._run, name="ai-broker", daemon=True)
        self._thread.start()
        self._ready.wait(timeout=5)
        if not self._ready.is_set():
            raise RuntimeError("AIBroker failed to start event loop")

    def _run(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._loop = loop
        self._client = AsyncOpenAI()
        self._ready.set()
        loop.run_forever()

    def responses_create_text(
        self,
        *,
        model: str,
        input: List[Dict[str, Any]],
        temperature: float,
        max_output_tokens: int,
        timeout: int,
    ) -> str:
        self.start()
        assert self._loop is not None
        assert self._client is not None

        async def _do() -> str:
            # Use chat.completions for broad compatibility with local
            # OpenAI-style servers like LM Studio.
            resp = await self._client.chat.completions.create(
                model=model,
                messages=input,
                temperature=temperature,
                max_tokens=max_output_tokens,
                timeout=timeout,
            )
            return _extract_chat_completion_text(resp)

        fut = asyncio.run_coroutine_threadsafe(_do(), self._loop)
        try:
            return fut.result(timeout=timeout + 5)
        except Exception:
            fut.cancel()
            raise


_BROKER: Optional[AIBroker] = None


def get_broker() -> AIBroker:
    global _BROKER
    if _BROKER is None:
        _BROKER = AIBroker()
    return _BROKER


def _extract_chat_completion_text(resp: Any) -> str:
    """Extract assistant text from varied chat.completions payload shapes."""
    try:
        choices = getattr(resp, "choices", None)
        if not choices:
            raise ValueError("No choices in completion response")
        msg = getattr(choices[0], "message", None)
        if msg is None:
            raise ValueError("No message in first completion choice")
        content = getattr(msg, "content", None)
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            chunks: list[str] = []
            for part in content:
                if isinstance(part, dict):
                    text = part.get("text")
                    if isinstance(text, str):
                        chunks.append(text)
                else:
                    text = getattr(part, "text", None)
                    if isinstance(text, str):
                        chunks.append(text)
            if chunks:
                return "".join(chunks)
        # Fallback to string conversion when content is a non-string scalar.
        if content is not None:
            return str(content)
    except Exception:
        pass

    try:
        dump = resp.model_dump() if hasattr(resp, "model_dump") else None
    except Exception:
        dump = None
    detail = json.dumps(dump, ensure_ascii=False)[:1000] if isinstance(dump, dict) else "<unavailable>"
    raise RuntimeError(f"Unable to extract text from chat completion response: {detail}")
