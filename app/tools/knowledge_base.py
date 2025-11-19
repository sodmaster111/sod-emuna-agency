"""RAG integration with PGVector."""
from __future__ import annotations

from typing import List, Tuple

from pgvector.sqlalchemy import Vector
from sqlalchemy import Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Session, mapped_column

from app.core.config import config


class Base(DeclarativeBase):
    pass


class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id: int = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: str = mapped_column(String, nullable=False)
    content: str = mapped_column(String, nullable=False)
    embedding: Vector = mapped_column(Vector(1536))


def _engine():
    return create_engine(config.postgres_url)


def init_db() -> None:
    engine = _engine()
    Base.metadata.create_all(engine)


def add_document(source: str, content: str, embedding: List[float]) -> int:
    engine = _engine()
    with Session(engine) as session:
        doc = DocumentEmbedding(source=source, content=content, embedding=embedding)
        session.add(doc)
        session.commit()
        session.refresh(doc)
        return doc.id


def similarity_search(embedding: List[float], limit: int = 5) -> List[Tuple[str, str]]:
    engine = _engine()
    with Session(engine) as session:
        stmt = (
            select(DocumentEmbedding.source, DocumentEmbedding.content)
            .order_by(DocumentEmbedding.embedding.l2_distance(embedding))
            .limit(limit)
        )
        return [(row[0], row[1]) for row in session.execute(stmt).all()]
