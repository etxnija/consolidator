"""JWT authentication — register, login, and token verification.

Environment variables:
  JWT_SECRET   — signing secret (required in production)
  JWT_ALGORITHM — algorithm (default: HS256)
  JWT_EXPIRE_MINUTES — token TTL in minutes (default: 60*8 = 8 hours)
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

_SECRET = os.environ.get("JWT_SECRET", "change-me-in-production-do-not-use-default")
_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
_EXPIRE_MINUTES = int(os.environ.get("JWT_EXPIRE_MINUTES", str(60 * 8)))

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_bearer = HTTPBearer()

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    username: str
    password: str
    tenant_id: Optional[uuid.UUID] = None  # if None, a new tenant UUID is created


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUser(BaseModel):
    user_id: uuid.UUID
    username: str
    tenant_id: uuid.UUID

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def _verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


def _create_token(user_id: uuid.UUID, username: str, tenant_id: uuid.UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "username": username,
        "tenant_id": str(tenant_id),
        "exp": expire,
    }
    return jwt.encode(payload, _SECRET, algorithm=_ALGORITHM)


# ---------------------------------------------------------------------------
# FastAPI dependency — inject into protected routes
# ---------------------------------------------------------------------------

def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
) -> CurrentUser:
    """Verify the Bearer token and return the decoded user claims."""
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, _SECRET, algorithms=[_ALGORITHM])
        user_id = uuid.UUID(payload["sub"])
        username: str = payload["username"]
        tenant_id = uuid.UUID(payload["tenant_id"])
    except (JWTError, KeyError, ValueError):
        raise exc
    return CurrentUser(user_id=user_id, username=username, tenant_id=tenant_id)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def register(req: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Create a new user. Returns a JWT on success.

    If `tenant_id` is omitted a new tenant UUID is generated — this is the
    normal flow for the first user of a new group. Supply an existing
    `tenant_id` to add a second user to the same tenant.
    """
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username {req.username!r} is already taken",
        )

    tenant_id = req.tenant_id or uuid.uuid4()
    user = User(
        user_id=uuid.uuid4(),
        username=req.username,
        hashed_password=_hash_password(req.password),
        tenant_id=tenant_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = _create_token(user.user_id, user.username, user.tenant_id)
    return TokenResponse(access_token=token)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive a JWT",
)
def login(req: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Verify credentials and return a signed JWT."""
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not _verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = _create_token(user.user_id, user.username, user.tenant_id)
    return TokenResponse(access_token=token)
