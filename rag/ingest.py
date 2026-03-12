"""
Ingest pipeline: chunk corpus docs → embed with text-embedding-004 → store in ChromaDB.

Run once locally (or in CI before docker build):
    cd rag && python ingest.py

The resulting chroma/ directory gets baked into the Docker image.
"""

import os
import re
import time
from pathlib import Path

import chromadb
from google import genai
from google.genai import types

from corpus import CORPUS_FILES

REPO_ROOT = Path(__file__).parent.parent
CHROMA_PATH = Path(__file__).parent / "chroma"
EMBED_MODEL = "text-embedding-004"
MAX_CHUNK_CHARS = 1800  # ~450 tokens, leaves room for overlap
CHUNK_OVERLAP_CHARS = 150


def make_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    return genai.Client(api_key=api_key, http_options={'api_version': 'v1'})


def load_file(rel_path: str) -> tuple[str, str]:
    """Return (title, content) for a corpus file."""
    path = REPO_ROOT / rel_path
    if not path.exists():
        print(f"  SKIP (not found): {rel_path}")
        return "", ""
    title = path.stem.replace("_", " ").replace("-", " ").title()
    return title, path.read_text(encoding="utf-8")


def split_markdown(text: str, source_title: str) -> list[dict]:
    """
    Split markdown into chunks. Strategy:
    1. Split on ## / ### headers to respect document structure.
    2. Further split any chunk that exceeds MAX_CHUNK_CHARS with a sliding window.
    Each chunk carries metadata: source_title, header_path, chunk_index.
    """
    # Split on lines that start with ## or ### (keep the header)
    header_re = re.compile(r"^#{2,3}\s+.+", re.MULTILINE)
    splits = header_re.split(text)
    headers = [""] + header_re.findall(text)

    raw_chunks = []
    for header, body in zip(headers, splits):
        section = (header + "\n" + body).strip()
        if not section:
            continue
        # Further split if too long
        if len(section) <= MAX_CHUNK_CHARS:
            raw_chunks.append((header.strip(), section))
        else:
            # Sliding window
            start = 0
            while start < len(section):
                end = start + MAX_CHUNK_CHARS
                raw_chunks.append((header.strip(), section[start:end]))
                start += MAX_CHUNK_CHARS - CHUNK_OVERLAP_CHARS

    chunks = []
    for i, (header, text_chunk) in enumerate(raw_chunks):
        if len(text_chunk.strip()) < 40:  # skip near-empty chunks
            continue
        chunks.append({
            "text": text_chunk.strip(),
            "source_title": source_title,
            "header": header,
            "chunk_index": i,
        })
    return chunks


def embed(client: genai.Client, texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """Embed a list of texts using text-embedding-004. Respects rate limits."""
    embeddings = []
    for i, text in enumerate(texts):
        result = client.models.embed_content(
            model=EMBED_MODEL,
            contents=text,
            config=types.EmbedContentConfig(task_type=task_type),
        )
        embeddings.append(result.embeddings[0].values)
        if (i + 1) % 10 == 0:
            time.sleep(0.5)  # gentle rate limiting
    return embeddings


def build_index():
    ai = make_client()

    client = chromadb.PersistentClient(path=str(CHROMA_PATH))

    # Fresh build each time
    try:
        client.delete_collection("portfolio")
    except Exception:
        pass
    collection = client.create_collection(
        name="portfolio",
        metadata={"hnsw:space": "cosine"},
    )

    all_chunks = []
    for rel_path in CORPUS_FILES:
        print(f"Loading: {rel_path}")
        title, content = load_file(rel_path)
        if not content:
            continue
        chunks = split_markdown(content, source_title=title or rel_path)
        for chunk in chunks:
            chunk["source_path"] = rel_path
        all_chunks.extend(chunks)
        print(f"  → {len(chunks)} chunks")

    print(f"\nTotal chunks: {len(all_chunks)}")
    print("Embedding...")

    texts = [c["text"] for c in all_chunks]
    embeddings = embed(ai, texts)

    ids = [f"chunk_{i}" for i in range(len(all_chunks))]
    metadatas = [
        {
            "source_title": c["source_title"],
            "source_path": c["source_path"],
            "header": c["header"],
            "chunk_index": c["chunk_index"],
        }
        for c in all_chunks
    ]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    print(f"Done. Index written to {CHROMA_PATH}")
    print(f"Collection size: {collection.count()} documents")


if __name__ == "__main__":
    build_index()
