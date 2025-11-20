"""Vector store utilities backed by PostgreSQL + pgvector."""
from __future__ import annotations

from functools import lru_cache
from typing import Iterable, List, Optional, Sequence

import litellm
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, text
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import Field, SQLModel, create_engine, select

from app.core.config import config
from app.core.engine import Engine


class TorahChunk(SQLModel, table=True):
    """Embeddable chunk of a Torah or halachic text."""

    __tablename__ = "torah_chunks"

    id: Optional[int] = Field(default=None, primary_key=True)
    reference: str = Field(index=True, nullable=False)
    book: str = Field(index=True, nullable=False)
    chunk_index: int = Field(default=0, nullable=False)
    content: str = Field(nullable=False)
    embedding: List[float] = Field(
        sa_column=Column(Vector(config.embedding_dimensions), nullable=False)
    )


def _create_engine():
    return create_engine(config.database_url, echo=False)


@lru_cache
def get_engine():
    """Return a shared SQLModel engine instance."""

    return _create_engine()


@lru_cache
def get_session_factory() -> sessionmaker:
    engine = get_engine()
    return sessionmaker(engine, class_=Session)


def ensure_vector_tables() -> None:
    """Create the pgvector extension and associated tables if missing."""

    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    SQLModel.metadata.create_all(engine)


def embed_texts(texts: Sequence[str]) -> List[List[float]]:
    """Generate embeddings for a sequence of texts using LiteLLM."""

    # Ensure LiteLLM is configured for the local Ollama/OpenAI endpoint.
    Engine()
    vectors: List[List[float]] = []
    for text in texts:
        result = litellm.embedding(model=config.embedding_model, input=text)
        vectors.append(result["data"][0]["embedding"])
    return vectors


def store_chunks(
    reference: str,
    book: str,
    chunks: Iterable[str],
    embeddings: Sequence[Sequence[float]],
) -> int:
    """Persist embedded chunks to the database.

    Returns the number of records inserted.
    """

    session_factory = get_session_factory()
    inserted = 0
    with session_factory() as session:
        for idx, (content, vector) in enumerate(zip(chunks, embeddings)):
            session.add(
                TorahChunk(
                    reference=reference,
                    book=book,
                    chunk_index=idx,
                    content=content,
                    embedding=list(vector),
                )
            )
            inserted += 1
        session.commit()
    return inserted


def search_halacha(query: str, limit: int = 5) -> List[TorahChunk]:
    """Return the most relevant halachic chunks for a given query."""

    query_embedding = embed_texts([query])[0]
    session_factory = get_session_factory()
    with session_factory() as session:
        stmt = (
            select(TorahChunk)
            .order_by(TorahChunk.embedding.l2_distance(query_embedding))
            .limit(limit)
        )
        return list(session.exec(stmt).all())


def chunk_passages(passages: Sequence[str], *, chunk_size: int = 400) -> List[str]:
    """Combine adjacent short passages into roughly equal sized chunks."""

    chunks: List[str] = []
    buffer: List[str] = []
    current_length = 0
    for passage in passages:
        words = passage.split()
        if current_length + len(words) > chunk_size and buffer:
            chunks.append(" ".join(buffer).strip())
            buffer = []
            current_length = 0
        buffer.append(passage)
        current_length += len(words)
    if buffer:
        chunks.append(" ".join(buffer).strip())
    return [chunk for chunk in chunks if chunk]


__all__ = [
    "TorahChunk",
    "ensure_vector_tables",
    "embed_texts",
    "store_chunks",
    "search_halacha",
    "chunk_passages",
]
