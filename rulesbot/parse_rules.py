"""Parse the MTG Comprehensive Rules PDF into rules.json.

Run once before starting the MCP server:
    python parse_rules.py
"""

import re
import json
from pathlib import Path

import fitz  # pymupdf

PDF_PATH = Path(__file__).parent / "MagicCompRules 20260116.pdf"
OUTPUT_PATH = Path(__file__).parent / "rules.json"

# Matches rule number at start of a line:
#   "100. General"    -> ("100",   "General")
#   "100.1. These..."  -> ("100.1", "These...")
#   "100.1a A two..."  -> ("100.1a", "A two...")  (no trailing period on lettered rules)
RULE_RE = re.compile(r"^(\d{3,}(?:\.\d+[a-z]?)?)(\.?)\s+(.*)")

# Chapter headings like "1. Game Concepts" — not rules
CHAPTER_RE = re.compile(r"^\d{1,2}\.\s+[A-Z]")

SKIP_LINES = {"Glossary", "Credits", "Contents", "Introduction"}


def find_section_boundaries(doc):
    """Return (glossary_start_page, credits_start_page) by scanning from the end."""
    glossary_page = None
    credits_page = None

    # Rules go up to 905.x; glossary follows. Scan backward for efficiency.
    for page_num in range(len(doc) - 1, -1, -1):
        text = doc[page_num].get_text("text")
        lines = [ln.strip() for ln in text.splitlines()]

        if credits_page is None and "Credits" in lines:
            credits_page = page_num

        if glossary_page is None and "Glossary" in lines:
            glossary_page = page_num

        if glossary_page is not None and credits_page is not None:
            break

    return glossary_page, credits_page


def parse_rules(text: str) -> dict[str, str]:
    """Extract numbered rules from raw text. Returns {rule_number: text}."""
    rules: dict[str, str] = {}
    current_rule: str | None = None
    current_parts: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line or line in SKIP_LINES:
            continue

        # Skip chapter headers (1-2 digit numbers)
        if CHAPTER_RE.match(line):
            continue

        m = RULE_RE.match(line)
        if m:
            if current_rule is not None:
                rules[current_rule] = " ".join(current_parts)
            current_rule = m.group(1)
            current_parts = [m.group(3)] if m.group(3) else []
        elif current_rule is not None:
            current_parts.append(line)

    if current_rule and current_parts:
        rules[current_rule] = " ".join(current_parts)

    return rules


def parse_glossary(doc, start_page: int, end_page: int) -> dict[str, str]:
    """Extract glossary entries using bold-span detection for term headings."""
    glossary: dict[str, str] = {}
    current_term: str | None = None
    current_def: list[str] = []

    for page_num in range(start_page, end_page):
        page = doc[page_num]
        for block in page.get_text("dict")["blocks"]:
            if block.get("type") != 0:
                continue
            for line in block["lines"]:
                line_text = "".join(span["text"] for span in line["spans"]).strip()
                has_bold = any(
                    span["flags"] & 16 or "Bold" in span.get("font", "")
                    for span in line["spans"]
                    if span["text"].strip()
                )

                if not line_text or line_text == "Glossary":
                    continue

                if has_bold:
                    if current_term and current_def:
                        glossary[current_term] = " ".join(current_def).strip()
                    current_term = line_text
                    current_def = []
                elif current_term is not None:
                    current_def.append(line_text)

    if current_term and current_def:
        glossary[current_term] = " ".join(current_def).strip()

    return glossary


def main():
    print(f"Opening {PDF_PATH.name} ({PDF_PATH.stat().st_size // 1024} KB)...")
    doc = fitz.open(str(PDF_PATH))
    print(f"  {len(doc)} pages")

    glossary_page, credits_page = find_section_boundaries(doc)
    print(f"  Glossary starts on page {glossary_page + 1}, Credits on page {credits_page + 1}")

    # Extract rules text (everything before the glossary section)
    rules_text = "\n".join(
        doc[p].get_text("text") for p in range(0, glossary_page)
    )

    print("Parsing rules...")
    rules = parse_rules(rules_text)
    print(f"  {len(rules)} rules extracted")

    print("Parsing glossary...")
    glossary = parse_glossary(doc, glossary_page, credits_page)
    print(f"  {len(glossary)} glossary entries extracted")

    doc.close()

    data = {
        "version": PDF_PATH.stem.split()[-1],  # e.g. "20260116"
        "rules": rules,
        "glossary": glossary,
    }

    OUTPUT_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"Saved to {OUTPUT_PATH} ({OUTPUT_PATH.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
