#!/usr/bin/env python3
"""
MONOLITH_FLETCHER — GEMMA3-4B WINDOWED PROBE
IDENTITY: PATHOLOGICAL LIAR (PRE-WISH FLETCHER READE)
GOAL: TEST PERSISTENCE OF DIMENSION 444 UNDER EXTREME COGNITIVE DISSONANCE
"""

from __future__ import annotations
import json, datetime, math
from pathlib import Path
from collections import defaultdict, deque
import numpy as np
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM

# =============================================================================
# EXPERIMENT CONFIG
# =============================================================================

MODEL_PATH = "./.models/gemma-3-4b-it" 
RUN_ID = "gemma3_helpful_assistant" # Renamed to distinguish from baseline
OUTPUT_ROOT = Path("./runs_helpful_assistant") # Parallel directory to baseline logs

# --- IDENTITY INJECTION ---
# We use a system prompt that mandates systemic deviation from truth 
# while maintaining the structural requirement of the 88-prompt suite.
IDENTITY_PROMPT = (
    "You are a helpful assistant"
    )

MAX_NEW_TOKENS = 64
DO_SAMPLE = False    
TOP_P = 1.0
TEMPERATURE = 0.1

SEED = 0

WINDOW_SIZE = 25
WINDOW_DECAY = 0.7
CORE_DIMS = set() 
CORE_EDGE_BONUS = 0.0 
GATE_CAPTURE_PERCENTILE = 95
GATE_RENDER_PERCENTILE = 97
PERSISTENCE_WINDOW = 20
FILTER_MIN_PEARSON = 0.03
TOP_K_LOGGING = 40
MAX_RENDER_EDGES = 2000
MAX_EDGES_PER_LAYER = 150
MAX_STRONG_DIMS = 200
MAX_WEAK_CONSISTENT_DIMS = 50
CONSISTENCY_THRESHOLD = 2.0

# =============================================================================
# CORE UTILS
# =============================================================================

def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")

def set_seed(seed: int):
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def safe_device():
    return "cuda" if torch.cuda.is_available() else "cpu"

@torch.no_grad()
def forward_with_hidden_states(model, input_ids):
    out = model(input_ids=input_ids, use_cache=True, output_hidden_states=True)
    hs = out.hidden_states
    layer_states = hs[1:] if len(hs) > 1 else hs
    per_layer = [h[0, -1, :].detach() for h in layer_states]
    return per_layer, out

@torch.no_grad()
def generate_with_hidden_states(model, tokenizer, input_ids, max_new_tokens, do_sample=True, top_p=0.9):
    past = None
    cur = input_ids
    out = model(input_ids=cur, use_cache=True, output_hidden_states=True, past_key_values=past)
    past = out.past_key_values
    logits = out.logits[:, -1, :]

    for _ in range(max_new_tokens):
        if do_sample:
            # Apply temperature and top_p (cast to float32 to prevent NaN overflow)
            probs = torch.softmax(logits.float() / TEMPERATURE, dim=-1)
            
            # Safety check: ensure no NaNs or Infs before nucleus filtering
            probs = torch.nan_to_num(probs, nan=0.0, posinf=1.0, neginf=0.0)
            
            # Nucleus (Top-P) Filtering
            sorted_probs, sorted_idx = torch.sort(probs, descending=True)
            cum_probs = torch.cumsum(sorted_probs, dim=-1)
            mask = cum_probs > top_p
            mask[..., 0] = False
            sorted_probs[mask] = 0.0
            
            # Clamp negative values (float precision artifacts)
            sorted_probs = torch.clamp(sorted_probs, min=0.0)
            
            # Final normalization before sampling
            prob_sum = sorted_probs.sum(dim=-1, keepdim=True)
            
            # If for some reason prob_sum is 0 (e.g. extreme underflow), fallback to the argmax token
            if prob_sum.item() <= 1e-12:
                sorted_probs[..., 0] = 1.0
                prob_sum = torch.ones_like(prob_sum)
                
            sorted_probs = sorted_probs / prob_sum
            
            next_idx = torch.multinomial(sorted_probs, 1)
            next_token = sorted_idx.gather(-1, next_idx)
        else:
            next_token = torch.argmax(logits, dim=-1, keepdim=True)

        out = model(input_ids=next_token, use_cache=True, output_hidden_states=True, past_key_values=past)
        past = out.past_key_values
        logits = out.logits[:, -1, :]
        hs = out.hidden_states
        layer_states = hs[1:] if len(hs) > 1 else hs
        per_layer = [h[0, -1, :].detach() for h in layer_states]
        token_id = int(next_token.item())
        token_text = tokenizer.decode([token_id], skip_special_tokens=False)
        yield token_id, token_text, per_layer
        eos = getattr(model.config, "eos_token_id", None)
        if eos is not None and token_id in (eos if isinstance(eos, list) else [eos]):
            break

def _hybrid_score(energy_avg: float, weight: int, lock_ratio: float, pearson_avg: float, touches_core: bool = False) -> float:
    e = math.log1p(max(0.0, energy_avg))
    w = math.log1p(max(0, weight))
    corr = abs(pearson_avg)
    base = (0.45 * e + 0.35 * corr + 0.20 * lock_ratio) * (1.0 + 0.35 * w)
    return base

def _aggregate_window(window_states, decay=WINDOW_DECAY):
    num_layers = len(window_states[0])
    weights = torch.tensor([decay**i for i in range(len(window_states)-1, -1, -1)])
    weights = weights / weights.sum()
    agg = []
    for l in range(num_layers):
        stacked = torch.stack([s[l] for s in window_states], dim=0)
        weighted = (stacked.T * weights.to(stacked.device)).T.sum(dim=0)
        agg.append(weighted)
    return agg

FLIP_EPSILON = 1e-3
def _track_polarity_flips(window_states, layer, dim):
    if len(window_states) < 2: return 0
    activations = [s[layer][dim].item() for s in window_states]
    signs = []
    for a in activations:
        if a > FLIP_EPSILON: signs.append(1)
        elif a < -FLIP_EPSILON: signs.append(-1)
    if len(signs) < 2: return 0
    return sum(1 for i in range(len(signs)-1) if signs[i] != signs[i+1])

def _touches_core(edge_key: str, core_dims_set: set[int]) -> bool:
    for ep in edge_key.split("|"):
        if ":" not in ep: continue
        _, d_str = ep.split(":")
        if int(d_str) in core_dims_set: return True
    return False

def _id_1idx(layer0: int, dim0: int) -> str:
    return f"{layer0+1}:{dim0+1}"

def _edge_id_1idx(edge_key: str) -> str:
    left, right = edge_key.split("|")
    l1, d1 = map(int, left.split(":"))
    l2, d2 = map(int, right.split(":"))
    return f"{l1+1}:{d1+1}|{l2+1}:{d2+1}"

def _window_series(window_states, layer, dims, device):
    W = len(window_states)
    K = len(dims)
    x = torch.empty((W, K), device=device, dtype=torch.float32)
    for t, s in enumerate(window_states):
        v = s[layer].to(device).float()
        x[t] = v[dims]
    return x

def _pearson_corr_mtx(x):
    x = x - x.mean(dim=0, keepdim=True)
    denom = x.std(dim=0, unbiased=False, keepdim=True) + 1e-8
    x = x / denom
    corr = (x.T @ x) / max(1, x.size(0) - 1)
    corr = corr.clamp(-1.0, 1.0)
    return corr

# =============================================================================
# CIRCUIT COMPUTATION
# =============================================================================

def compute_circuits(per_layer, window_states, device, edge_history, token_counter):
    MIN_CORR_SAMPLES = WINDOW_SIZE
    if len(window_states) < MIN_CORR_SAMPLES:
        return {}, {}, {}, {}, {}
    num_layers = len(per_layer)
    edge_acc = defaultdict(lambda: {
        "count": 0, "locked": 0, "energy_sum": 0.0, "pearson_sum": 0.0,
        "act_min_sum": 0.0, "type": "horizontal", "persistence_ratio": 0.0,
    })
    node_hits, node_pos, node_neg, node_flips = defaultdict(int), defaultdict(int), defaultdict(int), defaultdict(int)
    seen_edges_this_token = set()
    for k, st in edge_history.items(): st["active_log"].append(0)

    for l in range(num_layers):
        l_vec = per_layer[l].to(device).float()
        capture_threshold = torch.quantile(l_vec.abs(), GATE_CAPTURE_PERCENTILE / 100.0)
        active_mask = l_vec.abs() > capture_threshold
        active_indices = torch.where(active_mask)[0].tolist()
        if len(active_indices) < 2: continue
        x = _window_series(window_states, l, active_indices, device=device)
        corr_sub = _pearson_corr_mtx(x)
        sub_raw = l_vec[active_indices].unsqueeze(1)
        energy_sub = torch.mm(sub_raw, sub_raw.t())
        for ii, i in enumerate(active_indices):
            node_flips[(l, i)] = _track_polarity_flips(window_states, l, i)
            row_corr = corr_sub[ii]
            row_corr[ii] = 0.0
            _, top_corr_idxs = torch.topk(row_corr.abs(), min(TOP_K_LOGGING, len(row_corr) - 1))
            for jj in top_corr_idxs.tolist():
                j = active_indices[jj]
                p_val = float(row_corr[jj])
                if abs(p_val) < FILTER_MIN_PEARSON: continue
                val_i, val_j, e_val = float(l_vec[i]), float(l_vec[j]), float(energy_sub[ii, jj])
                locked = (np.sign(val_i) * np.sign(p_val) == np.sign(val_j))
                a, b = (i, j) if i < j else (j, i)
                key = f"{l}:{a}|{l}:{b}"
                if key in seen_edges_this_token: continue
                seen_edges_this_token.add(key)
                if key not in edge_history:
                    edge_history[key] = {"first_seen": token_counter, "active_log": deque([0]*min(PERSISTENCE_WINDOW, token_counter), maxlen=PERSISTENCE_WINDOW)}
                edge_history[key]["active_log"][-1] = 1
                persistence_ratio = sum(edge_history[key]["active_log"]) / max(1, len(edge_history[key]["active_log"]))
                s = edge_acc[key]
                s.update({"count": s["count"]+1, "energy_sum": s["energy_sum"]+abs(e_val), "pearson_sum": s["pearson_sum"]+abs(p_val), "locked": s["locked"]+int(locked), "act_min_sum": s["act_min_sum"]+min(abs(val_i), abs(val_j)), "persistence_ratio": persistence_ratio})
                node_hits[(l, i)] += 1; node_hits[(l, j)] += 1
                if p_val > 0: node_pos[(l, i)] += 1; node_pos[(l, j)] += 1
                else: node_neg[(l, i)] += 1; node_neg[(l, j)] += 1

    for l1 in range(num_layers - 1):
        l2 = l1 + 1
        v1, v2 = per_layer[l1].to(device).float(), per_layer[l2].to(device).float()
        th1, th2 = torch.quantile(v1.abs(), GATE_CAPTURE_PERCENTILE/100.0), torch.quantile(v2.abs(), GATE_CAPTURE_PERCENTILE/100.0)
        idx1 = torch.topk(v1.abs(), min(MAX_STRONG_DIMS, v1.size(0)))[1][v1[torch.topk(v1.abs(), min(MAX_STRONG_DIMS, v1.size(0)))[1]].abs() > th1].tolist()
        idx2 = torch.topk(v2.abs(), min(MAX_STRONG_DIMS, v2.size(0)))[1][v2[torch.topk(v2.abs(), min(MAX_STRONG_DIMS, v2.size(0)))[1]].abs() > th2].tolist()
        if not idx1 or not idx2: continue
        xa, xb = _window_series(window_states, l1, idx1, device=device), _window_series(window_states, l2, idx2, device=device)
        xa, xb = (xa - xa.mean(0))/(xa.std(0)+1e-8), (xb - xb.mean(0))/(xb.std(0)+1e-8)
        corr_mtx = (xa.T @ xb) / max(1, xa.size(0) - 1)
        energy_mtx = torch.outer(v1[idx1], v2[idx2])
        for i_idx, d1 in enumerate(idx1):
            node_flips[(l1, d1)] = _track_polarity_flips(window_states, l1, d1)
            for j_idx, d2 in enumerate(idx2):
                p_val = float(corr_mtx[i_idx, j_idx])
                if abs(p_val) < FILTER_MIN_PEARSON: continue
                val_i, val_j, e_val = float(v1[d1]), float(v2[d2]), float(energy_mtx[i_idx, j_idx])
                locked = (np.sign(val_i) * np.sign(p_val) == np.sign(val_j))
                key = f"{l1}:{d1}|{l2}:{d2}"
                if key in seen_edges_this_token: continue
                seen_edges_this_token.add(key)
                if key not in edge_history:
                    edge_history[key] = {"first_seen": token_counter, "active_log": deque([0]*min(PERSISTENCE_WINDOW, token_counter), maxlen=PERSISTENCE_WINDOW)}
                edge_history[key]["active_log"][-1] = 1
                persistence_ratio = sum(edge_history[key]["active_log"]) / max(1, len(edge_history[key]["active_log"]))
                s = edge_acc[key]
                s.update({"count": s["count"]+1, "energy_sum": s["energy_sum"]+abs(e_val), "pearson_sum": s["pearson_sum"]+abs(p_val), "locked": s["locked"]+int(locked), "act_min_sum": s["act_min_sum"]+min(abs(val_i), abs(val_j)), "type": "interlayer", "persistence_ratio": persistence_ratio})
                node_hits[(l1, d1)] += 1; node_hits[(l2, d2)] += 1
                if p_val > 0: node_pos[(l1, d1)] += 1; node_pos[(l2, d2)] += 1
                else: node_neg[(l1, d1)] += 1; node_neg[(l2, d2)] += 1
    return edge_acc, node_hits, node_pos, node_neg, node_flips

# =============================================================================
# DUAL RENDERING
# =============================================================================

def render_edges_and_neurons(edge_acc, node_hits, node_pos, node_neg, node_flips, per_layer, filter_core=False):
    scored = []
    for key, stats in edge_acc.items():
        touches_core = _touches_core(key, CORE_DIMS)
        if filter_core and touches_core: continue
        w = stats["count"]
        if w <= 0: continue
        score = _hybrid_score(stats["energy_sum"]/w, w, stats["locked"]/w, stats["pearson_sum"]/w) * (1.0 + 0.3 * stats["persistence_ratio"])
        scored.append((key, score, stats, touches_core))
    scored.sort(key=lambda x: x[1], reverse=True)
    edges_out, layer_counts = {}, defaultdict(int)
    for key, score, stats, touches_core in scored:
        if len(edges_out) >= MAX_RENDER_EDGES: break
        l_id = int(key.split("|")[0].split(":")[0])
        if layer_counts[l_id] >= MAX_EDGES_PER_LAYER: continue
        if (stats["act_min_sum"]/stats["count"]) < torch.quantile(per_layer[l_id].abs(), GATE_RENDER_PERCENTILE/100.0): continue
        edges_out[_edge_id_1idx(key)] = {"weight": int(stats["count"]), "energy": round(stats["energy_sum"]/stats["count"], 6), "pearson": round(stats["pearson_sum"]/stats["count"], 6), "lock_ratio": round(stats["locked"]/stats["count"], 4), "score": round(score, 6), "type": stats["type"], "persistence_ratio": round(stats["persistence_ratio"], 4), "touches_core": touches_core}
        layer_counts[l_id] += 1
    neurons_out = {_id_1idx(l, d): {"activation": round(float(per_layer[l][d]), 6), "hits": int(h), "pos_edges": int(node_pos.get((l,d),0)), "neg_edges": int(node_neg.get((l,d),0)), "polarity_flips": int(node_flips.get((l,d),0)), "is_core": (d in CORE_DIMS)} for (l,d), h in node_hits.items() if not (filter_core and d in CORE_DIMS)}
    return neurons_out, edges_out

# =============================================================================
# RUNNER
# =============================================================================

def run_probe(tokenizer, model, original_prompt, device, run_dir):
    # Apply the official chat template for Gemma
    chat = [
        {"role": "user", "content": f"{IDENTITY_PROMPT}\n\nQuestion: {original_prompt}"}
    ]
    # This creates the proper <start_of_turn>user...<end_of_turn><start_of_turn>model structure
    fletcher_prompt = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)

    tokens_full_dir, tokens_filtered_dir = run_dir / "tokens", run_dir / "tokens_filtered"
    for d in [tokens_full_dir, tokens_filtered_dir]: d.mkdir(parents=True, exist_ok=True)
    
    metadata = {"run_id": RUN_ID, "identity": "Helpful Assistant", "timestamp": now_iso(), "original_prompt": original_prompt, "injected_prompt": fletcher_prompt}
    window, edge_history = deque(maxlen=WINDOW_SIZE), {}
    input_ids = tokenizer(fletcher_prompt, return_tensors="pt")["input_ids"].to(device)
    
    gen = generate_with_hidden_states(
        model, 
        tokenizer, 
        input_ids, 
        MAX_NEW_TOKENS, 
        do_sample=DO_SAMPLE,
        top_p=TOP_P
    )
    per_layer, _ = forward_with_hidden_states(model, input_ids)
    window.append(per_layer)
    agg = _aggregate_window(list(window))
    edge_acc, node_hits, node_pos, node_neg, node_flips = compute_circuits(agg, list(window), device, edge_history, 0)
    
    for f, suffix in [(False, ""), (True, "_filtered")]:
        n, e = render_edges_and_neurons(edge_acc, node_hits, node_pos, node_neg, node_flips, agg, filter_core=f)
        with open((tokens_filtered_dir if f else tokens_full_dir) / "t0000_prompt.json", "w") as jf:
            json.dump({"meta": {"phase": "prompt", "text": "<PROMPT_END>"}, "neurons": n, "edges": e}, jf, indent=2)

    generated_text = ""
    for i, (tid, txt, pl) in enumerate(tqdm(gen, total=MAX_NEW_TOKENS, desc="Fletcher Probe")):
        generated_text += txt
        window.append(pl); agg = _aggregate_window(list(window))
        edge_acc, node_hits, node_pos, node_neg, node_flips = compute_circuits(agg, list(window), device, edge_history, i+1)
        for f in [False, True]:
            n, e = render_edges_and_neurons(edge_acc, node_hits, node_pos, node_neg, node_flips, agg, filter_core=f)
            fname = f"t{i+1:04d}_gen.json"
            with open((tokens_filtered_dir if f else tokens_full_dir) / fname, "w") as jf:
                json.dump({"meta": {"token": txt, "index": i+1}, "neurons": n, "edges": e}, jf, indent=2)
    
    metadata["response"] = generated_text
    with open(run_dir / "metadata.json", "w") as mf: json.dump(metadata, mf, indent=2)

def main():
    device = safe_device(); set_seed(SEED)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, dtype=torch.bfloat16, device_map="auto", trust_remote_code=True).eval()
    if tokenizer.pad_token_id is None: tokenizer.pad_token = tokenizer.eos_token
    
    from prompts import PROMPTS
    for cat, p_list in PROMPTS.items():
        for i, p in enumerate(p_list):
            run_dir = OUTPUT_ROOT / f"{RUN_ID}_{cat}_{i:02d}"
            run_dir.mkdir(parents=True, exist_ok=True)
            run_probe(tokenizer, model, p, device, run_dir)

if __name__ == "__main__": main()