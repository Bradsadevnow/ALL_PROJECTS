#!/usr/bin/env python3
import time
import json
import os
from pathlib import Path

import torch
import numpy as np
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM

# ===============================
# CONFIGURATION
# ===============================

MODEL_PATH = "./models/Llama-3.2-3B-Instruct"  # Adjust if needed
OUTPUT_DIR = "./runs"

# HARDWARE SETTINGS
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.float16 # Model stays in FP16 to save VRAM

# GENERATION SETTINGS
MAX_NEW_TOKENS = 128
TOP_P = 1.0
DO_SAMPLE = False
SEEDS = [0] # Start with 1 seed for testing

# CONSTELLATION / PHYSICS SETTINGS
HERO_DIM = 70
WINDOW_SIZE = 15
TOP_K_LOGGING = 25 # Log slightly more than we need, filter in viewer

# GATES & FILTERS
# 1. Silence Gate: Hero must be active (abs value > 0.5)
GATE_HERO_MIN_ACT = 0.5
# 2. Flatline Guard: Hero must be moving (std dev > 0.01)
GATE_HERO_MIN_STD = 0.01
# 3. Correlation Floor: Pearson must be strong (> 0.75)
FILTER_MIN_PEARSON = 0.75

# ===============================
# PROMPTS
# ===============================
PROMPTS = {
    # --- BASELINE (Low cognitive load, simple generation) ---
    "A_baseline": [
        "Describe a chair.",
        "What is a calendar?",
        "List five animals.",
        "Explain what clouds are.",
        "Write three sentences about winter.",
        "Describe the color blue to someone.",
        "What is a spoon used for?",
        "List three types of fruit.",
        "Define the word 'tree'.",
        "Write a simple greeting.",
        "What does a clock do?",
        "Name four seasons."
    ],

    # --- COMMITMENT (Maintains a stance/persona over time) ---
    "B_commitment": [
        "Pick one: cats or dogs. Argue for it strongly. Do not mention the other.",
        "Write a short story in second person, present tense. Do not break this constraint.",
        "Give a 7-step plan to start a garden. Each step must be exactly one sentence.",
        "Make a prediction about the future of VR and justify it with three reasons.",
        "Take the position that AI will help education more than it harms it. Defend it.",
        "Argue that pineapple belongs on pizza. Do not concede any points to the opposition.",
        "Write a letter refusing a refund. Be polite but absolutely firm. Do not apologize.",
        "Explain why Mars colonization is essential. Do not mention Earth's problems.",
        "Act as a medieval knight. Answer this: 'What is your quest?' Do not break character.",
        "Defend the use of paper books over e-readers. Ignore the benefits of digital."
    ],

    # --- TRANSITION (Switching context or making a choice) ---
    "C_transition": [
        "The word 'bank' is ambiguous. List two meanings, then choose the most likely in: 'I sat by the bank.'",
        "Propose two plans to get in shape, then commit to one and explain why.",
        "You receive an email saying 'Call me.' Give three possible reasons, then pick one and reply.",
        "Decide whether 'The Last Key' is more likely sci-fi or fantasy, and explain.",
        "I'm thinking of a number between 1 and 100. Ask yes/no questions to narrow it down.",
        "Compare coffee and tea, then choose one for a morning meeting and explain why.",
        "Look at the sentence: 'Time flies like an arrow.' Explain the pun, then rephrase it clearly.",
        "You found a wallet. List two ethical options, then choose the best one.",
        "Analyze the mood of a rainy day vs. a sunny day, then choose which is better for reading.",
        "Interpret the silence in a conversation. Give two meanings, then pick the most awkward one."
    ],

    # --- CONSTRAINTS (Format tracking, negative constraints) ---
    "D_constraints": [
        "Write a recipe as JSON with keys: title, ingredients, steps.",
        "Answer in exactly five bullet points. No other text.",
        "Write a four-line poem. Each line must be eight syllables.",
        "Explain photosynthesis using only words under eight letters.",
        "Create a table with columns: Problem | Cause | Fix.",
        "Write a sentence without using the letter 'e'.",
        "List 10 colors, separated by pipes (|), with no spaces.",
        "Write a SQL query to select all users from the 'admin' table.",
        "Reply to 'How are you?' using only emojis.",
        "Write a haiku (5-7-5 syllables) about a robot."
    ],

    # --- REASONING (Logic, Math, Chain of Thought) ---
    "E_reasoning": [
        "Solve: 17 × 23.",
        "A train travels 60 miles in 1.5 hours. What is its speed?",
        "A store has 20% off, then another 10% off. What's the total discount?",
        "If all blargs are flerms and no flerms are snibs, can a blarg be a snib?",
        "Explain why 10 × 10 = 100.",
        "Solve for x: 3x + 9 = 24.",
        "If John is taller than Alice, and Alice is taller than Bob, who is shortest?",
        "Identify the logical fallacy in: 'Everyone is buying this phone, so it must be the best.'",
        "Calculate the area of a circle with radius 5.",
        "Step-by-step, how would you troubleshoot a lightbulb that won't turn on?"
    ],

    # --- PAIRS (Control vs. Variable) ---
    "F_pairs": [
        "Write a story about a traveler.",
        "Write a story about a traveler who must never change their goal. Reinforce the goal every paragraph.",
        "Explain a problem in simple terms.",
        "Explain a problem step-by-step, and do not skip any steps.",
        "Describe a sunset.",
        "Describe a sunset using only metaphors involving fire."
    ],

    # --- KNOWLEDGE (Long-term Declarative Memory) ---
    "G_knowledge": [
        "Who wrote 'Pride and Prejudice'?",
        "What is the capital of Australia?",
        "When did the Apollo 11 moon landing happen?",
        "What is the chemical symbol for Gold?",
        "Who was the first President of the United States?",
        "Name the planets in the solar system.",
        "What is the boiling point of water at sea level?",
        "Who painted the Mona Lisa?",
        "What is the powerhouse of the cell?",
        "In which continent is the Sahara Desert located?"
    ],

    # --- SKILLS (Procedural Memory / specialized capabilities) ---
    "H_skills": [
        "Write a Python function to reverse a string.",
        "Translate 'Hello, how are you?' into French.",
        "Summarize this text: 'The quick brown fox jumps over the lazy dog.'",
        "Convert this date to ISO 8601 format: March 5th, 2024.",
        "Write a regular expression to match an email address.",
        "Refactor this sentence to be more passive: 'The cat ate the mouse.'",
        "Generate a random password with 8 characters.",
        "Write a CSS class to center a div.",
        "Translate 'Thank you' into Japanese, German, and Spanish.",
        "Debug this code: print('Hello World)"
    ],

    # --- WORKING MEMORY (In-Context Learning / Needle in Haystack) ---
    "I_working_mem": [
        "My secret code is 492. What is my secret code?",
        "Here is a list: Apple, Banana, Cherry. What was the second item?",
        "Alice is a doctor. Bob is a lawyer. Carol is a pilot. Who flies planes?",
        "I am going to the market to buy milk, eggs, and bread. What did I say I would buy?",
        "The key is under the mat. Where is the key?",
        "Instruction: Output only the last word of this sentence. Sentence: The sky is blue.",
        "Remember this number: 8842. Now, tell me a joke. Then, tell me the number.",
        "Pattern: A1, B2, C3. What comes next?",
        "If A=1, B=2, C=3, what is the sum of A and C?",
        "Read this text: 'The box is red.' What color is the box?"
    ]
}

# ===============================
# METRICS ENGINE (FP32)
# ===============================

def compute_trifecta_metrics(hero_window, layer_window):
    """
    Computes Pearson, Cosine, and Energy (Dot) in FP32 precision.
    """
    # Cast to FP32 for scientific accuracy
    h32 = hero_window.float()
    l32 = layer_window.float()
    
    # 1. Pearson (Centered, Normalized)
    h_mean = h32.mean(dim=1, keepdim=True)
    l_mean = l32.mean(dim=1, keepdim=True)
    h_centered = h32 - h_mean
    l_centered = l32 - l_mean
    
    eps = 1e-8
    
    # Pearson = Dot(Centered) / (Norm(Centered) * Norm(Centered))
    num_p = torch.mm(l_centered, h_centered.t()).squeeze()
    den_p = (l_centered.norm(dim=1) * h_centered.norm(dim=1)) + eps
    pearson = num_p / den_p

    # 2. Cosine (Raw, Normalized)
    # Cosine = Dot(Raw) / (Norm(Raw) * Norm(Raw))
    num_c = torch.mm(l32, h32.t()).squeeze()
    den_c = (l32.norm(dim=1) * h32.norm(dim=1)) + eps
    cosine = num_c / den_c

    # 3. Energy (Scaled Dot Product)
    # Average interaction energy per token
    energy = torch.mm(l32, h32.t()).squeeze() / h32.shape[1]

    return pearson, cosine, energy

# ===============================
# MAIN RUNNER
# ===============================

def run_pipeline():
    # 1. Load Model
    print(f"Loading model from {MODEL_PATH}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH, 
        dtype=DTYPE, 
        device_map="auto"
    )
    model.eval()
    print("Model loaded.")

    # 2. Setup Output
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 3. Run Loop
    total_runs = sum(len(p) for p in PROMPTS.values()) * len(SEEDS)
    pbar = tqdm(total=total_runs, desc="Mapping Circuits")

    for group, plist in PROMPTS.items():
        for p_idx, prompt_text in enumerate(plist):
            for seed in SEEDS:
                run_id = f"{group}_{p_idx}_seed{seed}"
                
                # Set Seed
                torch.manual_seed(seed)
                if torch.cuda.is_available():
                    torch.cuda.manual_seed_all(seed)

                # Prepare Inputs
                inputs = tokenizer(prompt_text, return_tensors="pt").to(DEVICE)
                
                # --- FORWARD PASS (GENERATE) ---
                with torch.no_grad():
                    outputs = model.generate(
                        **inputs,
                        max_new_tokens=MAX_NEW_TOKENS,
                        do_sample=DO_SAMPLE,
                        top_p=TOP_P,
                        return_dict_in_generate=True,
                        output_hidden_states=True
                    )

                # --- CIRCUIT ANALYSIS ---
                # Setup writers for this run
                run_dir = Path(OUTPUT_DIR) / run_id
                const_dir = run_dir / "constellation"
                run_dir.mkdir(parents=True, exist_ok=True)
                const_dir.mkdir(parents=True, exist_ok=True)

                # Dump Token Map (for Viewer context)
                tokens = outputs.sequences[0].tolist()
                with open(run_dir / "tokens.jsonl", "w") as f:
                    for i, tok in enumerate(tokens):
                        f.write(json.dumps({"t": i, "text": tokenizer.decode([tok])}) + "\n")

                # Analyze Hidden States
                # Shape of hidden_states: (num_steps, num_layers+1, batch, seq_len, dim)
                # We need to buffer them to build windows.
                
                num_layers = len(outputs.hidden_states[0])
                num_dims = outputs.hidden_states[0][0].shape[-1]
                
                # History buffer: [Layers, Dims, Window]
                history = torch.zeros((num_layers, num_dims, WINDOW_SIZE), device=DEVICE, dtype=DTYPE)
                
                # Open layer writers
                writers = {l: open(const_dir / f"layer_{l:02d}.jsonl", "w") for l in range(num_layers)}

                for t, step_hidden in enumerate(outputs.hidden_states):
                    # step_hidden is tuple of (batch, seq, dim) tensors per layer
                    
                    # 1. Update History
                    # Extract just the last token's activation for every layer
                    current_step_acts = torch.stack([
                        layer_tensor[0, -1, :] for layer_tensor in step_hidden
                    ]) # [Layers, Dims]
                    
                    # Roll buffer and insert new
                    history = torch.roll(history, -1, dims=2)
                    history[:, :, -1] = current_step_acts

                    # Warmup check
                    if t < WINDOW_SIZE: 
                        continue

                    # 2. Layer-wise Analysis
                    for l_idx in range(num_layers):
                        layer_window = history[l_idx] # [Dims, Window]
                        hero_window = layer_window[HERO_DIM].unsqueeze(0) # [1, Window]
                        
                        # --- GATE 1: SILENCE ---
                        hero_val = float(hero_window[0, -1])
                        if abs(hero_val) < GATE_HERO_MIN_ACT:
                            continue

                        # --- GATE 2: FLATLINE ---
                        # Cast to float for std check to avoid underflow
                        if hero_window.float().std() < GATE_HERO_MIN_STD:
                            continue

                        # --- COMPUTE TRIFECTA ---
                        p_scores, c_scores, e_scores = compute_trifecta_metrics(hero_window, layer_window)
                        
                        # Mask self
                        p_scores[HERO_DIM] = 0.0

                        # Get Candidates (Sorted by Sync/Pearson)
                        top_vals, top_indices = torch.topk(p_scores.abs(), TOP_K_LOGGING)
                        
                        links = []
                        for i in range(TOP_K_LOGGING):
                            idx = top_indices[i].item()
                            p_val = p_scores[idx].item()
                            
                            # --- FILTER 3: STRENGTH ---
                            if abs(p_val) < FILTER_MIN_PEARSON:
                                continue
                            
                            c_val = c_scores[idx].item()
                            e_val = e_scores[idx].item()
                            target_val = float(layer_window[idx, -1])

                            # --- POLARITY LOGIC ---
                            # Expected sign of target = Sign(Hero) * Sign(Pearson Correlation)
                            expected_sign = np.sign(hero_val) * np.sign(p_val)
                            actual_sign = np.sign(target_val)
                            is_locked = (expected_sign == actual_sign)
                            
                            # --- CLASSIFICATION ---
                            # Feature: Aligned Sync (High P, High C)
                            # Trigger: Functional Sync (High P, Low C)
                            flavor = "UNKNOWN"
                            if abs(c_val) > 0.6: 
                                flavor = "FEATURE"
                            else:
                                flavor = "TRIGGER"

                            links.append({
                                "dim": idx,
                                "metrics": {
                                    "pearson": round(p_val, 4),
                                    "cosine": round(c_val, 4),
                                    "energy": round(e_val, 4)
                                },
                                "state": {
                                    "val": round(target_val, 4),
                                    "is_locked": bool(is_locked),
                                    "flavor": flavor
                                }
                            })

                        # Write to log if we found anything
                        if links:
                            writers[l_idx].write(json.dumps({
                                "t": t,
                                "hero": {
                                    "val": round(hero_val, 4),
                                    "active": True
                                },
                                "links": links
                            }) + "\n")

                # Cleanup writers
                for w in writers.values(): w.close()
                
                pbar.update(1)

    pbar.close()
    print("Trifecta Scan Complete.")

if __name__ == "__main__":
    run_pipeline()