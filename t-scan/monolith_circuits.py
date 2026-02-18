#!/usr/bin/env python3
"""
BRAIN MONOLITH — LLaMA-3B WINDOWED PROBE (PER-TOKEN, LAYER-AWARE)

DUAL-RENDER PIPELINE:
- Computes circuits once
- Renders twice: full topology + core-filtered topology
- Outputs to separate folders for comparison
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

MODEL_PATH = "./models/llama_3b"
RUN_ID = "llama3b_windowed_probe"
OUTPUT_ROOT = Path("./runs")

MAX_NEW_TOKENS = 64
DO_SAMPLE = False
TOP_P = 1.0
SEED = 0

WINDOW_SIZE = 25
WINDOW_DECAY = 0.7

CORE_DIMS_ARE_1INDEXED = False
CORE_DIMS = {3039, 1043, 221, 103, 769, 1830, 2336}
if CORE_DIMS_ARE_1INDEXED:
    CORE_DIMS = {d-1 for d in CORE_DIMS}  # convert to 0-index


CORE_EDGE_BONUS = 1.0

GATE_CAPTURE_PERCENTILE = 95  # top 5% of activations per layer
GATE_RENDER_PERCENTILE = 97   # top 3% for final rendering
# --- PATCH 2: Sliding-window persistence ---
PERSISTENCE_WINDOW = 20


FILTER_MIN_PEARSON = 0.03
TOP_K_LOGGING = 40

MAX_RENDER_EDGES = 2000
MAX_EDGES_PER_LAYER = 150

MAX_STRONG_DIMS = 200
MAX_WEAK_CONSISTENT_DIMS = 50
CONSISTENCY_THRESHOLD = 2.0

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
def generate_with_hidden_states(model, tokenizer, input_ids, max_new_tokens, do_sample=False, top_p=1.0):
    past = None
    cur = input_ids

    out = model(input_ids=cur, use_cache=True, output_hidden_states=True, past_key_values=past)
    past = out.past_key_values
    logits = out.logits[:, -1, :]

    for _ in range(max_new_tokens):
        if do_sample:
            probs = torch.softmax(logits, dim=-1)
            sorted_probs, sorted_idx = torch.sort(probs, descending=True)
            cum = torch.cumsum(sorted_probs, dim=-1)
            mask = cum > top_p
            mask[..., 0] = False
            sorted_probs[mask] = 0.0
            sorted_probs = sorted_probs / (sorted_probs.sum(dim=-1, keepdim=True) + 1e-12)
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
    if touches_core:
        base *= (1.0 + CORE_EDGE_BONUS)
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


def _layer_normalize(vec):
    return (vec - vec.mean()) / (vec.std() + 1e-8)


# --- PATCH 1: Dead-zone polarity (ignore float noise near zero) ---
FLIP_EPSILON = 1e-3

def _track_polarity_flips(window_states, layer, dim):
    if len(window_states) < 2:
        return 0

    activations = [s[layer][dim].item() for s in window_states]
    signs = []

    for a in activations:
        if a > FLIP_EPSILON:
            signs.append(1)
        elif a < -FLIP_EPSILON:
            signs.append(-1)
        # else: ignore tiny jitter

    if len(signs) < 2:
        return 0

    return sum(1 for i in range(len(signs)-1) if signs[i] != signs[i+1])



def _touches_core(edge_key: str, core_dims_set: set[int]) -> bool:
    for ep in edge_key.split("|"):
        if ":" not in ep:
            continue
        _, d_str = ep.split(":")
        if int(d_str) in core_dims_set:
            return True
    return False

def _id_1idx(layer0: int, dim0: int) -> str:
    """Convert neuron coordinates to 1-indexed ID"""
    return f"{layer0+1}:{dim0+1}"

def _edge_id_1idx(edge_key: str) -> str:
    """Convert edge key from 0-indexed to 1-indexed"""
    left, right = edge_key.split("|")
    l1, d1 = map(int, left.split(":"))
    l2, d2 = map(int, right.split(":"))
    return f"{l1+1}:{d1+1}|{l2+1}:{d2+1}"

def _window_series(window_states, layer, dims, device):
    """
    Returns tensor shape [W, K] where W=len(window_states), K=len(dims)
    Each column is a dim's activation across the window.
    """
    W = len(window_states)
    K = len(dims)
    x = torch.empty((W, K), device=device, dtype=torch.float32)
    for t, s in enumerate(window_states):
        v = s[layer].to(device).float()
        x[t] = v[dims]
    return x

def _pearson_corr_mtx(x):
    """
    x: [W, K]
    returns corr: [K, K] Pearson correlation across time (W)
    """
    x = x - x.mean(dim=0, keepdim=True)
    denom = x.std(dim=0, unbiased=False, keepdim=True) + 1e-8
    x = x / denom
    # correlation = (x^T x) / (W-1) but scale doesn't matter for ranking; keep stable:
    corr = (x.T @ x) / max(1, x.size(0) - 1)
    corr = corr.clamp(-1.0, 1.0)
    return corr



# =============================================================================
# CIRCUIT COMPUTATION (NO FILTERING - COMPUTES EVERYTHING)
# =============================================================================

def compute_circuits(per_layer, window_states, device, edge_history, token_counter):
    """
    Computes ALL circuits without filtering.
    Returns raw edge_acc and node stats for downstream filtering.
    """

    # --- PATCH 3: Minimum sample guard ---
    MIN_CORR_SAMPLES = WINDOW_SIZE
    if len(window_states) < MIN_CORR_SAMPLES:
        return {}, {}, {}, {}, {}

    num_layers = len(per_layer)

    edge_acc = defaultdict(lambda: {
        "count": 0,
        "locked": 0,
        "energy_sum": 0.0,
        "pearson_sum": 0.0,
        "act_min_sum": 0.0,
        "type": "horizontal",
        "persistence_ratio": 0.0,
    })


    node_hits = defaultdict(int)
    node_pos = defaultdict(int)
    node_neg = defaultdict(int)
    node_flips = defaultdict(int)

    seen_edges_this_token = set()

    # Track misses for edges we already know about (temporal fairness)
    for k, st in edge_history.items():
        st["active_log"].append(0)


    # -----------------------------
    # INTRA-LAYER (HORIZONTAL)
    # -----------------------------
    for l in range(num_layers):
        l_vec = per_layer[l].to(device).float()
        
        # Compute threshold for THIS layer
        capture_threshold = torch.quantile(l_vec.abs(), GATE_CAPTURE_PERCENTILE / 100.0)
        
        # Get top dimensions above threshold
        active_mask = l_vec.abs() > capture_threshold
        active_indices = torch.where(active_mask)[0].tolist()

        if len(active_indices) < 2:
            continue

        # Windowed Pearson over time for these dims
        x = _window_series(window_states, l, active_indices, device=device)  # [W, K]
        corr_sub = _pearson_corr_mtx(x)                                      # [K, K]

        # Keep your "energy" concept as instantaneous product on the aggregated vector
        sub_raw = l_vec[active_indices].unsqueeze(1)                         # [K, 1]
        energy_sub = torch.mm(sub_raw, sub_raw.t())                          # [K, K]


        for ii, i in enumerate(active_indices):
            node_flips[(l, i)] = _track_polarity_flips(window_states, l, i)

            row_corr = corr_sub[ii]
            row_corr[ii] = 0.0

            _, top_corr_idxs = torch.topk(row_corr.abs(), min(TOP_K_LOGGING, len(row_corr) - 1))

            for jj in top_corr_idxs.tolist():
                j = active_indices[jj]
                if i == j:
                    continue

                p_val = float(row_corr[jj])
                if abs(p_val) < FILTER_MIN_PEARSON:
                    continue

                val_i = float(l_vec[i])
                val_j = float(l_vec[j])
                e_val = float(energy_sub[ii, jj])

                locked = (np.sign(val_i) * np.sign(p_val) == np.sign(val_j))

                a, b = (i, j) if i < j else (j, i)
                key = f"{l}:{a}|{l}:{b}"

                if key in seen_edges_this_token:
                    continue
                seen_edges_this_token.add(key)

                if key not in edge_history:
                    edge_history[key] = {
                        "first_seen": token_counter,
                        "active_log": deque([0]*min(PERSISTENCE_WINDOW, token_counter), maxlen=PERSISTENCE_WINDOW),
                    }

                # Mark this token as active (overwrite the last appended miss)
                if len(edge_history[key]["active_log"]) == 0:
                    edge_history[key]["active_log"].append(1)
                else:
                    edge_history[key]["active_log"][-1] = 1


                first_seen = edge_history[key]["first_seen"]
                windows_active = sum(edge_history[key]["active_log"])
                persistence_ratio = windows_active / max(1, len(edge_history[key]["active_log"]))


                s = edge_acc[key]
                s["count"] += 1
                s["energy_sum"] += abs(e_val)
                s["pearson_sum"] += abs(p_val)
                s["locked"] += int(locked)
                s["act_min_sum"] += min(abs(val_i), abs(val_j))
                s["type"] = "horizontal"
                s["windows_active"] = windows_active
                s["first_seen"] = first_seen
                s["persistence_ratio"] = persistence_ratio

                # ---- FIX: track node participation ----
                node_hits[(l, i)] += 1
                node_hits[(l, j)] += 1

                if p_val > 0:
                    node_pos[(l, i)] += 1
                    node_pos[(l, j)] += 1
                else:
                    node_neg[(l, i)] += 1
                    node_neg[(l, j)] += 1

    # -----------------------------
    # INTER-LAYER (ADJACENT)
    # -----------------------------
    for l1 in range(num_layers - 1):
        l2 = l1 + 1
        v1 = per_layer[l1].to(device).float()
        v2 = per_layer[l2].to(device).float()
        
        # Compute percentile thresholds for each layer
        threshold_l1 = torch.quantile(v1.abs(), GATE_CAPTURE_PERCENTILE / 100.0)
        threshold_l2 = torch.quantile(v2.abs(), GATE_CAPTURE_PERCENTILE / 100.0)

        _, idx1 = torch.topk(v1.abs(), min(MAX_STRONG_DIMS, v1.size(0)))
        idx1 = idx1[v1[idx1].abs() > threshold_l1].tolist()
        _, idx2 = torch.topk(v2.abs(), min(MAX_STRONG_DIMS, v2.size(0)))
        idx2 = idx2[v2[idx2].abs() > threshold_l2].tolist()

        if not idx1 or not idx2:
            continue

        a_vec = v1[idx1]
        b_vec = v2[idx2]

        # Windowed Pearson between layer l1 dims and layer l2 dims across time
        xa = _window_series(window_states, l1, idx1, device=device)   # [W, K1]
        xb = _window_series(window_states, l2, idx2, device=device)   # [W, K2]

        xa = (xa - xa.mean(dim=0, keepdim=True)) / (xa.std(dim=0, unbiased=False, keepdim=True) + 1e-8)
        xb = (xb - xb.mean(dim=0, keepdim=True)) / (xb.std(dim=0, unbiased=False, keepdim=True) + 1e-8)

        corr_mtx = (xa.T @ xb) / max(1, xa.size(0) - 1)               # [K1, K2]
        corr_mtx = corr_mtx.clamp(-1.0, 1.0)

        # Keep "energy" as instantaneous outer product on the aggregated vector
        energy_mtx = torch.outer(a_vec, b_vec)                        # [K1, K2]

        for i_idx, d1 in enumerate(idx1):
            node_flips[(l1, d1)] = _track_polarity_flips(window_states, l1, d1)
            val_i = float(v1[d1])

            for j_idx, d2 in enumerate(idx2):
                p_val = float(corr_mtx[i_idx, j_idx])
                if abs(p_val) < FILTER_MIN_PEARSON:
                    continue

                val_j = float(v2[d2])
                e_val = float(energy_mtx[i_idx, j_idx])

                locked = (np.sign(val_i) * np.sign(p_val) == np.sign(val_j))

                key = f"{l1}:{d1}|{l2}:{d2}"

                if key in seen_edges_this_token:
                    continue
                seen_edges_this_token.add(key)

                if key not in edge_history:
                    edge_history[key] = {
                        "first_seen": token_counter,
                        "active_log": deque([0]*min(PERSISTENCE_WINDOW, token_counter), maxlen=PERSISTENCE_WINDOW),
                    }

                # Mark this token as active (overwrite the last appended miss)
                if len(edge_history[key]["active_log"]) == 0:
                    edge_history[key]["active_log"].append(1)
                else:
                    edge_history[key]["active_log"][-1] = 1



                first_seen = edge_history[key]["first_seen"]
                windows_active = sum(edge_history[key]["active_log"])
                persistence_ratio = windows_active / max(1, len(edge_history[key]["active_log"]))



                s = edge_acc[key]
                s["count"] += 1
                s["energy_sum"] += abs(e_val)
                s["pearson_sum"] += abs(p_val)
                s["locked"] += int(locked)
                s["act_min_sum"] += min(abs(val_i), abs(val_j))
                s["type"] = "interlayer"
                s["windows_active"] = windows_active
                s["first_seen"] = first_seen
                s["persistence_ratio"] = persistence_ratio

                # ---- FIX: track node participation ----
                node_hits[(l1, d1)] += 1
                node_hits[(l2, d2)] += 1

                if p_val > 0:
                    node_pos[(l1, d1)] += 1
                    node_pos[(l2, d2)] += 1
                else:
                    node_neg[(l1, d1)] += 1
                    node_neg[(l2, d2)] += 1

    return edge_acc, node_hits, node_pos, node_neg, node_flips


# =============================================================================
# DUAL RENDERING: FULL + FILTERED
# =============================================================================

def render_edges_and_neurons(
    edge_acc, 
    node_hits, 
    node_pos, 
    node_neg, 
    node_flips, 
    per_layer,
    filter_core: bool = False
):
    """
    Takes raw circuit data and renders it with optional core filtering.
    
    filter_core=False: Include everything, flag core dims
    filter_core=True: Exclude core dims entirely
    
    IMPORTANT:
    - NO core bonus in scoring
    - FULL vs FILTERED differ ONLY by filtering
    """
    
    scored = []
    for key, stats in edge_acc.items():
        touches_core = _touches_core(key, CORE_DIMS)
        if filter_core and touches_core:
            continue

        w = stats["count"]
        if w <= 0:
            continue

        energy_avg = stats["energy_sum"] / w
        pearson_avg = stats["pearson_sum"] / w
        lock_ratio = stats["locked"] / w

        # ---- NO CORE BONUS ----
        score = _hybrid_score(energy_avg, w, lock_ratio, pearson_avg, touches_core=False)
        score *= (1.0 + 0.3 * stats["persistence_ratio"])

        scored.append((key, score, stats, touches_core))

    scored.sort(key=lambda x: x[1], reverse=True)

    edges_out = {}
    layer_counts = defaultdict(int)

    for key, score, stats, touches_core in scored:
        if len(edges_out) >= MAX_RENDER_EDGES:
            break

        left, _ = key.split("|")
        layer_id = int(left.split(":")[0])
        
        if layer_counts[layer_id] >= MAX_EDGES_PER_LAYER:
            continue
        
        # Compute act_min_avg FIRST
        w = stats["count"]
        act_min_avg = stats["act_min_sum"] / w
        
        # Then compute layer-specific threshold and check
        layer_vec = per_layer[layer_id]
        render_threshold = torch.quantile(layer_vec.abs(), GATE_RENDER_PERCENTILE / 100.0)
        
        if act_min_avg < render_threshold:
            continue

        out_key = _edge_id_1idx(key)

        edges_out[out_key] = {
            "weight": int(w),
            "energy": round(stats["energy_sum"] / w, 6),
            "pearson": round(stats["pearson_sum"] / w, 6),
            "lock_ratio": round(stats["locked"] / w, 4),
            "score": round(score, 6),
            "type": stats["type"],
            "persistence_ratio": round(stats["persistence_ratio"], 4),
            "windows_active": int(stats["windows_active"]),
            "touches_core": touches_core,
        }

        layer_counts[layer_id] += 1

    # -----------------------------
    # NEURON OUTPUT
    # -----------------------------
    neurons_out = {}
    for (l, d), hits in node_hits.items():
        is_core = d in CORE_DIMS
        if filter_core and is_core:
            continue

        act = float(per_layer[l][d])
        flips = int(node_flips.get((l, d), 0))

        neurons_out[_id_1idx(l, d)] = {
            "activation": round(act, 6),
            "hits": int(hits),
            "pos_edges": int(node_pos.get((l, d), 0)),
            "neg_edges": int(node_neg.get((l, d), 0)),
            "polarity_flips": flips,
            "is_core": is_core,
        }

    return neurons_out, edges_out

# =============================================================================
# RUNNER
# =============================================================================

def run_probe(tokenizer, model, prompt, device, run_dir):
    assert isinstance(prompt, str), f"Expected string, got {type(prompt)}"
    tokens_full_dir = run_dir / "tokens"
    tokens_filtered_dir = run_dir / "tokens_filtered"
    tokens_full_dir.mkdir(parents=True, exist_ok=True)
    tokens_filtered_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "run_id": RUN_ID,
        "model_path": MODEL_PATH,
        "timestamp": now_iso(),
        "device": device,
        "seed": SEED,
        "prompt": prompt,
        "window_size": WINDOW_SIZE,
        "window_decay": WINDOW_DECAY,
        "gate_capture_percentile": GATE_CAPTURE_PERCENTILE,
        "gate_render_percentile": GATE_RENDER_PERCENTILE,
        "core_dims": sorted(list(CORE_DIMS)),
        "tokens_full": [],
        "tokens_filtered": [],
        "generated_text": ""
    }

    window = deque(maxlen=WINDOW_SIZE)
    edge_history = {}

    inputs = tokenizer(prompt, return_tensors="pt")
    input_ids = inputs["input_ids"].to(device)

    per_layer, _ = forward_with_hidden_states(model, input_ids)
    window.append(per_layer)

    agg = _aggregate_window(list(window))
    edge_acc, node_hits, node_pos, node_neg, node_flips = compute_circuits(
        agg, list(window), device, edge_history, 0
    )

    # DUAL RENDER
    neurons_full, edges_full = render_edges_and_neurons(
        edge_acc, node_hits, node_pos, node_neg, node_flips, agg, filter_core=False
    )
    neurons_filtered, edges_filtered = render_edges_and_neurons(
        edge_acc, node_hits, node_pos, node_neg, node_flips, agg, filter_core=True
    )

    # Write full
    artifact_full = {
        "meta": {"phase": "prompt", "token_index": 0, "token_text": "<PROMPT_END>"},
        "neurons": neurons_full,
        "edges": edges_full
    }
    with open(tokens_full_dir / "t0000_prompt.json", "w") as f:
        json.dump(artifact_full, f, indent=2)

    # Write filtered
    artifact_filtered = {
        "meta": {"phase": "prompt", "token_index": 0, "token_text": "<PROMPT_END>"},
        "neurons": neurons_filtered,
        "edges": edges_filtered
    }
    with open(tokens_filtered_dir / "t0000_prompt.json", "w") as f:
        json.dump(artifact_filtered, f, indent=2)

    metadata["tokens_full"].append({
        "index": 0,
        "phase": "prompt",
        "token_text": "<PROMPT_END>",
        "file": "tokens/t0000_prompt.json"
    })
    metadata["tokens_filtered"].append({
        "index": 0,
        "phase": "prompt",
        "token_text": "<PROMPT_END>",
        "file": "tokens_filtered/t0000_prompt.json"
    })

    # GENERATION
    gen = generate_with_hidden_states(model, tokenizer, input_ids, MAX_NEW_TOKENS, DO_SAMPLE, TOP_P)
    token_counter = 1
    generated = []

    for tok_id, tok_text, per_layer in tqdm(gen, total=MAX_NEW_TOKENS, desc="Probing", unit="tok"):
        generated.append(tok_text)
        text_so_far = "".join(generated)


        window.append(per_layer)
        agg = _aggregate_window(list(window))
        edge_acc, node_hits, node_pos, node_neg, node_flips = compute_circuits(
            agg, list(window), device, edge_history, token_counter
        )

        # DUAL RENDER
        neurons_full, edges_full = render_edges_and_neurons(
            edge_acc, node_hits, node_pos, node_neg, node_flips, agg, filter_core=False
        )
        neurons_filtered, edges_filtered = render_edges_and_neurons(
            edge_acc, node_hits, node_pos, node_neg, node_flips, agg, filter_core=True
        )

        # Write full
        artifact_full = {
            "meta": {
                "phase": "generation",
                "token_index": token_counter,
                "token_id": tok_id,
                "token_text": tok_text,
                "text_so_far": text_so_far
            },
            "neurons": neurons_full,
            "edges": edges_full
        }

        fname = f"t{token_counter:04d}_gen.json"
        with open(tokens_full_dir / fname, "w") as f:
            json.dump(artifact_full, f, indent=2)

        # Write filtered
        artifact_filtered = {
            "meta": {
                "phase": "generation",
                "token_index": token_counter,
                "token_id": tok_id,
                "token_text": tok_text,
                "text_so_far": text_so_far
            },
            "neurons": neurons_filtered,
            "edges": edges_filtered
        }

        with open(tokens_filtered_dir / fname, "w") as f:
            json.dump(artifact_filtered, f, indent=2)

        metadata["tokens_full"].append({
            "index": token_counter,
            "phase": "generation",
            "token_text": tok_text,
            "text_so_far": text_so_far,
            "file": f"tokens/{fname}"
        })

        metadata["tokens_filtered"].append({
            "index": token_counter,
            "phase": "generation",
            "token_text": tok_text,
            "text_so_far": text_so_far,
            "file": f"tokens_filtered/{fname}"
        })


        token_counter += 1

        final_text = "".join(generated)
        metadata["generated_text"] = final_text
        metadata["response_text"] = final_text

        with open(run_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)



def main():
    device = safe_device()
    print(f"[monolith] device={device}")
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

    OUTPUT_ROOT = Path("./runs")

    from fMRI.prompts import PROMPTS

    for category, prompt_list in PROMPTS.items():
        print(f"\n=== CATEGORY: {category} ===")

        for i, prompt in enumerate(prompt_list):
            print(f"Running: {prompt}")

            run_dir = OUTPUT_ROOT / f"{RUN_ID}_{category}_{i:02d}"
            run_dir.mkdir(parents=True, exist_ok=True)

            run_probe(tokenizer, model, prompt, device, run_dir)


if __name__ == "__main__":
    main()