"""Test harness: PandasValidator vs IfrsCalculator + trial-balance invariant.

Two independent implementations are run on the same scenarios and their
net elimination amounts are compared.  Any divergence reveals a logic error
in one (or both) implementations.

Additionally, this module asserts the hard mathematical invariant:
    consolidated trial balance nets to zero
when the source ledger is perfectly balanced (every debit has a matching credit).

Signed-amount convention: positive = debit, negative = credit.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Optional

import pytest

from engine.calculator import IfrsCalculator
from engine.models import EntityNode, LedgerEntrySnapshot
from engine.validator import PandasValidator, assert_trial_balance_zero


# ---------------------------------------------------------------------------
# Shared test helpers (same as test_calculator.py so the harness is independent)
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

PARENT_ID = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001")
CHILD_ID  = uuid.UUID("bbbbbbbb-0000-0000-0000-000000000002")
SIBLING_ID = uuid.UUID("cccccccc-0000-0000-0000-000000000003")

PARENT  = EntityNode(entity_id=PARENT_ID, name="Parent Co")
CHILD   = EntityNode(entity_id=CHILD_ID,  name="Subsidiary",
                     parent_entity_id=PARENT_ID, ownership_pct=Decimal("100"))
SIBLING = EntityNode(entity_id=SIBLING_ID, name="Sibling Sub",
                     parent_entity_id=PARENT_ID, ownership_pct=Decimal("75"))

TWO_ENTITY   = [PARENT, CHILD]
THREE_ENTITY = [PARENT, CHILD, SIBLING]


# ---------------------------------------------------------------------------
# Comparison helpers
# ---------------------------------------------------------------------------

def _calc_net(entries, entities, cut_off):
    """Return {(entity_id_str, account_code): net_amount} from IfrsCalculator."""
    elims = IfrsCalculator.eliminate(entries, entities, cut_off)
    result: Dict = {}
    for e in elims:
        key = (str(e.entity_id), e.account_code)
        result[key] = result.get(key, 0.0) + float(e.amount)
    return result


def _validator_net(entries, entities, cut_off):
    """Return {(entity_id_str, account_code): net_amount} from PandasValidator."""
    df = PandasValidator.expected_eliminations(entries, entities, cut_off)
    if df.empty:
        return {}
    result: Dict = {}
    for _, row in df.iterrows():
        key = (str(row["entity_id"]), row["account_code"])
        result[key] = result.get(key, 0.0) + float(row["amount"])
    return result


def _assert_outputs_match(entries, entities, cut_off, tol=1e-4):
    """Assert both implementations produce the same net elimination amounts."""
    calc = _calc_net(entries, entities, cut_off)
    val  = _validator_net(entries, entities, cut_off)

    all_keys = set(calc) | set(val)
    mismatches = []
    for key in all_keys:
        c = calc.get(key, 0.0)
        v = val.get(key, 0.0)
        if abs(c - v) > tol:
            mismatches.append(f"  {key}: calculator={c:.4f}, validator={v:.4f}, Δ={c-v:.4f}")

    assert not mismatches, (
        "Calculator and PandasValidator disagree:\n" + "\n".join(mismatches)
    )


# ---------------------------------------------------------------------------
# Scenario 1: Matched intercompany receivable / payable
# ---------------------------------------------------------------------------

class TestIntercompanyComparison:

    def test_matched_pair(self):
        entries = [
            _entry(PARENT_ID, "INTERCO_REC", Decimal("500"),
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
            _entry(CHILD_ID,  "INTERCO_PAY", Decimal("-500"),
                   metadata={"counterparty_entity_id": str(PARENT_ID)}),
        ]
        _assert_outputs_match(entries, TWO_ENTITY, CUT_OFF)

    def test_multiple_transactions_same_pair(self):
        entries = [
            _entry(PARENT_ID, "INTERCO_REC", Decimal("100"),
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
            _entry(PARENT_ID, "INTERCO_REC", Decimal("150"),
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
            _entry(CHILD_ID,  "INTERCO_PAY", Decimal("-250"),
                   metadata={"counterparty_entity_id": str(PARENT_ID)}),
        ]
        _assert_outputs_match(entries, TWO_ENTITY, CUT_OFF)

    def test_sibling_interco(self):
        entries = [
            _entry(CHILD_ID,   "INTERCO_REC", Decimal("400"),
                   metadata={"counterparty_entity_id": str(SIBLING_ID)}),
            _entry(SIBLING_ID, "INTERCO_PAY", Decimal("-400"),
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
        ]
        _assert_outputs_match(entries, THREE_ENTITY, CUT_OFF)

    def test_receivable_only(self):
        """Unmatched receivable — only rec side should be eliminated."""
        entries = [
            _entry(PARENT_ID, "INTERCO_REC", Decimal("200"),
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
        ]
        _assert_outputs_match(entries, TWO_ENTITY, CUT_OFF)

    def test_empty_yields_empty(self):
        _assert_outputs_match([], TWO_ENTITY, CUT_OFF)


# ---------------------------------------------------------------------------
# Scenario 2: Equity elimination
# ---------------------------------------------------------------------------

class TestEquityComparison:

    def test_full_ownership(self):
        entries = [
            _entry(PARENT_ID, "INVEST_SUB", Decimal("1000"),
                   metadata={"subsidiary_entity_id": str(CHILD_ID)}),
            _entry(CHILD_ID,  "EQUITY_SHARE_CAP", Decimal("-1000")),
        ]
        _assert_outputs_match(entries, TWO_ENTITY, CUT_OFF)

    def test_multiple_equity_accounts(self):
        entries = [
            _entry(PARENT_ID, "INVEST_SUB", Decimal("1500"),
                   metadata={"subsidiary_entity_id": str(CHILD_ID)}),
            _entry(CHILD_ID,  "EQUITY_SHARE_CAP", Decimal("-1000")),
            _entry(CHILD_ID,  "EQUITY_RET_EARN",  Decimal("-500")),
        ]
        _assert_outputs_match(entries, TWO_ENTITY, CUT_OFF)

    def test_partial_ownership_nci(self):
        """75%-owned subsidiary → NCI_EQUITY entry should match between impls."""
        entries = [
            _entry(PARENT_ID,  "INVEST_SUB",       Decimal("750"),
                   metadata={"subsidiary_entity_id": str(SIBLING_ID)}),
            _entry(SIBLING_ID, "EQUITY_SHARE_CAP", Decimal("-1000")),
        ]
        _assert_outputs_match(entries, THREE_ENTITY, CUT_OFF)

    def test_two_subsidiaries(self):
        entries = [
            _entry(PARENT_ID,  "INVEST_SUB",       Decimal("1000"),
                   metadata={"subsidiary_entity_id": str(CHILD_ID)}),
            _entry(PARENT_ID,  "INVEST_SUB",       Decimal("750"),
                   metadata={"subsidiary_entity_id": str(SIBLING_ID)}),
            _entry(CHILD_ID,   "EQUITY_SHARE_CAP", Decimal("-1000")),
            _entry(SIBLING_ID, "EQUITY_SHARE_CAP", Decimal("-750")),
        ]
        _assert_outputs_match(entries, THREE_ENTITY, CUT_OFF)


# ---------------------------------------------------------------------------
# Scenario 3: Dividend elimination
# ---------------------------------------------------------------------------

class TestDividendComparison:

    def test_matched_dividend_pair(self):
        entries = [
            _entry(CHILD_ID,  "DIVIDEND_PAID", Decimal("200"),
                   metadata={"counterparty_entity_id": str(PARENT_ID)}),
            _entry(PARENT_ID, "DIVIDEND_REC",  Decimal("-200"),
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
        ]
        _assert_outputs_match(entries, TWO_ENTITY, CUT_OFF)

    def test_dividend_paid_only(self):
        entries = [
            _entry(CHILD_ID, "DIVIDEND_PAID", Decimal("100"),
                   metadata={"counterparty_entity_id": str(PARENT_ID)}),
        ]
        _assert_outputs_match(entries, TWO_ENTITY, CUT_OFF)


# ---------------------------------------------------------------------------
# Scenario 4: Intragroup revenue / COGS
# ---------------------------------------------------------------------------

class TestIntercoRevenueComparison:

    def test_matched_rev_cogs(self):
        entries = [
            _entry(CHILD_ID,   "INTERCO_REV",  Decimal("-500"),
                   metadata={"counterparty_entity_id": str(SIBLING_ID)}),
            _entry(SIBLING_ID, "INTERCO_COGS", Decimal("500"),
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
        ]
        _assert_outputs_match(entries, THREE_ENTITY, CUT_OFF)

    def test_revenue_only(self):
        entries = [
            _entry(CHILD_ID, "INTERCO_REV", Decimal("-300"),
                   metadata={"counterparty_entity_id": str(SIBLING_ID)}),
        ]
        _assert_outputs_match(entries, THREE_ENTITY, CUT_OFF)


# ---------------------------------------------------------------------------
# Scenario 5: Combined (all elimination types at once)
# ---------------------------------------------------------------------------

class TestCombinedComparison:

    def test_all_types_simultaneously(self):
        entries = [
            # Intercompany
            _entry(PARENT_ID, "INTERCO_REC", Decimal("300"),
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
            _entry(CHILD_ID,  "INTERCO_PAY", Decimal("-300"),
                   metadata={"counterparty_entity_id": str(PARENT_ID)}),
            # Equity
            _entry(PARENT_ID, "INVEST_SUB",       Decimal("1000"),
                   metadata={"subsidiary_entity_id": str(CHILD_ID)}),
            _entry(CHILD_ID,  "EQUITY_SHARE_CAP", Decimal("-1000")),
            # Dividends
            _entry(CHILD_ID,  "DIVIDEND_PAID", Decimal("50"),
                   metadata={"counterparty_entity_id": str(PARENT_ID)}),
            _entry(PARENT_ID, "DIVIDEND_REC",  Decimal("-50"),
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
        ]
        _assert_outputs_match(entries, TWO_ENTITY, CUT_OFF)


# ---------------------------------------------------------------------------
# Trial balance invariant tests
# ---------------------------------------------------------------------------
#
# The invariant: sum(all original in-scope entries) + sum(eliminations) = 0
#
# This holds when the source ledger is balanced (every debit has a matching
# credit) AND all eliminations are balanced double-entry pairs.
#
# We construct purposefully-balanced ledgers here (each entity's entries net
# to zero before consolidation).
# ---------------------------------------------------------------------------

class TestTrialBalanceInvariant:

    def test_matched_interco_nets_to_zero(self):
        """Balanced intercompany pair — eliminations net to zero."""
        # REC +500 and PAY -500 cancel; eliminations (-500 + 500) also cancel.
        entries = [
            _entry(PARENT_ID, "INTERCO_REC", Decimal("500"),
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
            _entry(CHILD_ID,  "INTERCO_PAY", Decimal("-500"),
                   metadata={"counterparty_entity_id": str(PARENT_ID)}),
        ]
        # Original sum = 500 + (-500) = 0; elim sum = -500 + 500 = 0; total = 0
        assert_trial_balance_zero(entries, TWO_ENTITY, CUT_OFF)

    def test_matched_equity_100pct_nets_to_zero(self):
        """Balanced invest / equity pair for 100%-owned subsidiary."""
        # invest +1000 + equity_share_cap -1000 = 0 originally;
        # eliminations: -1000 + 1000 = 0; total = 0
        entries = [
            _entry(PARENT_ID, "INVEST_SUB",       Decimal("1000"),
                   metadata={"subsidiary_entity_id": str(CHILD_ID)}),
            _entry(CHILD_ID,  "EQUITY_SHARE_CAP", Decimal("-1000")),
        ]
        assert_trial_balance_zero(entries, TWO_ENTITY, CUT_OFF)

    def test_matched_dividends_net_to_zero(self):
        """Balanced dividend pair — eliminations net to zero."""
        # div_paid +200 + div_rec -200 = 0; eliminations -200 + 200 = 0
        entries = [
            _entry(CHILD_ID,  "DIVIDEND_PAID", Decimal("200"),
                   metadata={"counterparty_entity_id": str(PARENT_ID)}),
            _entry(PARENT_ID, "DIVIDEND_REC",  Decimal("-200"),
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
        ]
        assert_trial_balance_zero(entries, TWO_ENTITY, CUT_OFF)

    def test_matched_interco_rev_cogs_net_to_zero(self):
        """Balanced intragroup revenue / COGS pair."""
        # rev -500 + cogs +500 = 0; eliminations +500 + (-500) = 0
        entries = [
            _entry(CHILD_ID,   "INTERCO_REV",  Decimal("-500"),
                   metadata={"counterparty_entity_id": str(SIBLING_ID)}),
            _entry(SIBLING_ID, "INTERCO_COGS", Decimal("500"),
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
        ]
        assert_trial_balance_zero(entries, THREE_ENTITY, CUT_OFF)

    def test_full_balanced_consolidation_nets_to_zero(self):
        """Complete balanced two-entity consolidation — all elimination types.

        Ledger is constructed so that each entity's entries independently net
        to zero (proper double-entry bookkeeping).

        Parent Co (entity A):
            Cash / other assets    +1100  Dr
            INVEST_SUB (in B)      +1100  Dr
            INTERCO_REC (from B)    +300  Dr
            DIVIDEND_REC (from B)   -100  Cr  (income)
            Liabilities             -500  Cr
            Own equity             -1900  Cr
            ────────────────────────────────
            Net                        0

        Subsidiary B (100 % owned, entity B):
            Assets                 +1300  Dr
            INTERCO_PAY (to A)      -300  Cr
            DIVIDEND_PAID (to A)    +100  Dr  (reduces B equity)
            EQUITY_SHARE_CAP       -1100  Cr
            ────────────────────────────────
            Net                        0

        Consolidated:
            • INTERCO_REC (+300) and INTERCO_PAY (−300) cancel → elims net 0
            • INVEST_SUB (+1100) vs EQUITY (−1100) at 100% → elims net 0
            • DIVIDEND_PAID (+100) and DIVIDEND_REC (−100) cancel → elims net 0
            Grand total original + eliminations = 0  ✓
        """
        entries = [
            # --- Parent ---
            _entry(PARENT_ID, "ASSETS",       Decimal("1100")),
            _entry(PARENT_ID, "INVEST_SUB",   Decimal("1100"),
                   metadata={"subsidiary_entity_id": str(CHILD_ID)}),
            _entry(PARENT_ID, "INTERCO_REC",  Decimal("300"),
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
            _entry(PARENT_ID, "DIVIDEND_REC", Decimal("-100"),
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
            _entry(PARENT_ID, "LIABILITIES",  Decimal("-500")),
            _entry(PARENT_ID, "OWN_EQUITY",   Decimal("-1900")),
            # --- Subsidiary B ---
            _entry(CHILD_ID, "ASSETS",            Decimal("1300")),
            _entry(CHILD_ID, "INTERCO_PAY",       Decimal("-300"),
                   metadata={"counterparty_entity_id": str(PARENT_ID)}),
            _entry(CHILD_ID, "DIVIDEND_PAID",     Decimal("100"),
                   metadata={"counterparty_entity_id": str(PARENT_ID)}),
            _entry(CHILD_ID, "EQUITY_SHARE_CAP",  Decimal("-1100")),
        ]
        assert_trial_balance_zero(entries, TWO_ENTITY, CUT_OFF)

    def test_empty_ledger_nets_to_zero(self):
        """Empty ledger trivially nets to zero."""
        assert_trial_balance_zero([], TWO_ENTITY, CUT_OFF)

    def test_no_entities_nets_to_zero(self):
        """Entries outside the entity scope are excluded; net is zero."""
        entries = [
            _entry(PARENT_ID, "INTERCO_REC", Decimal("999"),
                   metadata={"counterparty_entity_id": str(CHILD_ID)}),
        ]
        assert_trial_balance_zero(entries, [], CUT_OFF)
