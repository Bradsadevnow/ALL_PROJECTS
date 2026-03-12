"""
RAG query API.

POST /query  { "question": "..." }
  → { "answer": "...", "sources": [{ "title": "...", "path": "...", "excerpt": "..." }] }

GET /health  → { "status": "ok", "chunks": <int> }
"""

import os
from pathlib import Path

import chromadb
from google import genai
from google.genai import types
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

CHROMA_PATH = Path(__file__).parent / "chroma"
EMBED_MODEL = "gemini-embedding-001"
GENERATION_MODEL = "gemini-2.0-flash"
TOP_K = 5

SYSTEM_PROMPT = """You are a knowledgeable guide to Brad Bates' AI research and projects at recursiveemotion.com.

Answer questions accurately and concisely based on the provided context. Focus on the technical substance.
If the context doesn't contain enough information to answer well, say so directly.
Do not make up details not present in the context.
Keep answers focused — 2-4 paragraphs unless a longer answer is clearly warranted."""

app = FastAPI(title="Recursive Emotion RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Module-level singletons (initialized on first use)
_collection = None
_genai_client: genai.Client | None = None


def get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=str(CHROMA_PATH))
        _collection = client.get_collection("portfolio")
    return _collection


def get_genai() -> genai.Client:
    global _genai_client
    if _genai_client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set")
        _genai_client = genai.Client(api_key=api_key)
    return _genai_client


class QueryRequest(BaseModel):
    question: str


class Source(BaseModel):
    title: str
    path: str
    excerpt: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]


@app.get("/health")
def health():
    try:
        col = get_collection()
        return {"status": "ok", "chunks": col.count()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question cannot be empty")
    if len(question) > 1000:
        raise HTTPException(status_code=400, detail="question too long (max 1000 chars)")

    ai = get_genai()
    collection = get_collection()

    # Embed the question
    q_embedding = ai.models.embed_content(
        model=EMBED_MODEL,
        contents=question,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    ).embeddings[0].values

    # Retrieve top-k chunks
    results = collection.query(
        query_embeddings=[q_embedding],
        n_results=TOP_K,
        include=["documents", "metadatas", "distances"],
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]

    # Build context block
    context_parts = []
    for i, (doc, meta) in enumerate(zip(docs, metas)):
        label = f"[{i+1}] {meta['source_title']}"
        if meta.get("header"):
            label += f" — {meta['header']}"
        context_parts.append(f"{label}\n{doc}")
    context = "\n\n---\n\n".join(context_parts)

    # Generate answer
    prompt = f"""{SYSTEM_PROMPT}

Context:
{context}

Question: {question}

Answer:"""

    response = ai.models.generate_content(model=GENERATION_MODEL, contents=prompt)
    answer = response.text.strip()

    # Deduplicate sources by path
    seen = set()
    sources = []
    for doc, meta in zip(docs, metas):
        path = meta["source_path"]
        if path not in seen:
            seen.add(path)
            excerpt = doc[:200].replace("\n", " ").strip()
            if len(doc) > 200:
                excerpt += "..."
            sources.append(Source(
                title=meta["source_title"],
                path=path,
                excerpt=excerpt,
            ))

    return QueryResponse(answer=answer, sources=sources)
