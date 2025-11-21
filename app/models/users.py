"""User model for authentication and authorization."""
from __future__ import annotations

import uuid

from sqlalchemy import Column, String

from app.core.database import Base


class User(Base):
    """Persisted user account with role-based access control."""

    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="viewer")

    def __repr__(self) -> str:  # pragma: no cover - simple repr
        return f"User(id={self.id}, username={self.username}, role={self.role})"
