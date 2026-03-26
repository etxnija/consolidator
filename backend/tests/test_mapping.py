"""Tests for CSV-to-GCoA mapping logic."""

from __future__ import annotations

import io
from decimal import Decimal

import pandas as pd
import pytest

from ingestion.gcoa_map import lookup
from ingestion.mapping import map_trial_balance, parse_csv, split_records
from ingestion.models import TrialBalanceRow


# ---------------------------------------------------------------------------
# gcoa_map.lookup
# ---------------------------------------------------------------------------

class TestLookup:
    def test_known_mapping(self) -> None:
        assert lookup("SUBS_01", "1000") == "1100"

    def test_unknown_entity(self) -> None:
        assert lookup("SUBS_99", "1000") is None

    def test_unknown_local_code(self) -> None:
        assert lookup("SUBS_01", "9999") is None

    def test_whitespace_stripped(self) -> None:
        assert lookup("SUBS_01", " 1000 ") == "1100"

    def test_all_ten_subsidiaries_have_cash(self) -> None:
        local_cash = {
            "SUBS_01": "1000", "SUBS_02": "1001", "SUBS_03": "1002",
            "SUBS_04": "1003", "SUBS_05": "1004", "SUBS_06": "1005",
            "SUBS_07": "1006", "SUBS_08": "1007", "SUBS_09": "1008",
            "SUBS_10": "1009",
        }
        for entity_id, code in local_cash.items():
            assert lookup(entity_id, code) == "1100", (
                f"{entity_id}: expected 1100 for {code}"
            )


# ---------------------------------------------------------------------------
# parse_csv
# ---------------------------------------------------------------------------

VALID_CSV = """\
account_code,amount,description
1000,50000.00,Cash
2000,-15000.00,Accounts Payable
"""

MISSING_AMOUNT_CSV = """\
account_code,description
1000,Cash
"""

EMPTY_CSV = "account_code,amount,description\n"


class TestParseCsv:
    def test_valid_csv_bytes(self) -> None:
        df = parse_csv(VALID_CSV.encode())
        assert list(df.columns) == ["account_code", "amount", "description"]
        assert len(df) == 2

    def test_valid_csv_str(self) -> None:
        df = parse_csv(VALID_CSV)
        assert len(df) == 2

    def test_missing_required_column_raises(self) -> None:
        with pytest.raises(ValueError, match="missing required columns"):
            parse_csv(MISSING_AMOUNT_CSV)

    def test_empty_csv_raises(self) -> None:
        with pytest.raises(ValueError, match="no data rows"):
            parse_csv(EMPTY_CSV)

    def test_optional_description_added_if_absent(self) -> None:
        csv = "account_code,amount\n1000,100\n"
        df = parse_csv(csv)
        assert "description" in df.columns

    def test_column_names_lowercased(self) -> None:
        csv = "Account_Code,Amount,Description\n1000,100,Cash\n"
        df = parse_csv(csv)
        assert "account_code" in df.columns
        assert "amount" in df.columns


# ---------------------------------------------------------------------------
# map_trial_balance
# ---------------------------------------------------------------------------

def _make_df(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df.columns = [c.lower() for c in df.columns]
    for col in ["description"]:
        if col not in df.columns:
            df[col] = ""
    return df


class TestMapTrialBalance:
    def test_all_mapped(self) -> None:
        df = _make_df([
            {"account_code": "1000", "amount": "50000.00", "description": "Cash"},
            {"account_code": "2000", "amount": "-15000.00", "description": "AP"},
        ])
        records = map_trial_balance("SUBS_01", df)
        assert len(records) == 2
        assert all(r.gcoa_code is not None for r in records)
        assert all(r.entry is not None for r in records)

    def test_unmapped_row(self) -> None:
        df = _make_df([
            {"account_code": "9999", "amount": "100.00"},
        ])
        records = map_trial_balance("SUBS_01", df)
        assert len(records) == 1
        assert records[0].gcoa_code is None
        assert records[0].entry is None

    def test_mixed_mapped_and_unmapped(self) -> None:
        df = _make_df([
            {"account_code": "1000", "amount": "100.00"},
            {"account_code": "9999", "amount": "50.00"},
        ])
        records = map_trial_balance("SUBS_01", df)
        mapped = [r for r in records if r.entry is not None]
        unmapped = [r for r in records if r.entry is None]
        assert len(mapped) == 1
        assert len(unmapped) == 1

    def test_entry_fields_correct(self) -> None:
        df = _make_df([{"account_code": "1000", "amount": "12345.67"}])
        records = map_trial_balance("SUBS_01", df)
        entry = records[0].entry
        assert entry is not None
        assert entry.entity_id == "SUBS_01"
        assert entry.account_code == "1100"  # GCoA code
        assert entry.amount == Decimal("12345.67")
        assert entry.is_elimination is False
        assert entry.metadata["local_account_code"] == "1000"

    def test_invalid_amount_row_skipped(self) -> None:
        df = _make_df([
            {"account_code": "1000", "amount": "not_a_number"},
            {"account_code": "1100", "amount": "200.00"},
        ])
        records = map_trial_balance("SUBS_01", df)
        # Invalid row is skipped; only the valid row appears
        assert len(records) == 1

    def test_extra_metadata_merged(self) -> None:
        df = _make_df([{"account_code": "1000", "amount": "100.00"}])
        records = map_trial_balance("SUBS_01", df, extra_metadata={"upload_id": "x"})
        assert records[0].entry is not None
        assert records[0].entry.metadata["upload_id"] == "x"


# ---------------------------------------------------------------------------
# split_records
# ---------------------------------------------------------------------------

class TestSplitRecords:
    def test_splits_correctly(self) -> None:
        df = _make_df([
            {"account_code": "1000", "amount": "100.00"},
            {"account_code": "9999", "amount": "50.00"},
            {"account_code": "9999", "amount": "25.00"},  # duplicate unmapped
        ])
        records = map_trial_balance("SUBS_01", df)
        entries, unmapped = split_records(records)
        assert len(entries) == 1
        assert len(unmapped) == 1  # deduplicated
        assert unmapped[0] == "9999"

    def test_empty_input(self) -> None:
        entries, unmapped = split_records([])
        assert entries == []
        assert unmapped == []
