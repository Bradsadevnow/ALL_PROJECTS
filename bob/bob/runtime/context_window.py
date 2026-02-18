from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default


@dataclass(frozen=True)
class ContextBudget:
    model_window_tokens: int
    summary_target_tokens: int
    live_chat_target_tokens: int
    reserved_buffer_tokens: int


class OSS20BTokenizer:
    """
    Deterministic tokenizer wrapper backed by local OSS-20B artifacts.
    """

    def __init__(self, tokenizer_json_path: str) -> None:
        try:
            from tokenizers import Tokenizer  # type: ignore
        except Exception as e:  # pragma: no cover - environment dependent
            raise RuntimeError(
                "The `tokenizers` package is required for deterministic token accounting."
            ) from e

        if not os.path.exists(tokenizer_json_path):
            raise FileNotFoundError(f"Tokenizer artifact not found: {tokenizer_json_path}")

        self._tok = Tokenizer.from_file(tokenizer_json_path)

    def count(self, text: str) -> int:
        t = text or ""
        return len(self._tok.encode(t).ids)

    def truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        if max_tokens <= 0:
            return ""
        enc = self._tok.encode(text or "")
        if len(enc.ids) <= max_tokens:
            return text or ""
        ids = enc.ids[:max_tokens]
        return self._tok.decode(ids)


def format_live_chat(messages: List[Dict[str, Any]]) -> str:
    lines: list[str] = []
    for m in messages or []:
        role = str(m.get("role") or "").strip().lower()
        content = str(m.get("content") or "").strip()
        if not content:
            continue
        if role == "assistant":
            lines.append(f"Assistant: {content}")
        else:
            lines.append(f"User: {content}")
    return "\n".join(lines)


def keep_last_turns(messages: List[Dict[str, Any]], turns: int) -> List[Dict[str, Any]]:
    n_turns = max(1, int(turns or 1))
    max_messages = n_turns * 2
    if len(messages) <= max_messages:
        return list(messages)
    return list(messages[-max_messages:])


class ContextWindowManager:
    def __init__(self, *, artifacts_dir: str, budget: ContextBudget) -> None:
        tok_path = os.path.join(artifacts_dir, "tokenizer.json")
        self.tokenizer = OSS20BTokenizer(tok_path)
        self.budget = budget

    def count_buckets(
        self,
        *,
        system_block: str,
        conversation_summary: str,
        live_chat_messages: List[Dict[str, Any]],
        tool_injections: str,
        current_user_input: str,
    ) -> Dict[str, Any]:
        summary_block = f"Conversation Summary (non-authoritative):\n{conversation_summary.strip()}".strip()
        live_block = format_live_chat(live_chat_messages)
        user_block = f"Current User Input:\n{(current_user_input or '').strip()}"

        system_tokens = self.tokenizer.count(system_block)
        summary_tokens = self.tokenizer.count(summary_block)
        live_chat_tokens = self.tokenizer.count(live_block)
        tool_tokens = self.tokenizer.count(tool_injections or "")
        current_input_tokens = self.tokenizer.count(user_block)
        reserved_tokens = max(0, int(self.budget.reserved_buffer_tokens))

        used_without_reserve = system_tokens + summary_tokens + live_chat_tokens + tool_tokens + current_input_tokens
        total_with_reserve = used_without_reserve + reserved_tokens
        pressure = total_with_reserve > int(self.budget.model_window_tokens)

        return {
            "system_block": system_tokens,
            "conversation_summary": summary_tokens,
            "live_chat_buffer": live_chat_tokens,
            "tool_injections": tool_tokens,
            "reserved_buffer": reserved_tokens,
            "current_user_input": current_input_tokens,
            "used_without_reserve": used_without_reserve,
            "total_with_reserve": total_with_reserve,
            "model_window": int(self.budget.model_window_tokens),
            "pressure": pressure,
        }

    def fit_live_chat_to_budget(
        self,
        *,
        system_block: str,
        conversation_summary: str,
        live_chat_messages: List[Dict[str, Any]],
        tool_injections: str,
        current_user_input: str,
    ) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        msgs = list(live_chat_messages or [])
        metrics = self.count_buckets(
            system_block=system_block,
            conversation_summary=conversation_summary,
            live_chat_messages=msgs,
            tool_injections=tool_injections,
            current_user_input=current_user_input,
        )
        while msgs and metrics["pressure"]:
            msgs.pop(0)
            metrics = self.count_buckets(
                system_block=system_block,
                conversation_summary=conversation_summary,
                live_chat_messages=msgs,
                tool_injections=tool_injections,
                current_user_input=current_user_input,
            )
        return msgs, metrics

    @staticmethod
    def from_config(cfg: Any) -> "ContextWindowManager":
        budget = ContextBudget(
            model_window_tokens=_safe_int(getattr(cfg, "model_context_window_tokens", 100000), 100000),
            summary_target_tokens=_safe_int(getattr(cfg, "summary_target_tokens", 20000), 20000),
            live_chat_target_tokens=_safe_int(getattr(cfg, "live_chat_target_tokens", 50000), 50000),
            reserved_buffer_tokens=_safe_int(getattr(cfg, "reserved_buffer_tokens", 10000), 10000),
        )
        artifacts = os.path.join(os.path.dirname(__file__), "..", "model_tokenizer")
        artifacts_dir = os.path.abspath(artifacts)
        return ContextWindowManager(artifacts_dir=artifacts_dir, budget=budget)


def render_chat_first_prompt(
    *,
    conversation_summary: str,
    live_chat_messages: List[Dict[str, Any]],
    current_user_input: str,
    tool_injections: Optional[str] = None,
) -> str:
    blocks = [
        "Conversation Summary (non-authoritative):",
        (conversation_summary or "").strip() or "(none)",
        "",
        "Live Chat (recent turns):",
        format_live_chat(live_chat_messages) or "(none)",
    ]
    if tool_injections and tool_injections.strip():
        blocks.extend(["", tool_injections.strip()])
    blocks.extend(["", "Current User Input:", (current_user_input or "").strip()])
    return "\n".join(blocks).strip()
