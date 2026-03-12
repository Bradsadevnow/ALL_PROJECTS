import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from monolith_circuits import ForwardHookRig # Use your existing rig

class SteveGovernor:
    def __init__(self, model, stable_coords):
        self.model = model
        self.stable_coords = stable_coords # List of (layer, dim) from log_eval.py
        self.handles = []

    def stability_hook(self, layer_idx, target_dims):
        def hook(module, input, output):
            # THE EPOCH LOCK: Clamp high-centrality coordinates 
            # to their 'stability' bounds during generation.
            for dim in target_dims:
                # Example: prevent trajectory collapse by preventing zero-outs
                if torch.abs(output[..., dim]) < 0.1:
                    output[..., dim] *= 1.5 
            return output
        return hook

    def engage(self):
        # Group coords by layer for efficient hooking
        for layer_idx in range(28):
            targets = [d for l, d in self.stable_coords if l == layer_idx]
            if targets:
                h = self.model.model.layers[layer_idx].self_attn.o_proj.register_forward_hook(
                    self.stability_hook(layer_idx, targets)
                )
                self.handles.append(h)

# Logic to run the Agent with/without Steve goes here...