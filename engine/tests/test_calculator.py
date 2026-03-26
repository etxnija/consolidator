"""Tests for IfrsCalculator — IFRS 10 elimination logic.

All tests use in-memory data; no database is involved.

Signed-amount convention: positive = debit, negative = credit.

Normal balances:
    INTERCO_REC  (asset)       — positive
    INTERCO_PAY  (liability)   — negative
    INVEST_SUB   (asset)       — positive
    EQUITY_*     (equity)      — negative
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Optional

import pytest

from engine.calculator import IfrsCalculator
from engine.models import EliminationEntry, EntityNode, LedgerEntrySnapshot


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dt(year: int, month: int, day: int) -> datetime:
    return datetime(year, month, day, tzinfo=timezone.utc)


def _entry(
    entity_id: uuid.UUID,
    account_code: str,
    amount: Decimal,
    timestamp: datetime = _dt(2025, 12, 31),
    is_elimination: bool = False,
    metadata: Optional[Dict] = None,
) -> LedgerEntrySnapshot:
    return LedgerEntrySnapshot(
        entry_id=uuid.uuid4(),
        timestamp=timestamp,
        entity_id=entity_id,
        account_code=account_code,
        amount=amount,
        is_elimination=is_elimination,
        metadata=metadata,
    )


CUT_OFF = _dt(2025, 12, 31)

# ---------------------------------------------------------------------------
# Fixtures — entity hierarchy
# ---------------------------------------------------------------------------

PARENT_ID = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001")
CHILD_ID = uuid.UUID("bbbbbbbb-0000-0000-0000-000000000002")
SIBLING_ID = uuid.UUID("cccccccc-0000-0000-0000-000000000003")

PARENT = EntityNode(entity_id=PARENT_ID, name="Parent Co")
CHILD = EntityNode(entity_id=CHILD_ID, name="Subsidiary", parent_entity_id=PARENT_ID, ownership_pct=Decimal("100"))
SIBLING = EntityNode(entity_id=SIBLING_ID, name="Sibling Sub", parent_entity_id=PARENT_ID, ownership_pct=Decimal("75"))

TWO_ENTITY = [PARENT, CHILD]
THREE_ENTITY = [PARENT, CHILD, SIBLING]


# ---------------------------------------------------------------------------
# Intercompany elimination — basic
# ---------------------------------------------------------------------------

class TestIntercompanyElimination:

    def test_matched_pair_produces_two_eliminations(self):
        """A receivable on A and corresponding payable on B yield two eliminations."""
        entries = [
            _entry(PARENT_ID, "INTERCO_REC", Decimal("500"),
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
            _entry(CHILD_ID, "INTERCO_PAY", Decimal("-500"),
                   metadata={"counterparty_entity_id": str(PARENT_ID)}),
        ]

        result = IfrsCalculator.eliminate(entries, TWO_ENTITY, CUT_OFF)

        elim_codes = {e.account_code for e in result}
        assert "INTERCO_REC" in elim_codes
        assert "INTERCO_PAY" in elim_codes

        rec_elim = next(e for e in result if e.account_code == "INTERCO_REC")
        pay_elim = next(e for e in result if e.account_code == "INTERCO_PAY")

        # Negate the original balances
        assert rec_elim.amount == Decimal("-500"), rec_elim.amount
        assert pay_elim.amount == Decimal("500"), pay_elim.amount
        assert rec_elim.entity_id == PARENT_ID
        assert pay_elim.entity_id == CHILD_ID

    def test_all_elimination_entries_have_flag(self):
        entries = [
            _entry(PARENT_ID, "INTERCO_REC", Decimal("200"),
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
            _entry(CHILD_ID, "INTERCO_PAY", Decimal("-200"),
                   metadata={"counterparty_entity_id": str(PARENT_ID)}),
        ]
        for e in IfrsCalculator.eliminate(entries, TWO_ENTITY, CUT_OFF):
            assert e.is_elimination is True

    def test_no_interco_entries_yields_no_interco_eliminations(self):
        entries = [
            _entry(PARENT_ID, "REVENUE", Decimal("1000")),
            _entry(CHILD_ID, "EXPENSES", Decimal("500")),
        ]
        result = IfrsCalculator.eliminate(entries, TWO_ENTITY, CUT_OFF)
        interco = [e for e in result if "INTERCO" in e.account_code]
        assert interco == []

    def test_entries_after_cutoff_are_excluded(self):
        future = _dt(2026, 1, 15)
        entries = [
            _entry(PARENT_ID, "INTERCO_REC", Decimal("300"), timestamp=future,
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
        ]
        result = IfrsCalculator.eliminate(entries, TWO_ENTITY, CUT_OFF)
        assert result == []

    def test_already_eliminated_entries_are_excluded(self):
        entries = [
            _entry(PARENT_ID, "INTERCO_REC", Decimal("300"), is_elimination=True,
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
        ]
        result = IfrsCalculator.eliminate(entries, TWO_ENTITY, CUT_OFF)
        # The pre-existing elimination entry itself is not doubled
        assert result == []

    def test_multiple_transactions_aggregated(self):
        """Multiple REC postings between the same pair are summed."""
        entries = [
            _entry(PARENT_ID, "INTERCO_REC", Decimal("100"),
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
            _entry(PARENT_ID, "INTERCO_REC", Decimal("150"),
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
            _entry(CHILD_ID, "INTERCO_PAY", Decimal("-250"),
                   metadata={"counterparty_entity_id": str(PARENT_ID)}),
        ]
        result = IfrsCalculator.eliminate(entries, TWO_ENTITY, CUT_OFF)
        rec_elim = next(e for e in result if e.account_code == "INTERCO_REC")
        assert rec_elim.amount == Decimal("-250")

    def test_counterparty_outside_group_is_ignored(self):
        """Interco entries whose counterparty is outside the group are not eliminated."""
        external_id = uuid.uuid4()
        entries = [
            _entry(PARENT_ID, "INTERCO_REC", Decimal("999"),
                   metadata={"counterparty_entity_id": str(external_id)}),
        ]
        result = IfrsCalculator.eliminate(entries, TWO_ENTITY, CUT_OFF)
        assert result == []

    def test_sibling_interco(self):
        """Two siblings can also have intercompany balances that need elimination."""
        entries = [
            _entry(CHILD_ID, "INTERCO_REC", Decimal("400"),
                   metadata={"counterparty_entity_id": str(SIBLING_ID)}),
            _entry(SIBLING_ID, "INTERCO_PAY", Decimal("-400"),
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
        ]
        result = IfrsCalculator.eliminate(entries, THREE_ENTITY, CUT_OFF)
        assert len(result) == 2
        rec_elim = next(e for e in result if e.entity_id == CHILD_ID)
        pay_elim = next(e for e in result if e.entity_id == SIBLING_ID)
        assert rec_elim.amount == Decimal("-400")
        assert pay_elim.amount == Decimal("400")


# ---------------------------------------------------------------------------
# Equity elimination — basic
# ---------------------------------------------------------------------------

class TestEquityElimination:

    def test_investment_vs_equity_produces_two_eliminations(self):
        """Parent's INVEST_SUB and child's EQUITY_SHARE_CAP are both eliminated."""
        entries = [
            _entry(PARENT_ID, "INVEST_SUB", Decimal("1000"),
                   metadata={"subsidiary_entity_id": str(CHILD_ID)}),
            _entry(CHILD_ID, "EQUITY_SHARE_CAP", Decimal("-1000")),
        ]
        result = IfrsCalculator.eliminate(entries, TWO_ENTITY, CUT_OFF)

        invest_elim = next(
            (e for e in result if e.entity_id == PARENT_ID), None
        )
        equity_elim = next(
            (e for e in result if e.entity_id == CHILD_ID), None
        )

        assert invest_elim is not None
        assert equity_elim is not None
        # Investment (debit asset) is credit-eliminated: amount becomes negative
        assert invest_elim.amount == Decimal("-1000")
        # Equity (credit balance) is debit-eliminated: amount becomes positive
        assert equity_elim.amount == Decimal("1000")

    def test_multiple_equity_accounts_aggregated(self):
        """Share capital + retained earnings are summed for the child."""
        entries = [
            _entry(PARENT_ID, "INVEST_SUB", Decimal("1500"),
                   metadata={"subsidiary_entity_id": str(CHILD_ID)}),
            _entry(CHILD_ID, "EQUITY_SHARE_CAP", Decimal("-1000")),
            _entry(CHILD_ID, "EQUITY_RET_EARN", Decimal("-500")),
        ]
        result = IfrsCalculator.eliminate(entries, TWO_ENTITY, CUT_OFF)
        equity_elim = next(e for e in result if e.entity_id == CHILD_ID)
        assert equity_elim.amount == Decimal("1500")

    def test_no_equity_entries_only_invest_eliminated(self):
        """If child has no equity entries, only the parent investment is eliminated."""
        entries = [
            _entry(PARENT_ID, "INVEST_SUB", Decimal("200"),
                   metadata={"subsidiary_entity_id": str(CHILD_ID)}),
        ]
        result = IfrsCalculator.eliminate(entries, TWO_ENTITY, CUT_OFF)
        invest_elim = [e for e in result if e.entity_id == PARENT_ID]
        equity_elim = [e for e in result if e.entity_id == CHILD_ID]
        assert len(invest_elim) == 1
        assert invest_elim[0].amount == Decimal("-200")
        assert equity_elim == []

    def test_zero_balances_produce_no_entries(self):
        """If net investment and net equity are both zero, no entries are produced."""
        entries = [
            _entry(PARENT_ID, "INVEST_SUB", Decimal("0"),
                   metadata={"subsidiary_entity_id": str(CHILD_ID)}),
            _entry(CHILD_ID, "EQUITY_SHARE_CAP", Decimal("0")),
        ]
        result = IfrsCalculator.eliminate(entries, TWO_ENTITY, CUT_OFF)
        assert result == []

    def test_investment_for_unknown_subsidiary_is_ignored(self):
        """INVEST_SUB whose subsidiary is not in the entity list is skipped."""
        external_sub = uuid.uuid4()
        entries = [
            _entry(PARENT_ID, "INVEST_SUB", Decimal("500"),
                   metadata={"subsidiary_entity_id": str(external_sub)}),
        ]
        result = IfrsCalculator.eliminate(entries, TWO_ENTITY, CUT_OFF)
        invest_elims = [e for e in result if "INVEST" in e.account_code]
        assert invest_elims == []

    def test_two_subsidiaries_independent_eliminations(self):
        """Each parent→child pair gets its own equity elimination."""
        entries = [
            _entry(PARENT_ID, "INVEST_SUB", Decimal("1000"),
                   metadata={"subsidiary_entity_id": str(CHILD_ID)}),
            _entry(PARENT_ID, "INVEST_SUB", Decimal("750"),
                   metadata={"subsidiary_entity_id": str(SIBLING_ID)}),
            _entry(CHILD_ID, "EQUITY_SHARE_CAP", Decimal("-1000")),
            _entry(SIBLING_ID, "EQUITY_SHARE_CAP", Decimal("-750")),
        ]
        result = IfrsCalculator.eliminate(entries, THREE_ENTITY, CUT_OFF)
        # 2 invest eliminations + 2 equity eliminations = 4
        assert len(result) == 4


# ---------------------------------------------------------------------------
# Combined step: both intercompany + equity in one call
# ---------------------------------------------------------------------------

class TestCombinedElimination:

    def test_combined_returns_all_elimination_types(self):
        entries = [
            # Intercompany
            _entry(PARENT_ID, "INTERCO_REC", Decimal("300"),
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
            _entry(CHILD_ID, "INTERCO_PAY", Decimal("-300"),
                   metadata={"counterparty_entity_id": str(PARENT_ID)}),
            # Equity
            _entry(PARENT_ID, "INVEST_SUB", Decimal("1000"),
                   metadata={"subsidiary_entity_id": str(CHILD_ID)}),
            _entry(CHILD_ID, "EQUITY_SHARE_CAP", Decimal("-1000")),
        ]
        result = IfrsCalculator.eliminate(entries, TWO_ENTITY, CUT_OFF)
        assert len(result) == 4
        codes = {e.account_code for e in result}
        assert "INTERCO_REC" in codes
        assert "INTERCO_PAY" in codes
        assert "INVEST_SUB" in codes
        # equity elimination uses "EQUITY" code
        assert any("EQUITY" in c for c in codes)

    def test_empty_ledger_returns_empty_list(self):
        result = IfrsCalculator.eliminate([], TWO_ENTITY, CUT_OFF)
        assert result == []

    def test_empty_entities_returns_empty_list(self):
        entries = [
            _entry(PARENT_ID, "INTERCO_REC", Decimal("100"),
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
        ]
        result = IfrsCalculator.eliminate(entries, [], CUT_OFF)
        assert result == []


# ---------------------------------------------------------------------------
# EliminationEntry metadata correctness
# ---------------------------------------------------------------------------

class TestEliminationMetadata:

    def test_interco_rec_metadata_records_counterparty(self):
        entries = [
            _entry(PARENT_ID, "INTERCO_REC", Decimal("100"),
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
        ]
        result = IfrsCalculator.eliminate(entries, TWO_ENTITY, CUT_OFF)
        rec_elim = next(e for e in result if e.account_code == "INTERCO_REC")
        assert rec_elim.metadata["counterparty_entity_id"] == str(CHILD_ID)
        assert rec_elim.metadata["elimination_type"] == "intercompany_receivable"

    def test_equity_invest_metadata_records_subsidiary(self):
        entries = [
            _entry(PARENT_ID, "INVEST_SUB", Decimal("500"),
                   metadata={"subsidiary_entity_id": str(CHILD_ID)}),
        ]
        result = IfrsCalculator.eliminate(entries, TWO_ENTITY, CUT_OFF)
        inv_elim = next(e for e in result if e.entity_id == PARENT_ID)
        assert inv_elim.metadata["subsidiary_entity_id"] == str(CHILD_ID)
        assert inv_elim.metadata["elimination_type"] == "equity_investment"
