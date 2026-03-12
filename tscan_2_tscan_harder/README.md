# T-Scan 2: T-Scan Harder

Extended experimentation building on [T-Scan](../t-scan). Where T-Scan established the tooling (activation probing, circuit discovery, Godot viewer), this project applies it at scale — 88+ experimental runs across multiple prompt groups and model conditions — to investigate whether stable, universal activation patterns exist across diverse input contexts.

## Research Questions

- Do certain hidden-state dimensions activate consistently across unrelated prompts?
- Do "circuit" correlations persist across different conversational registers (assistant vs. character)?
- What does perturbation of high-correlation dims do to output quality and behavior?

## Structure

| Path | Contents |
|------|----------|
| `runs_fletcher/` | 88 experimental runs — "Fletcher" persona prompt group |
| `runs_helpful_assistant/` | 71 runs — baseline helpful assistant prompt group |
| `monolith_circuits.py` | Circuit discovery pipeline (ported/extended from T-Scan) |
| `monolith_fletcher.py` | Fletcher-specific variant |
| `dim_poke.py` | Dimension perturbation tool |
| `log_cat.py` / `flet_cat.py` | Log aggregation and analysis utilities |
| `agent.py` | Agentic probing pipeline |
| `prompts.py` | Prompt sets for both groups |

**Analysis notes:**
- `exp.md` — Design philosophy and experiment log
- `current_interp.md` — Current interpretation of findings
- `gemini_notes.md` — Gemini API behavior observations
- `fletcher.txt` / `h.txt` — Detailed run logs

## Key Finding Direction

The Fletcher vs. helpful-assistant comparison tests whether persona/identity framing produces distinct, stable activation signatures — or whether surface-level stylistic differences vanish at the hidden-state level. The `log_cat.py` aggregation and `log_eval.py` (from T-Scan) find intersection dims across run groups.

## Usage

```bash
cd tscan_2_tscan_harder
pip install torch transformers numpy tqdm gradio

# Run circuit scan (Fletcher prompts)
python monolith_fletcher.py

# Aggregate universal dims across all runs
python log_cat.py

# Dimension perturbation UI
python dim_poke.py
```

Model paths are hardcoded to `./models/` — update or symlink to your local model folder. GPU strongly recommended.

See [T-Scan README](../t-scan/readme.md) for full details on the tooling, data formats, and Godot viewer.
