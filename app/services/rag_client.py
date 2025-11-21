"""Lightweight RAG utilities for Ollama + vector database workflows."""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Sequence

import httpx

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
VECTOR_DB_URL = os.getenv("VECTOR_DB_URL", "http://localhost:6333").rstrip("/")
RAG_MODEL_NAME = os.getenv("RAG_MODEL_NAME", "llama3.1:8b-instruct")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "nomic-embed-text")


async def embed_texts(texts: Sequence[str]) -> List[List[float]]:
    """Generate embeddings for a batch of texts using Ollama."""

    if not texts:
        return []

    url = f"{OLLAMA_BASE_URL}/api/embeddings"
    embeddings: list[list[float]] = []
    async with httpx.AsyncClient(timeout=60) as client:
        for text in texts:
            response = await client.post(url, json={"model": EMBEDDING_MODEL_NAME, "prompt": text})
            response.raise_for_status()
            payload = response.json()
            vector = payload.get("embedding")
            if not isinstance(vector, list):
                raise ValueError("Embedding response missing 'embedding' vector")
            embeddings.append(vector)
    return embeddings


async def _ensure_collection(client: httpx.AsyncClient, collection: str, vector_size: int) -> None:
    """Create the collection in Qdrant if it does not already exist."""

    info = await client.get(f"{VECTOR_DB_URL}/collections/{collection}")
    if info.status_code == 200:
        return
    if info.status_code != 404:
        info.raise_for_status()

    create_payload = {"vectors": {"size": vector_size, "distance": "Cosine"}}
    create = await client.put(f"{VECTOR_DB_URL}/collections/{collection}", json=create_payload)
    create.raise_for_status()


async def add_documents(collection: str, docs: Sequence[Dict[str, Any]]) -> None:
    """Embed documents and upsert them into the vector database."""

    if not docs:
        return

    texts = [doc["text"] for doc in docs]
    embeddings = await embed_texts(texts)
    vector_size = len(embeddings[0]) if embeddings else 0

    async with httpx.AsyncClient(timeout=60) as client:
        if vector_size:
            await _ensure_collection(client, collection, vector_size)

        points = []
        for doc, vector in zip(docs, embeddings):
            points.append(
                {
                    "id": doc.get("id"),
                    "vector": vector,
                    "payload": {"text": doc.get("text", ""), "meta": doc.get("meta", {})},
                }
            )

        response = await client.put(
            f"{VECTOR_DB_URL}/collections/{collection}/points",
            json={"points": points},
        )
        response.raise_for_status()


async def query(collection: str, question: str, top_k: int = 5) -> Dict[str, Any]:
    """Retrieve the top matching documents for a question."""

    question_embedding = await embed_texts([question])
    vector = question_embedding[0] if question_embedding else []

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{VECTOR_DB_URL}/collections/{collection}/points/search",
            json={
                "vector": vector,
                "limit": top_k,
                "with_payload": True,
                "with_vectors": False,
            },
        )
        response.raise_for_status()
        payload = response.json()

    results = []
    for point in payload.get("result", []):
        results.append(
            {
                "id": str(point.get("id")),
                "score": float(point.get("score", 0.0)),
                "text": point.get("payload", {}).get("text", ""),
                "meta": point.get("payload", {}).get("meta", {}),
            }
        )

    return {"matches": results}


async def rag_answer(collection: str, question: str, *, top_k: int = 5) -> Dict[str, Any]:
    """Perform retrieval-augmented generation via Ollama."""

    search = await query(collection, question, top_k=top_k)
    matches = search.get("matches", [])
    context_lines = [f"[{match['id']}] {match.get('text', '')}" for match in matches]
    context_block = "\n\n".join(context_lines) if context_lines else "No relevant context found."

    prompt_messages = [
        {
            "role": "system",
            "content": "You are the SOD internal assistant. Answer succinctly and cite provided sources.",
        },
        {
            "role": "user",
            "content": f"Context:\n{context_block}\n\nQuestion: {question}",
        },
    ]

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={"model": RAG_MODEL_NAME, "messages": prompt_messages, "stream": False},
        )
        response.raise_for_status()
        payload = response.json()

    answer_text = None
    if isinstance(payload.get("message"), dict):
        answer_text = payload["message"].get("content")
    elif isinstance(payload.get("choices"), list) and payload["choices"]:
        answer_text = payload["choices"][0].get("message", {}).get("content")
    answer = answer_text or "No answer generated."

    sources = [{"id": match["id"], "score": match.get("score", 0.0), "meta": match.get("meta", {})} for match in matches]
    return {"answer": answer, "sources": sources}


__all__ = [
    "add_documents",
    "embed_texts",
    "query",
    "rag_answer",
]
