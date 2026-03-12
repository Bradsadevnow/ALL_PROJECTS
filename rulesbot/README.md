# RulesBot — MTG Comprehensive Rules MCP Server

An MCP (Model Context Protocol) server that exposes Magic: The Gathering's Comprehensive Rules as a queryable tool for LLM integrations.

## Why JSON, Not a Vector DB

The Comprehensive Rules are a well-structured, hierarchical document with canonical section numbers (e.g., `702.5` for Flying, `508` for Declare Attackers Step). Semantic search over embeddings would add overhead and introduce retrieval noise for a document where precise rule citations matter. Instead, `parse_rules.py` extracts the rules into a structured JSON tree that can be searched directly by rule number, keyword, or section — exact matches over a static document.

## Structure

| File | Role |
|------|------|
| `server.py` | MCP server entry point |
| `parse_rules.py` | PDF extraction → structured `rules.json` |
| `rules.json` | Extracted rules database (~3,500 KB) |
| `MagicCompRules *.pdf` | Source document (official WotC release) |

## Setup

```bash
cd rulesbot
pip install -e .  # installs via pyproject.toml

# Re-parse rules from PDF (if PDF is updated)
python parse_rules.py
```

## MCP Integration

Configure in your MCP client (e.g., Claude Desktop, any MCP-compatible host):

```json
{
  "mcpServers": {
    "rulesbot": {
      "command": "python",
      "args": ["/path/to/rulesbot/server.py"]
    }
  }
}
```

The server exposes tools for rule lookup that can be called by any LLM with MCP support, giving it authoritative access to the full Comprehensive Rules during reasoning.
