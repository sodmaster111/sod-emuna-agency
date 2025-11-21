"""Endpoints for internal retrieval-augmented generation workflows.

Integration tips:
- When importing Torah or liturgy content, push documents into the "torah" collection.
- Corporate DNA and Pinkas summaries belong in the "sod-internal" collection.
- Future dashboard UI can target these endpoints to surface answers + source snippets.
"""
from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, constr

from app.services import rag_client

router = APIRouter(prefix="/rag", tags=["rag"])


class DocumentInput(BaseModel):
    id: constr(strip_whitespace=True, min_length=1)
    text: constr(strip_whitespace=True, min_length=1)
    meta: Dict[str, Any] = Field(default_factory=dict)


class IndexRequest(BaseModel):
    collection: constr(strip_whitespace=True, min_length=1)
    documents: List[DocumentInput]


class QueryRequest(BaseModel):
    collection: constr(strip_whitespace=True, min_length=1)
    question: constr(strip_whitespace=True, min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class Source(BaseModel):
    id: str
    score: float
    meta: Dict[str, Any] = Field(default_factory=dict)


class RAGAnswer(BaseModel):
    answer: str
    sources: List[Source]


@router.post("/index")
async def index_documents(payload: IndexRequest) -> Dict[str, Any]:
    """Ingest internal documents into a RAG collection.

    NOTE: Keep this endpoint restricted to administrative or internal callers.
    """

    if not payload.documents:
        raise HTTPException(status_code=400, detail="No documents provided")

    await rag_client.add_documents(
        collection=payload.collection,
        docs=[doc.model_dump() for doc in payload.documents],
    )
    return {"status": "indexed", "count": len(payload.documents)}


@router.post("/query", response_model=RAGAnswer)
async def query_rag(payload: QueryRequest) -> RAGAnswer:
    """Query the local RAG stack for an internal answer.

    This should also remain admin/internal only until hardened.
    """

    result = await rag_client.rag_answer(
        collection=payload.collection, question=payload.question, top_k=payload.top_k
    )
    sources = [Source(**source) for source in result.get("sources", [])]
    return RAGAnswer(answer=result.get("answer", ""), sources=sources)
