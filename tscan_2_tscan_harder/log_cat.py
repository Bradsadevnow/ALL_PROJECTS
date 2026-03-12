import os
import json
from pathlib import Path
from collections import defaultdict

# Root of all your data
LOG_DIR = Path("runs")

# Threshold: Appearance count within a category
MIN_APPEARANCES = 5 

def scan_by_category():
    # Structure: category -> dim_id -> list of persistence_ratios
    cat_stats = defaultdict(lambda: defaultdict(list))
    # Structure: dim_id -> total hits across all categories
    total_hits = defaultdict(int)
    
    # Recursive search for token artifacts
    token_files = list(LOG_DIR.rglob("tokens_filtered/t*_gen.json"))
    
    if not token_files:
        print(f"ERROR: No files found in {LOG_DIR}")
        return

    print(f"🔍 Analyzing {len(token_files)} artifacts across categories...")

    for fpath in token_files:
        try:
            # Extract category from folder name (e.g., gemma3_..._A_baseline_00)
            run_id = fpath.parts[-3]
            # Assumes format: model_runID_category_index
            parts = run_id.split("_")
            # Pulling the category identifier (e.g., "A_baseline", "H_skills")
            cat_name = "_".join(parts[-2:-1]) 
            
            with open(fpath, "r") as f:
                data = json.load(f)
                edges = data.get("edges", {})
                
                for edge_key, stats in edges.items():
                    nodes = edge_key.split("|")
                    p_ratio = stats.get("persistence_ratio", 0)
                    
                    for node in nodes:
                        cat_stats[cat_name][node].append(p_ratio)
                        total_hits[node] += 1
        except Exception:
            continue

    # Identify Universal Backbone (Dimensions present in ALL found categories)
    all_found_cats = sorted(cat_stats.keys())
    
    # Sort dimensions by total hits for the leaderboard
    sorted_dims = sorted(total_hits.items(), key=lambda x: x[1], reverse=True)

    header = f"{'DIM (L:D)':<12} | {'TOTAL':<8} | " + " | ".join([f"{c:<12}" for c in all_found_cats])
    bar = "=" * len(header)
    sep = "-" * len(header)

    print("\n" + bar)
    print(header)
    print(sep)

    for dim, total in sorted_dims[:100]: # Expanded to top 100
        row = f"{dim:<12} | {total:<8} | "
        
        cat_values = []
        for cat in all_found_cats:
            scores = cat_stats[cat].get(dim, [])
            if len(scores) >= MIN_APPEARANCES:
                avg_p = sum(scores) / len(scores)
                cat_values.append(f"{avg_p:<12.4f}")
            else:
                cat_values.append(f"{'---':<12}")
        
        print(row + " | ".join(cat_values))

    print(bar)
    print(f"Note: '---' indicates dimension did not meet MIN_APPEARANCES ({MIN_APPEARANCES}) in that category.")

if __name__ == "__main__":
    scan_by_category()