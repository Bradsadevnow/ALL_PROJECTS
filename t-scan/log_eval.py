import os
import json
import glob
from collections import defaultdict

# --- CONFIGURATION ---
LOG_DIR = "./runs"

# NOISE FILTER: 
# A dimension must appear at least this many times WITHIN A SINGLE GROUP 
# to be considered a "valid partner" for that group.
MIN_APPEARANCES = 5 

def scan_universals():
    # Structure: group_name -> set of valid dims
    group_valid_dims = defaultdict(set)
    
    # Structure: dim -> list of groups it appeared in (for final reporting)
    dim_to_groups_map = defaultdict(list)

    # 1. SCAN AND AGGREGATE COUNTS
    # Structure: group_name -> dim_id -> raw_count
    raw_group_counts = defaultdict(lambda: defaultdict(int))
    
    files = glob.glob(f"{LOG_DIR}/*/constellation/layer_*.jsonl")
    print(f"Scanning {len(files)} layer logs...")

    if not files:
        print(f"ERROR: No files found in {LOG_DIR}")
        return

    for fpath in files:
        try:
            run_id = fpath.split("/")[-3]
            group_parts = run_id.split("_")[0:2] 
            group_name = "_".join(group_parts)
        except Exception:
            group_name = "unknown_group"

        with open(fpath, "r") as f:
            for line in f:
                try:
                    row = json.loads(line)
                    if not row.get("hero", {}).get("active", False):
                        continue

                    for link in row.get("links", []):
                        dim_id = link["dim"]
                        raw_group_counts[group_name][dim_id] += 1
                        
                except json.JSONDecodeError:
                    continue

    # 2. APPLY NOISE FILTER & DETERMINE PRESENCE
    print("\n--- Group Analysis (Noise Filter Applied) ---")
    all_groups = sorted(raw_group_counts.keys())
    
    for group in all_groups:
        counts = raw_group_counts[group]
        valid_dims = {d for d, c in counts.items() if c >= MIN_APPEARANCES}
        
        group_valid_dims[group] = valid_dims
        
        for d in valid_dims:
            dim_to_groups_map[d].append(group)
            
        print(f"Group '{group}': Found {len(valid_dims)} valid partners (Threshold: {MIN_APPEARANCES}+ hits)")

    # 3. INTERSECTION ANALYSIS
    total_groups = len(all_groups)
    universal_dims = []
    near_miss_dims = [] 

    for dim, groups_seen in dim_to_groups_map.items():
        if len(groups_seen) == total_groups:
            universal_dims.append(dim)
        elif len(groups_seen) == total_groups - 1:
            near_miss_dims.append(dim)

    # 4. REPORT (SORTED BY HITS)
    print("\n" + "="*50)
    print(f"THE UNIVERSAL CIRCUIT (Present in {total_groups}/{total_groups} Groups)")
    print("="*50)
    
    if not universal_dims:
        print("No dimensions survived the strict intersection.")
    else:
        # COLLECT HITS FIRST
        ranked_universals = []
        for dim in universal_dims:
            total_hits = sum(raw_group_counts[g][dim] for g in all_groups)
            ranked_universals.append((dim, total_hits))
        
        # SORT BY HITS (Descending)
        ranked_universals.sort(key=lambda x: x[1], reverse=True)

        for dim, hits in ranked_universals:
            print(f"DIM {dim:<4} | Total Hits: {hits:<6} | Groups: ALL")

    # NEAR MISSES REPORT (OPTIONAL)
    if not universal_dims and near_miss_dims:
        print("\n" + "-"*50)
        print(f"NEAR MISSES (Present in {total_groups-1}/{total_groups} Groups)")
        print("-" * 50)
        
        # Sort near misses by ID (or you could sort by hits here too)
        near_miss_dims.sort()
        for dim in near_miss_dims:
            missing = set(all_groups) - set(dim_to_groups_map[dim])
            print(f"DIM {dim:<4} | Missing from: {list(missing)}")

if __name__ == "__main__":
    scan_universals()