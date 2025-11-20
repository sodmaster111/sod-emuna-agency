"""ORM model for registered Sanhedrin agents."""
from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Text
from sqlmodel import Field, SQLModel


class Agent(SQLModel, table=True):
    """Database representation of a Digital Sanhedrin agent."""

    __tablename__ = "agents"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    name: str = Field(nullable=False, index=True)
    role: str = Field(nullable=False)
    system_prompt: str = Field(sa_type=Text(), nullable=False)
    is_c_level: bool = Field(default=False, nullable=False)


__all__ = ["Agent"]
