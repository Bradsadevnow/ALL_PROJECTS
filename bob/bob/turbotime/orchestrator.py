from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Generator, Optional, Protocol

from bob.config import BobConfig
from bob.memory.stm_store import STMStore, maybe_create_stm_store
from bob.models.openai_client import ChatModel, OpenAICompatClient
from bob.runtime.context_window import ContextWindowManager, keep_last_turns, render_chat_first_prompt
from bob.runtime.logging import JsonlLogger, TurnRecord, now_utc
from bob.runtime.state import StateStore
from bob.prompts.continuity import CONTINUITY_UPDATE_PROMPT
from bob.turbotime.prompts import (
    SYSTEM_PROMPT,
    STAGE1_ORIENTATION_PROMPT,
    STAGE2_PLANNING_PROMPT,
    STAGE2_INTEGRATION_PROMPT,
    STAGE3_RESPONSE_PROMPT,
)
from bob.turbotime.tools import ToolRegistry, ToolResult, format_tool_results, parse_tool_requests
from bob.tools.sandbox import ToolSandbox


@dataclass
class Session:
    session_id: str
    turn_counter: int = 0


class ChatClient(Protocol):
    def chat_text(self, *, messages: list[dict[str, Any]], temperature: float, max_tokens: int, timeout_s: int) -> str: ...

    def chat_text_stream(
        self, *, messages: list[dict[str, Any]], temperature: float, max_tokens: int, timeout_s: int
    ) -> Generator[str, None, None]: ...


class TurbotimeOrchestrator:
    def __init__(
        self,
        cfg: BobConfig,
        *,
        local_llm: Optional[ChatClient] = None,
        mtg_llm: Optional[ChatClient] = None,
        stm_store: Optional[STMStore] = None,
        state_store: Optional[StateStore] = None,
        logger: Optional[JsonlLogger] = None,
        tool_registry: Optional[ToolRegistry] = None,
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

        self.stm = stm_store or maybe_create_stm_store(cfg)
        self.context_window = ContextWindowManager.from_config(cfg)

        if getattr(cfg, "tool_sandbox_enabled", False):
            sandbox = ToolSandbox.enabled_with_roots(getattr(cfg, "tool_roots", []))
        else:
            sandbox = ToolSandbox.disabled()
        self.tools = tool_registry or ToolRegistry(sandbox=sandbox, runtime_dir=cfg.runtime_dir)

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
        enabled_tools: Optional[list[str] | str] = None,
        pending_tools: Optional[list[str] | str] = None,
    ) -> Generator[str, None, None]:
        session.turn_counter += 1
        turn_no = session.turn_counter

        state_before = self.state.snapshot()
        chat = self.remote_llm if use_remote else self.local_llm

        continuity = state_before.get("continuity") or {}
        summary = str(continuity.get("conversation_summary") or "")
        live_chat = list(continuity.get("live_chat") or [])

        enabled_list = self._normalize_enabled_tools(enabled_tools)
        pending_list = self._normalize_enabled_tools(pending_tools)
        allowed_tools, enabled_public = self.tools.resolve_allowed(enabled_list)
        tool_context = self._format_tool_context(enabled_public)

        pre_metrics = self.context_window.count_buckets(
            system_block=SYSTEM_PROMPT,
            conversation_summary=summary,
            live_chat_messages=live_chat,
            tool_injections=tool_context,
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
            tool_injections=tool_context,
            current_user_input=user_input,
        )

        # Stage 1: Orientation
        stage1 = chat.chat_text(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"{STAGE1_ORIENTATION_PROMPT}\n\n"
                        f"{tool_context}\n\n"
                        f"=== AUTHORITATIVE STATE (TRUTH) ===\n{json.dumps(state_before, ensure_ascii=False, indent=2)}\n\n"
                        f"=== CURRENT USER INPUT ===\n{user_input}\n"
                    ),
                },
            ],
            temperature=0.4,
            max_tokens=800,
            timeout_s=120,
        ).strip()

        # Stage 2: Planning
        thalamic_window = self._build_thalamic_window(
            state_before,
            user_input=user_input,
            orientation=stage1,
            tool_context=tool_context,
        )
        stage2 = chat.chat_text(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{STAGE2_PLANNING_PROMPT}\n\n{thalamic_window}"},
            ],
            temperature=0.4,
            max_tokens=2000,
            timeout_s=120,
        ).strip()

        # Tool requests
        tool_requests = parse_tool_requests(stage2)
        tool_results: list[ToolResult] = []
        for req in tool_requests:
            tool_name = str(req.get("tool") or "").strip()
            args = req.get("args") or {}
            tool_results.append(
                self.tools.run(
                    tool_name=tool_name,
                    args=args,
                    allowed_tools=allowed_tools,
                    bypass_sandbox=bool(enabled_public),
                )
            )

        cognition_final = stage2
        if tool_results:
            tool_block = format_tool_results(tool_results)
            cognition_final = chat.chat_text(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": (
                            f"{STAGE2_INTEGRATION_PROMPT}\n\n"
                            f"PRIOR DELIBERATION:\n{stage2}\n\n"
                            f"TOOL RESULTS:\n{tool_block}\n"
                        ),
                    },
                ],
                temperature=0.4,
                max_tokens=1600,
                timeout_s=120,
            ).strip()

        # non-MTG chat posture: no automatic memory candidates in casual chat.
        memory_candidates: list[dict[str, Any]] = []

        del use_stm
        tool_results_log: list[dict[str, Any]] = [r.to_dict() for r in tool_results]
        if pending_list:
            tool_results_log.append(
                {
                    "tool_name": "TOOL_ENABLEMENT",
                    "status": "pending",
                    "pending_tools": pending_list,
                    "active_tools": enabled_public,
                }
            )

        tool_block = format_tool_results(tool_results)
        injections = tool_context
        if tool_block:
            injections = f"{injections}\n\n=== TOOL RESULTS (INTERNAL) ===\n{tool_block}"
        respond_context = render_chat_first_prompt(
            conversation_summary=summary,
            live_chat_messages=live_chat,
            current_user_input=user_input,
            tool_injections=injections,
        )

        safe_think = self._strip_control_sections(cognition_final)
        out_buf = ""
        for tok in chat.chat_text_stream(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"{STAGE3_RESPONSE_PROMPT}\n\n"
                        f"{respond_context}\n\n"
                        f"INTERNAL THINK NOTES (NOT USER-FACING):\n{safe_think}\n\n"
                        f"Respond to the user."
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
            tool_injections=injections,
            current_user_input="",
        )

        active_context, open_threads = self._update_continuity(
            state_before=state_before,
            user_input=user_input,
            assistant_output=out_buf,
            chat=chat,
            stm_anchors=[],
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
            think=f"STAGE1\n{stage1}\n\nSTAGE2\n{cognition_final}",
            tools=tool_results_log,
            memory_candidates=memory_candidates,
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

        coarse_prompt = (
            "Summarize the conversation neutrally. Include: goals discussed, decisions made, constraints, unresolved questions. "
            "No instructions, no speculation, no memory claims."
        )
        coarse = self._summary_pass(chat=chat, instruction=coarse_prompt, source_text=transcript)

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

    def _format_stm_block(self, stm_hits: list[dict[str, Any]]) -> str:
        if not stm_hits:
            return ""
        lines = ["=== STM RECALL (NON-AUTHORITATIVE) ==="]
        for h in stm_hits:
            text = str(h.get("text") or "").strip()
            meta = h.get("metadata") or {}
            created = meta.get("created_at") or meta.get("created_at_utc")
            prefix = f"- ({created}) " if created else "- "
            if text:
                lines.append(prefix + text)
        return "\n".join(lines)

    def _build_thalamic_window(
        self,
        state: Dict[str, Any],
        *,
        user_input: str,
        orientation: str,
        tool_results: Optional[str] = None,
        tool_context: Optional[str] = None,
    ) -> str:
        blocks = [
            "=== AUTHORITATIVE STATE (TRUTH) ===",
            json.dumps(state, ensure_ascii=False, indent=2),
            "\n=== CURRENT USER INPUT ===",
            user_input,
            "\n=== STAGE 1 ORIENTATION (INTERNAL) ===",
            orientation.strip() if orientation else "",
        ]
        if tool_context:
            blocks.append("\n" + tool_context)
        if tool_results:
            blocks.append("\n=== TOOL RESULTS (INTERNAL) ===")
            blocks.append(tool_results)
        return "\n".join(blocks)

    def _format_tool_context(self, enabled_tools: list[str]) -> str:
        lines = ["=== ENABLED TOOLS ==="]
        if not enabled_tools:
            lines.append("NONE")
            return "\n".join(lines)
        for name in enabled_tools:
            lines.append(f"- {name}")
        return "\n".join(lines)

    def _normalize_enabled_tools(self, enabled_tools: Optional[list[str] | str]) -> list[str]:
        if enabled_tools is None:
            return []
        if isinstance(enabled_tools, str):
            return [enabled_tools]
        out: list[str] = []
        for item in enabled_tools:
            if not item:
                continue
            out.append(str(item))
        return out

    def _strip_control_sections(self, think: str) -> str:
        section_re = re.compile(r"^\s*([A-Z][A-Z _/]{2,})\s*:\s*$")
        drop = {"TOOL REQUESTS", "MEMORY CANDIDATES"}
        out: list[str] = []
        skipping = False
        for raw in (think or "").splitlines():
            line = raw.rstrip("\n")
            m = section_re.match(line.strip())
            if m:
                header = m.group(1).strip().upper()
                skipping = header in drop
                if skipping:
                    continue
            if skipping:
                continue
            out.append(line)
        return "\n".join(out).strip()

    def _build_stm_trace(
        self, *, user_input: str, assistant_output: str, tool_results: list[dict[str, Any]]
    ) -> str:
        def _truncate(s: str, limit: int) -> str:
            if len(s) <= limit:
                return s
            return s[: max(0, limit - 3)] + "..."

        user_text = (user_input or "").strip()
        assistant_text = (assistant_output or "").strip()

        intent = _truncate(user_text.splitlines()[0] if user_text else "", 200)

        open_questions: list[str] = []
        for chunk in re.split(r"(?<=[?])\s+", user_text):
            chunk = chunk.strip()
            if chunk.endswith("?"):
                open_questions.append(_truncate(chunk, 200))
        if len(open_questions) > 3:
            open_questions = open_questions[:3]

        tools_used = []
        for t in tool_results:
            name = t.get("tool_name")
            if isinstance(name, str) and name:
                tools_used.append(name)
        tools_used = tools_used[:10]

        entities: list[str] = []
        for m in re.findall(r"[A-Za-z0-9_./:-]{3,}", user_text):
            if "/" in m or "." in m:
                entities.append(m)
        if len(entities) > 10:
            entities = entities[:10]

        resolution = ""
        if assistant_text:
            resolution = _truncate(assistant_text.splitlines()[0], 200)

        trace_obj = {
            "intent": intent,
            "resolution": resolution,
            "open_questions": open_questions,
            "tools_used": tools_used,
            "entities": entities,
        }
        text = json.dumps(trace_obj, ensure_ascii=False)
        max_chars = int(getattr(self.cfg, "stm_max_entry_chars", 3072))
        if len(text) > max_chars:
            trace_obj["resolution"] = ""
            trace_obj["open_questions"] = []
            text = json.dumps(trace_obj, ensure_ascii=False)
        if len(text) > max_chars:
            trace_obj["entities"] = trace_obj["entities"][:5]
            text = json.dumps(trace_obj, ensure_ascii=False)
        if len(text) > max_chars:
            text = text[: max_chars - 3] + "..."
        return text

    def _promotion_entry_to_candidate(self, entry: dict[str, Any]) -> Optional[dict[str, Any]]:
        text = str(entry.get("text") or "").strip()
        if not text:
            return None
        meta = entry.get("metadata") or {}
        trace: dict[str, Any]
        try:
            trace = json.loads(text)
        except Exception:
            trace = {"intent": text}

        intent = str(trace.get("intent") or "").strip()
        entities = trace.get("entities") or []
        if not isinstance(entities, list):
            entities = []
        entities = [str(e) for e in entities if e]

        lowered = intent.lower()
        if any(tok in lowered for tok in ["prefer", "please", "don't", "do not", "only", "always", "never"]):
            mem_type = "preference"
        elif any(tok in lowered for tok in ["decide", "decision", "we will", "let's", "we should"]):
            mem_type = "project_decision"
        elif any(tok in lowered for tok in ["how to", "steps", "procedure", "workflow"]):
            mem_type = "procedure"
        else:
            mem_type = "fact"

        base_text = intent or text
        if base_text:
            cand_text = f"User intent (recurring): {base_text}"
        else:
            cand_text = "User intent (recurring)"

        tags = ["stm_promotion"]
        tags.extend(entities[:5])

        access_count = meta.get("access_count")
        sessions_seen = meta.get("sessions_seen")
        why = f"STM promotion: access_count={access_count}, sessions_seen={sessions_seen}"

        return {
            "text": cand_text,
            "type": mem_type,
            "tags": tags,
            "ttl_days": 180,
            "source": "assistant_inferred",
            "why_store": why,
            "promotion_stm_id": entry.get("id"),
        }

    def _update_continuity(
        self,
        *,
        state_before: Dict[str, Any],
        user_input: str,
        assistant_output: str,
        chat: ChatClient,
        stm_anchors: Optional[list[str]] = None,
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
            "stm_anchors": stm_anchors or [],
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


def _summarize_stm_hits(hits: list[dict[str, Any]], *, limit: int = 4) -> list[str]:
    out: list[str] = []
    for h in hits or []:
        raw = str(h.get("text") or "").strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
        except Exception:
            obj = {"intent": raw}

        intent = str(obj.get("intent") or "").strip()
        if intent:
            out.append(f"intent: {intent}")

        open_q = obj.get("open_questions") or []
        if isinstance(open_q, list):
            for q in open_q:
                q_text = str(q or "").strip()
                if q_text:
                    out.append(f"open_q: {q_text}")

        if len(out) >= limit:
            break

    return out[:limit]
