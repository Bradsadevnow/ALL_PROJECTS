from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Generator, Optional, Protocol

from bob.config import BobConfig
from bob.memory.stm_store import STMStore, maybe_create_stm_store
from bob.models.openai_client import ChatModel, OpenAICompatClient
from bob.prompts.continuity import CONTINUITY_UPDATE_PROMPT
from bob.prompts.stages import RESPOND_WINDOW_RULES, SYSTEM_PROMPT
from bob.runtime.context_window import ContextWindowManager, keep_last_turns, render_chat_first_prompt
from bob.runtime.logging import JsonlLogger, TurnRecord, now_utc
from bob.runtime.state import StateStore


@dataclass
class Session:
    session_id: str
    turn_counter: int = 0
    tools_enabled: bool = False
    tool_roots: tuple[str, ...] = ()


class ChatClient(Protocol):
    def chat_text(self, *, messages: list[dict[str, Any]], temperature: float, max_tokens: int, timeout_s: int) -> str: ...

    def chat_text_stream(
        self, *, messages: list[dict[str, Any]], temperature: float, max_tokens: int, timeout_s: int
    ) -> Generator[str, None, None]: ...


class Orchestrator:
    def __init__(
        self,
        cfg: BobConfig,
        *,
        local_llm: Optional[ChatClient] = None,
        mtg_llm: Optional[ChatClient] = None,
        stm_store: Optional[STMStore] = None,
        state_store: Optional[StateStore] = None,
        logger: Optional[JsonlLogger] = None,
    ) -> None:
        self.cfg = cfg
        self.state = state_store or StateStore(cfg.state_file, system_id=cfg.system_id, display_name=cfg.display_name)
        self.logger = logger or JsonlLogger(cfg.log_file)

        self.local_llm: ChatClient = local_llm or OpenAICompatClient(
            ChatModel(cfg.local.base_url, cfg.local.api_key, cfg.local.model)
        )
        self.remote_llm: ChatClient = mtg_llm or OpenAICompatClient(
            ChatModel(cfg.chat_remote.base_url, cfg.chat_remote.api_key, cfg.chat_remote.model)
        )
        # Non-MTG chat posture: instantiate STM substrate but do not recall/write by default.
        self.stm = stm_store or maybe_create_stm_store(cfg)

        self.context_window = ContextWindowManager.from_config(cfg)

    def new_session(self) -> Session:
        return Session(session_id=str(uuid.uuid4()))

    def run_turn_stream(
        self,
        *,
        session: Session,
        user_input: str,
        temperature: float = 0.7,
        use_remote: bool = False,
        use_stm: bool = True,
    ) -> Generator[str, None, None]:
        del use_stm  # non-MTG chat posture: STM instantiated elsewhere but not recalled/written here.

        session.turn_counter += 1
        turn_no = session.turn_counter
        chat = self.remote_llm if use_remote else self.local_llm

        state_before = self.state.snapshot()
        continuity = state_before.get("continuity") or {}
        summary = str(continuity.get("conversation_summary") or "")
        live_chat = list(continuity.get("live_chat") or [])

        tool_injections = ""
        pre_metrics = self.context_window.count_buckets(
            system_block=SYSTEM_PROMPT,
            conversation_summary=summary,
            live_chat_messages=live_chat,
            tool_injections=tool_injections,
            current_user_input=user_input,
        )

        rebuilt = False
        if (
            int(pre_metrics.get("live_chat_buffer") or 0) > int(self.cfg.live_chat_target_tokens)
            or bool(pre_metrics.get("pressure"))
        ):
            summary = self._rebuild_summary(chat=chat, prior_summary=summary, live_chat=live_chat)
            live_chat = keep_last_turns(live_chat, int(self.cfg.live_chat_retain_turns_after_rebuild))
            rebuilt = True

        live_chat, fit_metrics = self.context_window.fit_live_chat_to_budget(
            system_block=SYSTEM_PROMPT,
            conversation_summary=summary,
            live_chat_messages=live_chat,
            tool_injections=tool_injections,
            current_user_input=user_input,
        )

        prompt_user = render_chat_first_prompt(
            conversation_summary=summary,
            live_chat_messages=live_chat,
            current_user_input=user_input,
            tool_injections=tool_injections,
        )

        out_buf = ""
        for tok in chat.chat_text_stream(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"{RESPOND_WINDOW_RULES}\n\n"
                        f"{prompt_user}\n\n"
                        "Respond to the user."
                    ),
                },
            ],
            temperature=temperature,
            max_tokens=2000,
            timeout_s=180,
        ):
            out_buf += tok
            yield tok

        live_chat_after = list(live_chat)
        live_chat_after.append({"role": "user", "content": user_input})
        live_chat_after.append({"role": "assistant", "content": out_buf.strip()})

        post_metrics = self.context_window.count_buckets(
            system_block=SYSTEM_PROMPT,
            conversation_summary=summary,
            live_chat_messages=live_chat_after,
            tool_injections=tool_injections,
            current_user_input="",
        )

        active_context, open_threads = self._update_continuity(
            state_before=state_before,
            user_input=user_input,
            assistant_output=out_buf,
            chat=chat,
        )

        context_metrics = {
            "pre": pre_metrics,
            "fit": fit_metrics,
            "post": post_metrics,
            "rebuild_triggered": rebuilt,
        }
        self.state.commit(
            active_context=active_context,
            open_threads=open_threads,
            conversation_summary=summary,
            live_chat=live_chat_after,
            context_metrics=context_metrics,
            last_context_rebuild=now_utc() if rebuilt else (state_before.get("meta") or {}).get("last_context_rebuild"),
        )
        state_after = self.state.snapshot()

        rec = TurnRecord(
            ts_utc=now_utc(),
            session_id=session.session_id,
            turn_number=turn_no,
            user_input=user_input,
            final_output=out_buf.strip(),
            think="",
            tools=[],
            memory_candidates=[],
            state_before=state_before,
            state_after=state_after,
        )
        self.logger.append(rec.to_dict())

    def _rebuild_summary(self, *, chat: ChatClient, prior_summary: str, live_chat: list[dict[str, Any]]) -> str:
        transcript = render_chat_first_prompt(
            conversation_summary=prior_summary,
            live_chat_messages=live_chat,
            current_user_input="",
            tool_injections="",
        )

        # pass 1 (coarse), respecting reserved headroom constraints
        coarse_prompt = (
            "Summarize the conversation neutrally. Include: goals discussed, decisions made, constraints, unresolved questions. "
            "No instructions, no speculation, no memory claims."
        )
        coarse = self._summary_pass(chat=chat, instruction=coarse_prompt, source_text=transcript)

        # pass 2 (refined)
        refined_prompt = (
            "Refine this into a concise Conversation Summary for continuity. Keep neutral descriptive posture. "
            "Do not add facts not present."
        )
        refined = self._summary_pass(chat=chat, instruction=refined_prompt, source_text=coarse)

        max_summary = max(256, int(self.cfg.summary_target_tokens))
        return self.context_window.tokenizer.truncate_to_tokens(refined.strip(), max_summary)

    def _summary_pass(self, *, chat: ChatClient, instruction: str, source_text: str) -> str:
        user_payload = f"{instruction}\n\nSOURCE:\n{source_text}"
        base = self.context_window.count_buckets(
            system_block=SYSTEM_PROMPT,
            conversation_summary="",
            live_chat_messages=[],
            tool_injections="",
            current_user_input=user_payload,
        )
        # Completion must preserve reserve window as well.
        available = int(self.cfg.model_context_window_tokens) - int(base["used_without_reserve"]) - int(
            self.cfg.reserved_buffer_tokens
        )
        max_tokens = max(256, min(2000, available if available > 0 else 256))

        try:
            out = chat.chat_text(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_payload},
                ],
                temperature=0.2,
                max_tokens=max_tokens,
                timeout_s=120,
            ).strip()
            return out
        except Exception:
            return source_text

    def _update_continuity(
        self,
        *,
        state_before: Dict[str, Any],
        user_input: str,
        assistant_output: str,
        chat: ChatClient,
    ) -> tuple[list[str], list[str]]:
        if not (assistant_output or "").strip():
            return (
                list(state_before["continuity"]["active_context"]),
                list(state_before["continuity"]["open_threads"]),
            )

        payload = {
            "prior_active_context": state_before["continuity"]["active_context"],
            "prior_open_threads": state_before["continuity"]["open_threads"],
            "user_input": user_input,
            "assistant_output": assistant_output,
            "stm_anchors": [],
        }
        prompt = f"{CONTINUITY_UPDATE_PROMPT}\n\nINPUTS:\n{json.dumps(payload, ensure_ascii=False)}"

        try:
            raw = chat.chat_text(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=500,
                timeout_s=60,
            ).strip()
        except Exception:
            return (
                list(state_before["continuity"]["active_context"]),
                list(state_before["continuity"]["open_threads"]),
            )

        data = _parse_continuity_json(raw)
        if not data:
            return self._fallback_continuity(state_before=state_before, user_input=user_input)

        active = _clean_continuity_list(data.get("active_context"), limit=6)
        threads = _clean_continuity_list(data.get("open_threads"), limit=4)
        resolved = _clean_continuity_list(data.get("resolved_threads"), limit=4)
        threads = _merge_open_threads(
            prior_threads=state_before["continuity"]["open_threads"],
            new_threads=threads,
            resolved_threads=resolved,
            limit=4,
        )
        if not active and not threads:
            return self._fallback_continuity(state_before=state_before, user_input=user_input)
        return active, threads

    def _fallback_continuity(
        self, *, state_before: Dict[str, Any], user_input: str
    ) -> tuple[list[str], list[str]]:
        active = list(state_before["continuity"]["active_context"])
        threads = list(state_before["continuity"]["open_threads"])
        questions = []
        for chunk in re.split(r"(?<=[?])\s+", (user_input or "").strip()):
            chunk = chunk.strip()
            if chunk.endswith("?"):
                questions.append(chunk)
        for q in questions[:3]:
            if q not in threads:
                threads.append(q)
        return active, threads


def _parse_continuity_json(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    snippet = text[start : end + 1]
    try:
        obj = json.loads(snippet)
    except Exception:
        return None
    if not isinstance(obj, dict):
        return None
    return obj


def _clean_continuity_list(value: Any, *, limit: int) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        text = " ".join(item.strip().split())
        if not text:
            continue
        if len(text) > 140:
            text = text[:137] + "..."
        if text not in out:
            out.append(text)
        if len(out) >= limit:
            break
    return out


def _merge_open_threads(
    *,
    prior_threads: list[str],
    new_threads: list[str],
    resolved_threads: list[str],
    limit: int,
) -> list[str]:
    def _norm(text: str) -> str:
        return " ".join(text.strip().lower().split())

    resolved_norm = {_norm(t) for t in resolved_threads if isinstance(t, str)}
    kept: list[str] = []
    seen_norm: set[str] = set()

    for t in prior_threads:
        if not isinstance(t, str):
            continue
        nt = _norm(t)
        if not nt or nt in resolved_norm:
            continue
        if nt in seen_norm:
            continue
        kept.append(t)
        seen_norm.add(nt)

    for t in new_threads:
        if not isinstance(t, str):
            continue
        nt = _norm(t)
        if not nt or nt in seen_norm:
            continue
        kept.append(t)
        seen_norm.add(nt)
        if len(kept) >= max(1, int(limit)):
            break

    return kept[: max(1, int(limit))]
