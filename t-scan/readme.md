T-Scan: LLM circuit scans + Godot viewer
=======================================

T-Scan is a compact research artifact for probing LLM internals (activations and circuit-like correlations) and visualizing per-token structure in a 3D Godot viewer. It includes:
- Python scripts to log activations, compute windowed correlation "circuits," and run targeted perturbations.
- A Godot 4 scene that renders per-token neuron/edge graphs from JSON artifacts.

This is legacy, exploratory code intended for research and hiring review rather than production use.

Research context (short)
------------------------
This project explores whether stable, interpretable structure emerges in LLM hidden states over short token windows. The probes are intentionally "glass box" and low-friction: grab activations, compute simple temporal correlations, and render the result as a navigable 3D graph for qualitative inspection.

What is in here
--------------
- `monolith_circuits.py` — "Brain Monolith" windowed probe for Llama 3B. Computes circuits once per token window, then renders two outputs: full topology and core-filtered topology. Writes JSON artifacts per token plus `metadata.json`.
- `baseline_hooks.py` — Baseline forward-hook logger for Llama 3B. Logs per-layer `self_attn.o_proj` activations in the same JSON shape as the monolith output (edges empty).
- `mri_hero.py` — "Hero dim" scan that finds correlated dimensions around a single anchor dim using a Pearson/Cosine/Energy trifecta. Outputs `tokens.jsonl` and `constellation/layer_XX.jsonl` logs.
- `log_eval.py` — Aggregates `runs/*/constellation/layer_*.jsonl` to find universal dims across prompt groups.
- `dim_poke.py` — Gradio UI to perturb (poke or suppress) specific dimensions while logging baseline vs. perturbed runs.
- `noderender.gd`, `camera.gd`, `main.tscn` — Godot 4 scene/scripts for the 3D viewer.
- `prompts.py` — Prompt sets used by the probes.
- `screenshots/` — Example captures of the viewer.

Outputs and data format
-----------------------
The probe scripts emit per-token JSON artifacts designed for the viewer:

- Monolith + baseline outputs:
  - `runs/<run_id>/tokens/t0000_prompt.json`
  - `runs/<run_id>/tokens/t####_gen.json`
  - For monolith: `tokens_filtered/` is the core-filtered variant.
  - Each JSON contains:
    - `meta` (phase, token index/id, token text, etc.)
    - `neurons`: dict keyed by `"layer:dim"` (1-indexed)
    - `edges`: dict keyed by `"layer:dim|layer:dim"` (1-indexed)

- Hero scan outputs:
  - `runs/<run_id>/tokens.jsonl` (token map)
  - `runs/<run_id>/constellation/layer_XX.jsonl` (correlated dims per time step)
  - These dim indices are zero-based.

- Dim poke outputs:
  - `logs/<timestamp>/base/` and `logs/<timestamp>/perturbed/`
  - Each contains `run.json`, `tokens.jsonl`, and `layer_XX.jsonl`.
  - Indexing is explicitly zero-based in `run.json`.

Quickstart (local)
------------------
Requirements: Python 3.10+, PyTorch, Transformers, NumPy, tqdm, and (for `dim_poke.py`) Gradio. A GPU is strongly recommended.

Model paths are hardcoded in scripts:
- Llama 3B: `./models/llama_3b` (monolith + baseline)
- Llama 3.2-3B-Instruct: `./models/Llama-3.2-3B-Instruct` (hero + poke)

Update those paths (or add symlinks) to match your local model folders.

Running the probes
------------------
- Monolith circuit scan (full + core-filtered):
  - `python monolith_circuits.py`
  - Outputs to `runs/llama3b_windowed_probe_<group>_<idx>/`

- Baseline hook scan (activations only):
  - `python baseline_hooks.py`
  - Outputs to `runs/llama3b_baseline_hooks_<group>_<idx>/`

- Hero-dim scan (correlation trifecta):
  - `python mri_hero.py`
  - Outputs to `runs/<group>_<idx>_seed<seed>/`

- Universal-dim evaluation:
  - `python log_eval.py`
  - Reads `runs/*/constellation/` and prints intersection results.

- Dim poke UI (baseline vs. perturbed comparison):
  - `python dim_poke.py`
  - Opens a Gradio UI and writes runs to `logs/<timestamp>/`.

Viewer (Godot 4)
----------------
Open `main.tscn` in Godot 4. The viewer renders the JSON artifacts as a 3D grid:
- `noderender.gd` loads a single token JSON (`data_path`) and draws nodes/edges.
- `camera.gd` provides RTS-style camera controls (pan/rotate/zoom + click selection).

To point the viewer at new data:
1. Copy your token JSONs into the project (e.g., under `res://data/...`).
2. Update `data_path`, `token_start`, and `token_end` in `noderender.gd` or the scene inspector.

Controls in the viewer:
- Left click: select neuron
- Right mouse: rotate
- Left mouse drag: pan
- Middle mouse drag: vertical move
- Scroll wheel: zoom
- Arrow keys: step tokens / move layer cursor
- Enter: toggle layer visibility

Notes and gotchas
-----------------
- Prompt sets live in `prompts.py`, but `monolith_circuits.py` and `baseline_hooks.py`
  import `PROMPTS` from `fMRI.prompts`. If you do not have that package, update
  the import to `from prompts import PROMPTS`.
- Indexing differs by tool: monolith/baseline use 1-indexed neuron IDs, hero/poke use zero-based.
- This is research code: expect to tune thresholds and filters per model.
