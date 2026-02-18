"""
Strict personalization policy for deckbuilder sessions.

This module enforces bounded, STM-only personalization signals.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional, Tuple, Set


class PersonalizationDomain(Enum):
    """Allowed personalization domains."""
    CONVERSATION = "conversation"
    TOOLS_IR = "tools_ir"
    OPT_IN_CONTEXT_APPLE = "opt_in_context_apple"


# Domain-specific allowed abstract signal keys.
ALLOWED_SIGNAL_KEYS: Dict[PersonalizationDomain, Set[str]] = {
    PersonalizationDomain.CONVERSATION: {
        "framing_preference",
        "verbosity_tolerance",
        "humor_directness_balance",
        "question_style",
    },
    PersonalizationDomain.TOOLS_IR: {
        "source_format_preference",
        "depth_vs_breadth",
        "exploration_vs_confirmation",
        "uncertainty_tolerance",
    },
    PersonalizationDomain.OPT_IN_CONTEXT_APPLE: {
        "focus_pattern",
        "energy_pattern",
        "downshift_pattern",
        "novelty_tolerance",
        "session_rhythm",
        "media_context",
    },
}


# STM-only decay windows.
DEFAULT_DOMAIN_TTLS_SECONDS: Dict[PersonalizationDomain, int] = {
    PersonalizationDomain.CONVERSATION: 30 * 60,          # fast decay
    PersonalizationDomain.TOOLS_IR: 2 * 60 * 60,          # medium decay
    PersonalizationDomain.OPT_IN_CONTEXT_APPLE: 60 * 60,  # required decay
}


OUT_OF_SCOPE_TERMS = {
    "identifier", "email", "phone", "address", "location", "gps", "lat", "lng",
    "social_graph", "friend", "follower", "biometric", "health", "medical", "ssn",
    "passport", "device_id", "ip", "name",
}


@dataclass
class SignalRecord:
    """A validated, abstracted STM personalization signal."""
    domain: PersonalizationDomain
    key: str
    value: Any
    created_at: datetime
    expires_at: datetime

    def is_expired(self, now: Optional[datetime] = None) -> bool:
        now = now or datetime.now()
        return now >= self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain.value,
            "key": self.key,
            "value": self.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }

    @classmethod
    def create(
        cls,
        domain: PersonalizationDomain,
        key: str,
        value: Any,
        ttl_seconds: int,
    ) -> "SignalRecord":
        now = datetime.now()
        return cls(
            domain=domain,
            key=key,
            value=value,
            created_at=now,
            expires_at=now + timedelta(seconds=max(0, ttl_seconds)),
        )


def is_out_of_scope_key(key: str) -> bool:
    lowered = key.lower()
    return any(term in lowered for term in OUT_OF_SCOPE_TERMS)


def validate_signal(domain: PersonalizationDomain, key: str, value: Any) -> Tuple[bool, str]:
    """Validate domain, key, and value against hard policy boundaries."""
    if domain not in ALLOWED_SIGNAL_KEYS:
        return False, "domain_not_allowed"

    if is_out_of_scope_key(key):
        return False, "key_out_of_scope"

    if key not in ALLOWED_SIGNAL_KEYS[domain]:
        return False, "key_not_allowed_for_domain"

    if isinstance(value, str) and len(value) > 200:
        return False, "value_too_long"

    if not isinstance(value, (str, int, float, bool)):
        return False, "value_type_not_allowed"

    return True, "ok"
