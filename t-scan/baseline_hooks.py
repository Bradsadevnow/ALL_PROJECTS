#!/usr/bin/env python3
"""
BASELINE MRI — LLaMA-3B (FORWARD HOOKS)

- Logs per-layer activations from attention o_proj
- Outputs in the SAME JSON format as Brain Monolith
- No circuits, just neuron activations
"""

from __future__ import annotations
import json, datetime, os
from pathlib import Path
from collections import defaultdict
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM

# =============================================================================
# CONFIG
# =============================================================================

MODEL_PATH = "./models/llama_3b"
RUN_ID = "llama3b_baseline_hooks"
OUTPUT_ROOT = Path("./runs")

MAX_NEW_TOKENS = 64
SEED = 0

# =============================================================================

def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")

def set_seed(seed: int):
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def safe_device():
    return "cuda" if torch.cuda.is_available() else "cpu"

# =============================================================================
# FORWARD HOOK RIG
# =============================================================================

class ForwardHookRig:
    def __init__(self, model):
        self.model = model
        self.handles = []
        self.attn_out_step = {}

    def _hook_factory(self, layer_idx):
        def hook(module, inputs, output):
            val = output[0] if isinstance(output, tuple) else output
            self.attn_out_step[layer_idx] = (
                val[0, -1, :]
                .detach()
                .to(torch.float32)
            )
        return hook

    def install(self):
        for i, layer in enumerate(self.model.model.layers):
            h = layer.self_attn.o_proj.register_forward_hook(self._hook_factory(i))
            self.handles.append(h)
        print(f"📟 Wired {len(self.handles)} layers.")

    def remove(self):
        for h in self.handles:
            h.remove()
        self.handles = []

    def get_per_layer(self):
        if not self.attn_out_step:
            return None
        return [self.attn_out_step[i] for i in sorted(self.attn_out_step.keys())]

# =============================================================================
# RENDER (MATCHES MONOLITH FORMAT)
# =============================================================================

def render_neurons_only(per_layer):
    neurons_out = {}
    for l, vec in enumerate(per_layer):
        for d in range(vec.shape[0]):
            neurons_out[f"{l+1}:{d+1}"] = {
                "activation": round(float(vec[d]), 6),
                "hits": 0,
                "pos_edges": 0,
                "neg_edges": 0,
                "polarity_flips": 0,
                "is_core": False,
            }
    return neurons_out

# =============================================================================
# RUNNER
# =============================================================================

def run_baseline(tokenizer, model, prompt, device, run_dir):
    tokens_dir = run_dir / "tokens"
    tokens_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "run_id": RUN_ID,
        "model_path": MODEL_PATH,
        "timestamp": now_iso(),
        "device": device,
        "seed": SEED,
        "prompt": prompt,
        "tokens": [],
        "generated_text": ""
    }

    rig = ForwardHookRig(model)
    rig.install()

    try:
        inputs = tokenizer(prompt, return_tensors="pt")
        input_ids = inputs["input_ids"].to(device)

        # PROMPT PASS
        with torch.no_grad():
            _ = model(input_ids)

        per_layer = rig.get_per_layer()
        neurons = render_neurons_only(per_layer)

        artifact = {
            "meta": {"phase": "prompt", "token_index": 0, "token_text": "<PROMPT_END>"},
            "neurons": neurons,
            "edges": {}
        }

        with open(tokens_dir / "t0000_prompt.json", "w") as f:
            json.dump(artifact, f, indent=2)

        metadata["tokens"].append({
            "index": 0,
            "phase": "prompt",
            "token_text": "<PROMPT_END>",
            "file": "tokens/t0000_prompt.json"
        })

        # GENERATION LOOP
        generated = []
        for t in tqdm(range(MAX_NEW_TOKENS), desc="Baseline", unit="tok"):
            with torch.no_grad():
                outputs = model(input_ids)

            token_id = int(outputs.logits[0, -1, :].argmax().item())
            token_text = tokenizer.decode([token_id], skip_special_tokens=False)

            new_token = torch.tensor([[token_id]], device=device)
            input_ids = torch.cat([input_ids, new_token], dim=-1)

            with torch.no_grad():
                _ = model(input_ids)

            per_layer = rig.get_per_layer()
            neurons = render_neurons_only(per_layer)

            generated.append(token_text)
            text_so_far = "".join(generated)

            artifact = {
                "meta": {
                    "phase": "generation",
                    "token_index": t + 1,
                    "token_id": token_id,
                    "token_text": token_text,
                    "text_so_far": text_so_far
                },
                "neurons": neurons,
                "edges": {}
            }

            fname = f"t{t+1:04d}_gen.json"
            with open(tokens_dir / fname, "w") as f:
                json.dump(artifact, f, indent=2)

            metadata["tokens"].append({
                "index": t + 1,
                "phase": "generation",
                "token_text": token_text,
                "text_so_far": text_so_far,
                "file": f"tokens/{fname}"
            })

            metadata["generated_text"] = text_so_far

            if token_id == tokenizer.eos_token_id:
                break

        with open(run_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

    finally:
        rig.remove()
        print(f"\n✅ Baseline complete: {run_dir}")

# =============================================================================
# MAIN
# =============================================================================

def main():
    device = safe_device()
    print(f"[baseline] device={device}")
    set_seed(SEED)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    ).eval()

    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    from fMRI.prompts import PROMPTS

    for category, prompt_list in PROMPTS.items():
        print(f"\n=== CATEGORY: {category} ===")

        for i, prompt in enumerate(prompt_list):
            print(f"Running baseline: {prompt}")

            run_dir = OUTPUT_ROOT / f"{RUN_ID}_{category}_{i:02d}"
            run_dir.mkdir(parents=True, exist_ok=True)

            run_baseline(tokenizer, model, prompt, device, run_dir)

if __name__ == "__main__":
    main()
