"""
RAG query API.

POST /query  { "question": "..." }
  → { "answer": "...", "sources": [{ "title": "...", "path": "...", "excerpt": "..." }] }

GET /health  → { "status": "ok", "chunks": <int> }
"""

import os
from pathlib import Path

import chromadb
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

CHROMA_PATH = Path(__file__).parent / "chroma"
EMBED_MODEL = "models/text-embedding-004"
GENERATION_MODEL = "gemini-1.5-flash-latest"
TOP_K = 5

SYSTEM_PROMPT = """You are a knowledgeable guide to Brad Bates' AI research and projects at recursiveemotion.com.

Answer questions accurately and concisely based on the provided context. Focus on the technical substance.
If the context doesn't contain enough information to answer well, say so directly.
Do not make up details not present in the context.
Keep answers focused — 2-4 paragraphs unless a longer answer is clearly warranted."""

app = FastAPI(title="Recursive Emotion RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://recursiveemotion.com",
        "https://www.recursiveemotion.com",
        "http://localhost:5173",
        "http://localhost:4173",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Module-level singletons (initialized on startup)
_collection = None
_api_configured = False


def get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=str(CHROMA_PATH))
        _collection = client.get_collection("portfolio")
    return _collection


def ensure_genai():
    global _api_configured
    if not _api_configured:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set")
        genai.configure(api_key=api_key)
        _api_configured = True


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

    ensure_genai()
    collection = get_collection()

    # Embed the question
    q_embedding = genai.embed_content(
        model=EMBED_MODEL,
        content=question,
        task_type="retrieval_query",
    )["embedding"]

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

    model = genai.GenerativeModel(GENERATION_MODEL)
    response = model.generate_content(prompt)
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
