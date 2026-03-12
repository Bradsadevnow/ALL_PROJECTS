"""
Quick script to list available models and check embedding support.
Run: cd rag && python list_models.py
"""

import os
from google import genai

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY not set")

client = genai.Client(api_key=api_key)

print("=== Models supporting embedContent ===")
for m in client.models.list():
    supported = getattr(m, "supported_actions", None) or getattr(m, "supported_generation_methods", [])
    name = m.name
    if "embed" in name.lower() or "embed" in str(supported).lower():
        print(f"  {name}  |  {supported}")

print("\n=== Quick embed test ===")
result = client.models.embed_content(
    model="gemini-embedding-001",
    contents="hello world",
)
print(f"  Vector length: {len(result.embeddings[0].values)}")
print("  OK")
