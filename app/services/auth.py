"""Authentication helpers for password hashing and JWT issuance."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.core.config import settings
from app.models.users import User

ALGORITHM = "HS256"
security_scheme = HTTPBearer(auto_error=False)


def _get_secret_key() -> str:
    if not settings.SECRET_KEY:
        raise RuntimeError("SECRET_KEY is not configured")
    return settings.SECRET_KEY


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Validate a plain-text password against a bcrypt hash."""

    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))


def hash_password(password: str) -> str:
    """Generate a bcrypt hash for a password."""

    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Issue a signed JWT for the supplied payload."""

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, _get_secret_key(), algorithm=ALGORITHM)


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    """Retrieve a user by username."""

    result = await session.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def authenticate_user(session: AsyncSession, username: str, password: str) -> User | None:
    """Validate credentials and return the user when successful."""

    user = await get_user_by_username(session, username)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


async def verify_token(session: AsyncSession, token: str) -> User:
    """Decode a JWT and resolve the associated user."""

    try:
        payload = jwt.decode(token, _get_secret_key(), algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    except JWTError as exc:  # pragma: no cover - exercised in runtime
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    user = await get_user_by_username(session, username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    """FastAPI dependency ensuring the request is authenticated."""

    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return await verify_token(session, credentials.credentials)


def require_role(required_role: str):
    """Dependency factory enforcing a minimum role."""

    async def dependency(user: User = Depends(get_current_user)) -> User:
        role_order = {"viewer": 1, "operator": 2, "admin": 3}
        if role_order.get(user.role, 0) < role_order.get(required_role, 0):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return dependency
