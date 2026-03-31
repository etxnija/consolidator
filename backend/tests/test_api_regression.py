"""Regression tests for the Consolidator API.

Covers JWT authentication and multi-tenancy isolation.

Run from the ``rig/`` directory:
    python -m pytest backend/tests/test_api_regression.py -v

How Python paths work here
--------------------------
``ingestion/app.py`` uses relative imports (``from ..database import ...``),
which means the ``backend/`` directory is the package root.  Tests import
``from ingestion.app import app`` — so ``rig/backend/`` must be on sys.path.
We add it explicitly at module load time so the test file is self-contained.

SQLite / JSONB workaround
--------------------------
``models.py`` imports ``JSONB`` from ``sqlalchemy.dialects.postgresql``.
SQLite does not understand JSONB; its ``create_all`` would raise a
``CompileError``.  We patch ``sqlalchemy.dialects.postgresql.JSONB`` to
``sqlalchemy.types.JSON`` *before* importing any backend module.

The PostgreSQL-specific trigger DDL in ``models.py`` is already wrapped with
``execute_if(dialect="postgresql")`` and is silently skipped on SQLite.
"""

from __future__ import annotations

import pathlib
import sys

# ---------------------------------------------------------------------------
# Ensure rig/backend/ is on sys.path so that ``ingestion``, ``auth``,
# ``database``, ``models``, etc. are importable as top-level packages.
# ---------------------------------------------------------------------------

_BACKEND_DIR = str(pathlib.Path(__file__).parent.parent)
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

# ---------------------------------------------------------------------------
# Patch JSONB → JSON BEFORE importing any backend module.
# ---------------------------------------------------------------------------

import sqlalchemy.dialects.postgresql as _pg_dialect  # noqa: E402
from sqlalchemy.types import JSON as _JSON  # noqa: E402

_pg_dialect.JSONB = _JSON  # type: ignore[attr-defined]

# ---------------------------------------------------------------------------
# Now import backend modules (safe after the patch above).
# ---------------------------------------------------------------------------

import uuid  # noqa: E402
from typing import Generator  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

# ``ingestion.app`` resolves to rig/backend/ingestion/app.py
from ingestion.app import app  # noqa: E402
# ``database`` resolves to rig/backend/database.py
from database import Base, get_db  # noqa: E402

# ---------------------------------------------------------------------------
# SQLite in-memory engine and session factory
# ---------------------------------------------------------------------------

_SQLITE_URL = "sqlite:///:memory:"

_test_engine = create_engine(
    _SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

_TestingSessionLocal = sessionmaker(
    bind=_test_engine,
    autocommit=False,
    autoflush=False,
)

# Create all tables once at import time; the autouse fixture below drops and
# recreates them between tests for full isolation.
Base.metadata.create_all(bind=_test_engine)


def _override_get_db() -> Generator:
    """FastAPI dependency override that yields a SQLite test session."""
    db = _TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_db():
    """Drop and recreate all tables between tests for full isolation."""
    Base.metadata.drop_all(bind=_test_engine)
    Base.metadata.create_all(bind=_test_engine)
    yield


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app, raise_server_exceptions=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_auth_token(client: TestClient, username: str, password: str) -> str:
    """Register the user (if not yet registered) and return a JWT token.

    Falls back to login if the username is already taken (409).
    """
    resp = client.post(
        "/auth/register",
        json={"username": username, "password": password},
    )
    if resp.status_code == 409:
        # Already registered — just log in.
        resp = client.post(
            "/auth/login",
            json={"username": username, "password": password},
        )
    assert resp.status_code in (200, 201), (
        f"Auth failed for {username!r}: {resp.status_code} {resp.text}"
    )
    return resp.json()["access_token"]


def auth_headers(token: str) -> dict:
    """Return an Authorization header dict for the given Bearer token."""
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Auth tests
# ---------------------------------------------------------------------------


def test_register_happy_path(client: TestClient) -> None:
    resp = client.post(
        "/auth/register",
        json={"username": "alice", "password": "s3cr3t"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 10


def test_register_duplicate_username_409(client: TestClient) -> None:
    payload = {"username": "bob", "password": "password1"}
    first = client.post("/auth/register", json=payload)
    assert first.status_code == 201

    second = client.post("/auth/register", json=payload)
    assert second.status_code == 409


def test_login_happy_path(client: TestClient) -> None:
    client.post("/auth/register", json={"username": "carol", "password": "hunter2"})

    resp = client.post(
        "/auth/login",
        json={"username": "carol", "password": "hunter2"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password_401(client: TestClient) -> None:
    client.post("/auth/register", json={"username": "dave", "password": "correct"})

    resp = client.post(
        "/auth/login",
        json={"username": "dave", "password": "wrong"},
    )
    assert resp.status_code == 401


def test_unauthenticated_entities_401(client: TestClient) -> None:
    resp = client.get("/entities")
    assert resp.status_code == 401


def test_unauthenticated_periods_401(client: TestClient) -> None:
    resp = client.get("/periods")
    assert resp.status_code == 401


def test_malformed_token_401(client: TestClient) -> None:
    resp = client.get(
        "/entities",
        headers={"Authorization": "Bearer garbage.token.here"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Tenant isolation tests
# ---------------------------------------------------------------------------


def test_two_users_get_different_tenant_ids(client: TestClient) -> None:
    import base64
    import json as _json

    resp_a = client.post("/auth/register", json={"username": "user_a", "password": "pw"})
    resp_b = client.post("/auth/register", json={"username": "user_b", "password": "pw"})
    assert resp_a.status_code == 201
    assert resp_b.status_code == 201

    def _decode_tenant(token: str) -> str:
        payload_b64 = token.split(".")[1]
        # Restore base64 padding.
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += "=" * padding
        payload = _json.loads(base64.urlsafe_b64decode(payload_b64))
        return payload["tenant_id"]

    tenant_a = _decode_tenant(resp_a.json()["access_token"])
    tenant_b = _decode_tenant(resp_b.json()["access_token"])
    assert tenant_a != tenant_b, (
        "Two independent users must receive different tenant_ids"
    )


def test_entity_isolation(client: TestClient) -> None:
    token_a = get_auth_token(client, "tenant_a_user", "pw")
    token_b = get_auth_token(client, "tenant_b_user", "pw")

    # Tenant A creates an entity.
    create_resp = client.post(
        "/entities",
        json={"name": "Tenant A Corp"},
        headers=auth_headers(token_a),
    )
    assert create_resp.status_code == 201

    # Tenant B lists entities — must be empty.
    list_resp = client.get("/entities", headers=auth_headers(token_b))
    assert list_resp.status_code == 200
    assert list_resp.json() == [], "Tenant B should not see Tenant A's entities"


def test_period_isolation(client: TestClient) -> None:
    token_a = get_auth_token(client, "period_tenant_a", "pw")
    token_b = get_auth_token(client, "period_tenant_b", "pw")

    # Tenant A creates a period.
    create_resp = client.post(
        "/periods",
        json={
            "label": "FY-2024",
            "period_start": "2024-01-01",
            "period_end": "2024-12-31",
        },
        headers=auth_headers(token_a),
    )
    assert create_resp.status_code == 201

    # Tenant B lists periods — must be empty.
    list_resp = client.get("/periods", headers=auth_headers(token_b))
    assert list_resp.status_code == 200
    assert list_resp.json() == [], "Tenant B should not see Tenant A's periods"


def test_consolidate_cross_tenant_404(client: TestClient) -> None:
    token_a = get_auth_token(client, "consol_tenant_a", "pw")
    token_b = get_auth_token(client, "consol_tenant_b", "pw")

    # Tenant A creates a period.
    period_resp = client.post(
        "/periods",
        json={
            "label": "Q1-2024",
            "period_start": "2024-01-01",
            "period_end": "2024-03-31",
        },
        headers=auth_headers(token_a),
    )
    assert period_resp.status_code == 201
    period_id = period_resp.json()["period_id"]

    # Tenant B attempts to consolidate using Tenant A's period_id — must get 404.
    consol_resp = client.post(
        f"/consolidate/{period_id}",
        headers=auth_headers(token_b),
    )
    assert consol_resp.status_code == 404, (
        f"Cross-tenant consolidation must return 404, "
        f"got {consol_resp.status_code}: {consol_resp.text}"
    )


# ---------------------------------------------------------------------------
# Workflow tests (auth-aware)
# ---------------------------------------------------------------------------


def test_entity_crud(client: TestClient) -> None:
    token = get_auth_token(client, "entity_crud_user", "pw")
    headers = auth_headers(token)

    # Create entity.
    create_resp = client.post(
        "/entities",
        json={"name": "Acme Holdings"},
        headers=headers,
    )
    assert create_resp.status_code == 201
    entity = create_resp.json()
    assert entity["name"] == "Acme Holdings"
    assert "entity_id" in entity
    assert entity["parent_entity_id"] is None
    assert entity["ownership_pct"] is None

    # List entities — should contain exactly the one we created.
    list_resp = client.get("/entities", headers=headers)
    assert list_resp.status_code == 200
    entities = list_resp.json()
    assert len(entities) == 1
    assert entities[0]["name"] == "Acme Holdings"
    assert entities[0]["entity_id"] == entity["entity_id"]


def test_period_crud(client: TestClient) -> None:
    token = get_auth_token(client, "period_crud_user", "pw")
    headers = auth_headers(token)

    # Create period.
    create_resp = client.post(
        "/periods",
        json={
            "label": "FY-2025",
            "period_start": "2025-01-01",
            "period_end": "2025-12-31",
        },
        headers=headers,
    )
    assert create_resp.status_code == 201
    period = create_resp.json()
    assert period["label"] == "FY-2025"
    assert period["period_start"] == "2025-01-01"
    assert period["period_end"] == "2025-12-31"
    assert period["status"] == "open"
    assert "period_id" in period

    # List periods — should contain exactly the one we created.
    list_resp = client.get("/periods", headers=headers)
    assert list_resp.status_code == 200
    periods = list_resp.json()
    assert len(periods) == 1
    assert periods[0]["label"] == "FY-2025"
    assert periods[0]["period_id"] == period["period_id"]


def test_period_label_conflict(client: TestClient) -> None:
    token = get_auth_token(client, "period_conflict_user", "pw")
    headers = auth_headers(token)

    payload = {
        "label": "CONFLICT-2024",
        "period_start": "2024-01-01",
        "period_end": "2024-12-31",
    }

    first = client.post("/periods", json=payload, headers=headers)
    assert first.status_code == 201

    second = client.post("/periods", json=payload, headers=headers)
    # The router raises 409 for a duplicate label within the same tenant.
    assert second.status_code in (409, 422), (
        f"Duplicate label should return 409 or 422, "
        f"got {second.status_code}: {second.text}"
    )
