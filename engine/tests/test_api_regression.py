"""Full API regression suite for the Consolidator backend.

Covers:
  1. Entity CRUD — create, list, tree, patch, delete, duplicate-name guard
  2. Period CRUD — create, list, lock, reject ingestion on locked period
  3. Ingestion — happy path, unknown entity, locked period, duplicate entity name
  4. Consolidation — run on period with data, verify eliminations_created > 0
  5. Report — balance sheet, income statement, eliminations summary present
  6. Delete entity blocked when ledger entries exist

Uses FastAPI TestClient with an in-memory SQLite database.
The engine HTTP call in consolidation is mocked via unittest.mock.patch.

NOTE: There is a known design conflict on Postgres: the _block_unsafe_ddl hook
in backend/database.py blocks DELETE on entity_metadata at the SQLAlchemy event
layer, which would prevent DELETE /entities/{entity_id} from succeeding.  These
tests exercise the endpoint logic through SQLite (where the hook is not
registered) and pass.  A separate bead tracks the Postgres incompatibility.
"""

from __future__ import annotations

import io
import uuid
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# ---------------------------------------------------------------------------
# SQLite compatibility: teach SQLite compiler to render JSONB as JSON.
# The models use sqlalchemy.dialects.postgresql.JSONB for the metadata_ column;
# SQLite has no native JSONB but stores JSON as text.
# ---------------------------------------------------------------------------

def _visit_JSONB(self, type_, **kw):  # noqa: N802
    return "JSON"

SQLiteTypeCompiler.visit_JSONB = _visit_JSONB  # type: ignore[attr-defined]

# ---------------------------------------------------------------------------
# Test database engine — SQLite in-memory, no immutability hook
# ---------------------------------------------------------------------------

_SQLITE_URL = "sqlite://"

# StaticPool forces all connections to share the same in-memory database,
# which is required for SQLite in-memory DBs (otherwise each connection
# gets its own fresh empty database).
_test_engine = create_engine(
    _SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create tables once for the whole module.
def _init_db() -> None:
    from backend.database import Base  # noqa: F401 — registers Base
    from backend.models import EntityMetadata, LedgerEntry, ReportingPeriod  # noqa: F401
    Base.metadata.create_all(bind=_test_engine)

_init_db()

_TestingSessionLocal = sessionmaker(
    bind=_test_engine, autocommit=False, autoflush=False
)


def _new_session() -> Session:
    return _TestingSessionLocal()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def db() -> Generator[Session, None, None]:
    """Yield a fresh session; always rollback so tests are isolated."""
    session = _new_session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture()
def client(db: Session):
    """TestClient with SQLite DB override and mocked engine HTTP calls.

    Three patches are required:
    1. app.dependency_overrides[get_db]  — overrides the FastAPI DI injection
       used by all router handlers.
    2. backend.ingestion.database.get_db — overrides the direct get_db() call
       inside commit_entries (not injected via FastAPI DI).
    3. backend.ingestion.app.engine     — overrides the SQLAlchemy Engine used
       by the lifespan create_all() call so it targets SQLite, not Postgres.
    """
    from backend.ingestion.app import app
    from backend.database import get_db

    def _override_get_db():
        yield db

    app.dependency_overrides[get_db] = _override_get_db

    with patch("backend.ingestion.database.get_db", lambda: iter([db])), \
         patch("backend.ingestion.app.engine", _test_engine):
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c

    app.dependency_overrides.clear()


# GCoA map uses entity names SUBS_01 through SUBS_10.
# Each subsidiary has its own local account number range.
# Offsets: SUBS_0X uses account codes ending in X-1.
#   SUBS_01: 1000 → 1100, 4000 → 4100
#   SUBS_02: 1001 → 1100, 4001 → 4100
#   SUBS_03: 1002 → 1100, 4002 → 4100
#   SUBS_04: 1003 → 1100
_SUBS01_CSV = b"account_code,amount,description\n1000,50000.00,Cash\n4000,100000.00,Revenue\n"
_SUBS02_CSV = b"account_code,amount,description\n1001,50000.00,Cash\n4001,100000.00,Revenue\n"
_SUBS03_CSV = b"account_code,amount,description\n1002,50000.00,Cash\n4002,100000.00,Revenue\n"
_SUBS04_CSV = b"account_code,amount,description\n1003,50000.00,Cash\n"


# ---------------------------------------------------------------------------
# 1. Entity CRUD
# ---------------------------------------------------------------------------

class TestEntityCrud:
    def test_create_entity_returns_201(self, client):
        r = client.post("/entities", json={"name": "ParentCo"})
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "ParentCo"
        assert "entity_id" in data
        assert data["parent_entity_id"] is None
        assert data["ownership_pct"] is None

    def test_create_child_entity(self, client):
        parent = client.post("/entities", json={"name": "HoldCo"}).json()
        child = client.post(
            "/entities",
            json={
                "name": "SubCo",
                "parent_entity_id": parent["entity_id"],
                "ownership_pct": "80.00",
            },
        )
        assert child.status_code == 201
        data = child.json()
        assert data["parent_entity_id"] == parent["entity_id"]
        assert data["ownership_pct"] == "80.0000"

    def test_create_entity_invalid_parent_404(self, client):
        r = client.post(
            "/entities",
            json={"name": "Orphan", "parent_entity_id": str(uuid.uuid4())},
        )
        assert r.status_code == 404

    def test_list_entities(self, client):
        client.post("/entities", json={"name": "ListCo1"})
        client.post("/entities", json={"name": "ListCo2"})
        r = client.get("/entities")
        assert r.status_code == 200
        names = [e["name"] for e in r.json()]
        assert "ListCo1" in names
        assert "ListCo2" in names

    def test_entity_tree_structure(self, client):
        parent = client.post("/entities", json={"name": "TreeParent"}).json()
        client.post(
            "/entities",
            json={
                "name": "TreeChild",
                "parent_entity_id": parent["entity_id"],
                "ownership_pct": "100.00",
            },
        )
        r = client.get("/entities/tree")
        assert r.status_code == 200
        tree = r.json()
        assert isinstance(tree, list)
        # Locate our root node
        roots = [n for n in tree if n["name"] == "TreeParent"]
        assert roots, "TreeParent not found as root"
        root = roots[0]
        child_names = [c["name"] for c in root["children"]]
        assert "TreeChild" in child_names

    def test_get_entity_by_id(self, client):
        created = client.post("/entities", json={"name": "GetMe"}).json()
        r = client.get(f"/entities/{created['entity_id']}")
        assert r.status_code == 200
        assert r.json()["name"] == "GetMe"

    def test_get_entity_unknown_404(self, client):
        r = client.get(f"/entities/{uuid.uuid4()}")
        assert r.status_code == 404

    def test_patch_entity_ownership(self, client):
        parent = client.post("/entities", json={"name": "PatchParent"}).json()
        child = client.post(
            "/entities",
            json={"name": "PatchChild", "parent_entity_id": parent["entity_id"], "ownership_pct": "60.00"},
        ).json()
        r = client.patch(
            f"/entities/{child['entity_id']}", json={"ownership_pct": "75.00"}
        )
        assert r.status_code == 200
        assert r.json()["ownership_pct"] == "75.0000"

    def test_patch_entity_unknown_404(self, client):
        r = client.patch(f"/entities/{uuid.uuid4()}", json={"ownership_pct": "50.00"})
        assert r.status_code == 404

    def test_delete_entity_no_entries_204(self, client):
        created = client.post("/entities", json={"name": "DeleteMe"}).json()
        r = client.delete(f"/entities/{created['entity_id']}")
        assert r.status_code == 204
        # Confirm gone
        assert client.get(f"/entities/{created['entity_id']}").status_code == 404

    def test_delete_entity_unknown_404(self, client):
        r = client.delete(f"/entities/{uuid.uuid4()}")
        assert r.status_code == 404

    def test_duplicate_entity_name_allowed_at_creation(self, client):
        """Two entities may share a name; ingestion will 404 on ambiguity."""
        client.post("/entities", json={"name": "DupName"})
        r2 = client.post("/entities", json={"name": "DupName"})
        assert r2.status_code == 201  # creation succeeds; ambiguity is an ingestion concern


# ---------------------------------------------------------------------------
# 2. Period CRUD
# ---------------------------------------------------------------------------

class TestPeriodCrud:
    def test_create_period_201(self, client):
        r = client.post(
            "/periods",
            json={"label": "FY-2100", "period_start": "2100-01-01", "period_end": "2100-12-31"},
        )
        assert r.status_code == 201
        data = r.json()
        assert data["label"] == "FY-2100"
        assert data["status"] == "open"
        assert "period_id" in data

    def test_create_period_duplicate_label_409(self, client):
        client.post(
            "/periods",
            json={"label": "FY-DUP", "period_start": "2100-01-01", "period_end": "2100-12-31"},
        )
        r = client.post(
            "/periods",
            json={"label": "FY-DUP", "period_start": "2101-01-01", "period_end": "2101-12-31"},
        )
        assert r.status_code == 409

    def test_create_period_end_before_start_422(self, client):
        r = client.post(
            "/periods",
            json={"label": "FY-BAD", "period_start": "2100-12-31", "period_end": "2100-01-01"},
        )
        assert r.status_code == 422

    def test_list_periods(self, client):
        client.post(
            "/periods",
            json={"label": "FY-LIST", "period_start": "2100-01-01", "period_end": "2100-12-31"},
        )
        r = client.get("/periods")
        assert r.status_code == 200
        labels = [p["label"] for p in r.json()]
        assert "FY-LIST" in labels

    def test_get_period_by_id(self, client):
        created = client.post(
            "/periods",
            json={"label": "FY-GET", "period_start": "2100-01-01", "period_end": "2100-12-31"},
        ).json()
        r = client.get(f"/periods/{created['period_id']}")
        assert r.status_code == 200
        assert r.json()["label"] == "FY-GET"

    def test_get_period_unknown_404(self, client):
        r = client.get(f"/periods/{uuid.uuid4()}")
        assert r.status_code == 404

    def test_lock_period(self, client):
        created = client.post(
            "/periods",
            json={"label": "FY-LOCK", "period_start": "2100-01-01", "period_end": "2100-12-31"},
        ).json()
        r = client.post(f"/periods/{created['period_id']}/lock")
        assert r.status_code == 200
        assert r.json()["status"] == "locked"

    def test_lock_period_already_locked_409(self, client):
        created = client.post(
            "/periods",
            json={"label": "FY-LOCK2", "period_start": "2100-01-01", "period_end": "2100-12-31"},
        ).json()
        client.post(f"/periods/{created['period_id']}/lock")
        r = client.post(f"/periods/{created['period_id']}/lock")
        assert r.status_code == 409

    def test_lock_period_unknown_404(self, client):
        r = client.post(f"/periods/{uuid.uuid4()}/lock")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# 3. Ingestion
# ---------------------------------------------------------------------------

class TestIngestion:
    def test_ingest_happy_path(self, client):
        """Create entity SUBS_01, ingest valid CSV, get mapped entries committed."""
        client.post("/entities", json={"name": "SUBS_01"})
        period = client.post(
            "/periods",
            json={"label": "FY-INGEST", "period_start": "2100-01-01", "period_end": "2100-12-31"},
        ).json()
        r = client.post(
            f"/ingest/SUBS_01?period_id={period['period_id']}",
            files={"file": ("tb.csv", io.BytesIO(_SUBS01_CSV), "text/csv")},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["mapped_count"] > 0
        assert data["entries_committed"] > 0

    def test_ingest_unknown_entity_404(self, client):
        # SUBS_02 is in the GCoA map (account 1001 → 1100) so rows are mapped,
        # but SUBS_02 is NOT registered in entity_metadata here → LookupError → 404.
        r = client.post(
            "/ingest/SUBS_02",
            files={"file": ("tb.csv", io.BytesIO(_SUBS02_CSV), "text/csv")},
        )
        assert r.status_code == 404

    def test_ingest_locked_period_423(self, client):
        # SUBS_03 is in the GCoA map so CSV rows are mapped → period lock check fires.
        client.post("/entities", json={"name": "SUBS_03"})
        period = client.post(
            "/periods",
            json={"label": "FY-LOCKINGEST", "period_start": "2100-01-01", "period_end": "2100-12-31"},
        ).json()
        client.post(f"/periods/{period['period_id']}/lock")
        r = client.post(
            f"/ingest/SUBS_03?period_id={period['period_id']}",
            files={"file": ("tb.csv", io.BytesIO(_SUBS03_CSV), "text/csv")},
        )
        assert r.status_code == 423

    def test_ingest_duplicate_entity_name_404(self, client):
        """When two entities share the same name, ingestion returns 404.

        SUBS_04 is in the GCoA map so the CSV has mapped rows. Creating two
        entity_metadata rows with name='SUBS_04' makes _resolve_entity_uuid
        raise LookupError("Multiple entities...") → 404.
        """
        client.post("/entities", json={"name": "SUBS_04"})
        client.post("/entities", json={"name": "SUBS_04"})
        r = client.post(
            "/ingest/SUBS_04",
            files={"file": ("tb.csv", io.BytesIO(_SUBS04_CSV), "text/csv")},
        )
        assert r.status_code == 404
        assert "Multiple entities" in r.json()["detail"]

    def test_ingest_empty_file_422(self, client):
        # Empty file check fires before entity resolution, so any entity name works.
        r = client.post(
            "/ingest/SUBS_01",
            files={"file": ("tb.csv", io.BytesIO(b""), "text/csv")},
        )
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# 4. Consolidation
# ---------------------------------------------------------------------------

def _fake_elim(entity_id: str) -> dict:
    """Return a fake elimination entry with a fresh UUID for each call."""
    return {
        "entry_id": str(uuid.uuid4()),
        "entity_id": entity_id,
        "account_code": "INTERCO_REC",
        "amount": "-50000.0000",
        "is_elimination": True,
        "metadata": {"elimination_type": "interco_receivable"},
    }


class TestConsolidation:
    def _setup_entity_and_period(self, client):
        """Create entity SUBS_05, ingest CSV, return (entity_id, period_id).

        Uses SUBS_05 (in GCoA map) and its account codes so ingestion commits
        real ledger entries required for consolidation.
        """
        entity = client.post("/entities", json={"name": "SUBS_05"}).json()
        period = client.post(
            "/periods",
            json={"label": "FY-CONS", "period_start": "2100-01-01", "period_end": "2100-12-31"},
        ).json()
        # SUBS_05 account 1004 → GCoA 1100 (cash)
        subs05_csv = b"account_code,amount,description\n1004,50000.00,Cash\n4004,100000.00,Revenue\n"
        client.post(
            f"/ingest/SUBS_05?period_id={period['period_id']}",
            files={"file": ("tb.csv", io.BytesIO(subs05_csv), "text/csv")},
        )
        return entity["entity_id"], period["period_id"]

    def test_consolidation_returns_eliminations(self, client):
        entity_id, period_id = self._setup_entity_and_period(client)

        mock_response = MagicMock()
        mock_response.json.return_value = {"eliminations": [_fake_elim(entity_id)], "count": 1}
        mock_response.raise_for_status.return_value = None

        with patch("backend.consolidation.router.httpx.post", return_value=mock_response):
            r = client.post(f"/consolidate/{period_id}")

        assert r.status_code == 200
        data = r.json()
        assert data["eliminations_created"] > 0
        assert str(data["period_id"]) == period_id

    def test_consolidation_no_entries_422(self, client):
        """Consolidation on a period with no ledger entries returns 422."""
        period = client.post(
            "/periods",
            json={"label": "FY-EMPTY-CONS", "period_start": "2100-01-01", "period_end": "2100-12-31"},
        ).json()
        r = client.post(f"/consolidate/{period['period_id']}")
        assert r.status_code == 422

    def test_consolidation_unknown_period_404(self, client):
        r = client.post(f"/consolidate/{uuid.uuid4()}")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# 5. Report
# ---------------------------------------------------------------------------

class TestReport:
    # Use SUBS_06 through SUBS_09 for report tests to avoid collisions with
    # earlier tests.  SUBS_0X has local cash code 100(X-1).
    _SUBS_NAMES = ["SUBS_06", "SUBS_07", "SUBS_08", "SUBS_09"]
    _SUBS_CASH  = {"SUBS_06": "1005", "SUBS_07": "1006", "SUBS_08": "1007", "SUBS_09": "1008"}
    _SUBS_REV   = {"SUBS_06": "4005", "SUBS_07": "4006", "SUBS_08": "4007", "SUBS_09": "4008"}

    def _setup(self, client, subs_name: str, period_label: str):
        """Create entity subs_name, ingest, consolidate; return period_id."""
        entity = client.post("/entities", json={"name": subs_name}).json()
        period = client.post(
            "/periods",
            json={"label": period_label, "period_start": "2100-01-01", "period_end": "2100-12-31"},
        ).json()
        cash_code = self._SUBS_CASH[subs_name]
        rev_code  = self._SUBS_REV[subs_name]
        csv_data  = f"account_code,amount,description\n{cash_code},50000.00,Cash\n{rev_code},100000.00,Rev\n".encode()
        client.post(
            f"/ingest/{subs_name}?period_id={period['period_id']}",
            files={"file": ("tb.csv", io.BytesIO(csv_data), "text/csv")},
        )
        mock_response = MagicMock()
        mock_response.json.return_value = {"eliminations": [_fake_elim(entity["entity_id"])], "count": 1}
        mock_response.raise_for_status.return_value = None
        with patch("backend.consolidation.router.httpx.post", return_value=mock_response):
            client.post(f"/consolidate/{period['period_id']}")
        return period["period_id"]

    def test_report_structure(self, client):
        period_id = self._setup(client, "SUBS_06", "FY-RPT1")
        r = client.get(f"/report/{period_id}")
        assert r.status_code == 200
        data = r.json()
        assert "balance_sheet" in data
        assert "income_statement" in data
        assert "eliminations_summary" in data
        assert "period" in data

    def test_report_balance_sheet_has_data(self, client):
        period_id = self._setup(client, "SUBS_07", "FY-RPT2")
        r = client.get(f"/report/{period_id}")
        assert r.status_code == 200
        bs = r.json()["balance_sheet"]
        # GCoA 1100 (assets) should appear from the cash account
        assert bs["assets"] or bs["liabilities"] or bs["equity"], (
            "Balance sheet should have at least one non-zero section"
        )

    def test_report_income_statement_has_data(self, client):
        period_id = self._setup(client, "SUBS_08", "FY-RPT3")
        r = client.get(f"/report/{period_id}")
        data = r.json()["income_statement"]
        # GCoA 4100 (revenue) from the revenue account
        assert data["revenue"], "Income statement revenue should be non-empty"

    def test_report_eliminations_summary_present(self, client):
        period_id = self._setup(client, "SUBS_09", "FY-RPT4")
        r = client.get(f"/report/{period_id}")
        summary = r.json()["eliminations_summary"]
        assert isinstance(summary, list)
        assert len(summary) > 0
        entry = summary[0]
        assert "elimination_type" in entry
        assert "entity_id" in entry
        assert "account_code" in entry
        assert "amount" in entry

    def test_report_unknown_period_404(self, client):
        r = client.get(f"/report/{uuid.uuid4()}")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# 6. Delete entity blocked when ledger entries exist
# ---------------------------------------------------------------------------

class TestDeleteEntityBlocked:
    def test_delete_blocked_by_ledger_entries(self, client):
        """DELETE /entities/{id} returns 409 when entity has ledger entries.

        Uses SUBS_10 (in GCoA map) so the CSV produces real ledger entries.
        """
        entity = client.post("/entities", json={"name": "SUBS_10"}).json()
        period = client.post(
            "/periods",
            json={"label": "FY-NODELETE", "period_start": "2100-01-01", "period_end": "2100-12-31"},
        ).json()
        # SUBS_10 account 1009 → GCoA 1100
        subs10_csv = b"account_code,amount,description\n1009,50000.00,Cash\n"
        ingest_r = client.post(
            f"/ingest/SUBS_10?period_id={period['period_id']}",
            files={"file": ("tb.csv", io.BytesIO(subs10_csv), "text/csv")},
        )
        assert ingest_r.status_code == 200, f"Ingest failed: {ingest_r.json()}"
        assert ingest_r.json()["entries_committed"] > 0, "No entries committed; delete won't be blocked"

        r = client.delete(f"/entities/{entity['entity_id']}")
        assert r.status_code == 409
        assert "ledger entries" in r.json()["detail"].lower()
