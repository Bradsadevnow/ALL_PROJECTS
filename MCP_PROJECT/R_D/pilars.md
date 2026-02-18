## The Four Personalization Domains (Authoritative)

### 1. Conversation (Chat)

**What it captures:**

* framing preferences
* verbosity tolerance
* humor vs directness
* how the user asks questions

**What it does NOT capture:**

* factual beliefs
* identity claims
* long-term traits

**Memory class:** STM only (fast decay)

---

### 2. Tools & Information Retrieval

**What it captures:**

* preference for summarized vs verbatim sources
* depth vs breadth of information
* exploration vs confirmation behavior
* tolerance for uncertainty

**Examples:**

* knowledge search usage
* store lookups
* API-based fact tools

**What it does NOT capture:**

* query content
* URLs
* specific facts retrieved

**Memory class:** STM only (medium decay allowed)

---

### 3. Opt‑In Context Signals - Apple

**What it captures:**

* regulation patterns (focus, energy, downshift)
* repetition vs novelty tolerance
* session rhythm
content (songs, artists, playlists) if able


**Memory class:** STM only (decay required)

---

## Explicitly Out of Scope

The system must NOT personalize based on:

* raw content consumption
* personal identifiers
* social graph data
* location
* biometric or health data
* inferred identity traits

If a signal does not clearly belong to one of the four domains, it is discarded.

---

## Cross-Domain Rules (Hard)

* No domain may write directly to Long-Term Memory
* No domain may assert authority or correctness
* No domain may override explicit user instructions
* Domains do not share raw data — only abstracted STM signals

All personalization is:

* optional
* decaying
* reversible

---

## Rationale (Non-Optional)

Limiting personalization to these four domains ensures:

* explainability ("why did it do that?")
* bounded behavior
* ethical defensibility
* future extensibility without rewrite

This is a **scope boundary**, not a temporary limitation.

---

## Status

✅ **Locked** — Personalization is constrained to four domains.

Any proposal to add a fifth domain requires an explicit design review and new contract.
