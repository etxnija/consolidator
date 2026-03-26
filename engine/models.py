"""Pure Python dataclasses mirroring the ORM schema.

These types are used by the IFRS 10 calculator and carry no SQLAlchemy
or database dependencies.  Callers load data from whatever source they
like and convert to these types before calling IfrsCalculator.eliminate().

Signed-amount convention (same as the ORM model):
    positive amount = debit
    negative amount = credit

Typical normal balances:
    Assets        — debit (+)
    Liabilities   — credit (-)
    Equity        — credit (-)
    Revenue       — credit (-)
    Expenses      — debit (+)

Account-code conventions used by the calculator:
    INTERCO_REC   — intercompany receivable (asset, debit balance)
                    metadata must contain: counterparty_entity_id (str UUID)
    INTERCO_PAY   — intercompany payable (liability, credit balance)
                    metadata must contain: counterparty_entity_id (str UUID)
    INVEST_SUB    — parent's investment in subsidiary (asset, debit balance)
                    metadata must contain: subsidiary_entity_id (str UUID)
    EQUITY_*      — any equity account of the subsidiary
                    (share capital, retained earnings, …)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional


@dataclass
class EntityNode:
    """One node in the consolidation entity hierarchy."""

    entity_id: uuid.UUID
    name: str
    parent_entity_id: Optional[uuid.UUID] = None
    # Ownership percentage expressed as 0–100 (e.g. 75.0 means 75 %)
    ownership_pct: Optional[Decimal] = None


@dataclass
class LedgerEntrySnapshot:
    """Immutable snapshot of a single ledger posting."""

    entry_id: uuid.UUID
    timestamp: datetime
    entity_id: uuid.UUID
    account_code: str
    amount: Decimal
    is_elimination: bool = False
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class EliminationEntry:
    """A synthetic elimination entry produced by IfrsCalculator.

    Always has is_elimination=True.  entry_id is generated fresh so the
    entry can be appended to the ledger without collision.
    """

    entry_id: uuid.UUID = field(default_factory=uuid.uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.utcnow())
    entity_id: uuid.UUID = field(default_factory=uuid.uuid4)
    account_code: str = ""
    amount: Decimal = Decimal("0")
    is_elimination: bool = True
    metadata: Optional[Dict[str, Any]] = None
