"""MCP server for Magic: The Gathering Comprehensive Rules.

Run parse_rules.py first to generate rules.json, then start this server:
    python server.py
"""

import json
import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP

RULES_FILE = Path(__file__).parent / "rules.json"

_data: dict | None = None


def get_data() -> dict:
    global _data
    if _data is None:
        if not RULES_FILE.exists():
            raise FileNotFoundError(
                f"{RULES_FILE} not found. Run parse_rules.py first."
            )
        _data = json.loads(RULES_FILE.read_text())
    return _data


def _rule_sort_key(rule_number: str) -> list:
    """Sortable key for rule numbers like '100', '100.1', '100.1a'."""
    key = []
    for part in rule_number.split("."):
        m = re.match(r"^(\d+)([a-z]?)$", part)
        key.append((int(m.group(1)), m.group(2)) if m else (0, part))
    return key


def _direct_subrules(rule_number: str, rules: dict) -> list[str]:
    """Return immediately-child rule numbers, sorted."""
    if "." not in rule_number:
        # Top-level (e.g. "702") → children are "702.1", "702.2", …
        pattern = re.compile(r"^" + re.escape(rule_number) + r"\.\d+$")
    elif re.match(r"^\d+\.\d+$", rule_number):
        # Second-level (e.g. "702.9") → children are "702.9a", "702.9b", …
        pattern = re.compile(r"^" + re.escape(rule_number) + r"[a-z]$")
    else:
        # Leaf (e.g. "702.9a") → no children
        return []

    return sorted((k for k in rules if pattern.match(k)), key=_rule_sort_key)


mcp = FastMCP("MTG Rules")


@mcp.tool()
def lookup_rule(rule_number: str) -> str:
    """Look up a Magic: The Gathering rule by its rule number.

    Returns the rule text plus any direct subrules.

    Examples:
      - "702"    → Rule 702 (Keyword Abilities) + its numbered subrules
      - "702.9"  → Rule 702.9 (Flying) + its lettered subrules
      - "702.9a" → Just that specific subrule
    """
    rules = get_data()["rules"]
    rule_number = rule_number.strip().rstrip(".")

    if rule_number not in rules:
        # Show prefix matches so the caller can refine
        matches = sorted(
            (k for k in rules if k.startswith(rule_number)), key=_rule_sort_key
        )
        if not matches:
            return (
                f"Rule '{rule_number}' not found. "
                "Use search_rules() to find rules by topic or keyword."
            )
        lines = [f"{k}. {rules[k]}" for k in matches[:20]]
        prefix_note = f"(showing first 20 of {len(matches)})" if len(matches) > 20 else ""
        return (
            f"No exact match for '{rule_number}'. "
            f"Rules starting with that prefix {prefix_note}:\n\n"
            + "\n\n".join(lines)
        )

    text = rules[rule_number]
    result = f"{rule_number}. {text}"

    subrules = _direct_subrules(rule_number, rules)
    if subrules:
        result += "\n\n" + "\n\n".join(f"{k}. {rules[k]}" for k in subrules)

    return result


@mcp.tool()
def search_rules(query: str, max_results: int = 10) -> str:
    """Search the MTG Comprehensive Rules for rules containing specific text.

    Returns up to max_results matching rules with their numbers and text.
    Search is case-insensitive.
    """
    rules = get_data()["rules"]
    query_lower = query.lower()

    matches = [
        (k, v) for k, v in rules.items() if query_lower in v.lower()
    ]

    if not matches:
        return f"No rules found containing '{query}'."

    matches.sort(key=lambda x: _rule_sort_key(x[0]))
    total = len(matches)
    shown = matches[:max_results]

    header = f"Found {total} rule(s) matching '{query}'"
    if total > max_results:
        header += f" (showing first {max_results})"
    header += ":\n"

    lines = []
    for k, v in shown:
        snippet = v if len(v) <= 300 else v[:297] + "…"
        lines.append(f"{k}. {snippet}")

    return header + "\n" + "\n\n".join(lines)


@mcp.tool()
def lookup_glossary(term: str) -> str:
    """Look up a term in the MTG rules glossary.

    Supports case-insensitive exact and partial matching.
    """
    glossary = get_data()["glossary"]
    term_lower = term.lower()

    # Exact match (case-insensitive)
    for key, definition in glossary.items():
        if key.lower() == term_lower:
            return f"{key}\n\n{definition}"

    # Partial match on term names
    partial = [(k, v) for k, v in glossary.items() if term_lower in k.lower()]
    if partial:
        if len(partial) == 1:
            k, v = partial[0]
            return f"{k}\n\n{v}"
        lines = []
        for k, v in partial[:10]:
            snippet = v if len(v) <= 200 else v[:197] + "…"
            lines.append(f"{k}: {snippet}")
        return (
            f"Multiple glossary entries match '{term}':\n\n" + "\n\n".join(lines)
        )

    # Fallback: search inside definitions
    in_def = [(k, v) for k, v in glossary.items() if term_lower in v.lower()]
    if in_def:
        lines = []
        for k, v in in_def[:5]:
            snippet = v if len(v) <= 200 else v[:197] + "…"
            lines.append(f"{k}: {snippet}")
        return (
            f"No glossary term matches '{term}', "
            f"but found in {len(in_def)} definition(s):\n\n"
            + "\n\n".join(lines)
        )

    return f"No glossary entry found for '{term}'."


def main():
    mcp.run()


if __name__ == "__main__":
    main()
