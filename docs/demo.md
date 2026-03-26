# North Star Consolidator — Demo Walkthrough

End-to-end demo of Phase 2: entity management, reporting periods, consolidation, NCI, and report output.

---

## Prerequisites

- Docker (or Podman + podman-compose)
- `curl` and `jq`

---

## 1. Start the stack

```bash
cd /path/to/consolidator
cp .env.example .env   # only needed once
docker compose up --build
```

Wait ~30 seconds for health checks. Then open **http://localhost:8000/docs** for the Swagger UI.

---

## 2. Register the group structure

```bash
# Create the ultimate parent
PARENT=$(curl -s -X POST http://localhost:8000/entities \
  -H "Content-Type: application/json" \
  -d '{"name": "ParentCo"}')
echo $PARENT | jq .
PARENT_ID=$(echo $PARENT | jq -r .entity_id)

# Create a 100%-owned subsidiary
SUB_A=$(curl -s -X POST http://localhost:8000/entities \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"SubsidiaryA\", \"parent_entity_id\": \"$PARENT_ID\", \"ownership_pct\": 100}")
echo $SUB_A | jq .
SUB_A_ID=$(echo $SUB_A | jq -r .entity_id)

# Create a 75%-owned subsidiary (will produce NCI entries)
SUB_B=$(curl -s -X POST http://localhost:8000/entities \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"SubsidiaryB\", \"parent_entity_id\": \"$PARENT_ID\", \"ownership_pct\": 75}")
echo $SUB_B | jq .
SUB_B_ID=$(echo $SUB_B | jq -r .entity_id)

# Inspect the ownership tree
curl -s http://localhost:8000/entities/tree | jq .
```

---

## 3. Create a reporting period

```bash
PERIOD=$(curl -s -X POST http://localhost:8000/periods \
  -H "Content-Type: application/json" \
  -d '{"label": "FY-2024", "period_start": "2024-01-01", "period_end": "2024-12-31"}')
echo $PERIOD | jq .
PERIOD_ID=$(echo $PERIOD | jq -r .period_id)
```

---

## 4. Create trial balance CSV files

**`parent.csv`**
```csv
account_code,amount
1100,500000
INVEST_SUB,200000
INTERCO_REC,50000
```

**`sub_a.csv`**
```csv
account_code,amount
1100,100000
2100,-80000
EQUITY_SHARE_CAP,-200000
INTERCO_PAY,-50000
```

**`sub_b.csv`** *(75%-owned — will generate NCI)*
```csv
account_code,amount
1100,80000
2100,-20000
EQUITY_SHARE_CAP,-80000
DIVIDEND_PAID,10000
```

---

## 5. Ingest trial balances

```bash
curl -s -X POST "http://localhost:8000/ingest/ParentCo?period_id=$PERIOD_ID" \
  -F "file=@parent.csv" | jq .

curl -s -X POST "http://localhost:8000/ingest/SubsidiaryA?period_id=$PERIOD_ID" \
  -F "file=@sub_a.csv" | jq .

curl -s -X POST "http://localhost:8000/ingest/SubsidiaryB?period_id=$PERIOD_ID" \
  -F "file=@sub_b.csv" | jq .
```

Each call returns an `UploadSummary` with `mapped_count` and `entries_committed`.

---

## 6. Run consolidation

```bash
curl -s -X POST "http://localhost:8000/consolidate/$PERIOD_ID" | jq .
```

Expected response:
```json
{
  "period_id": "...",
  "eliminations_created": 6,
  "warnings": []
}
```

`warnings` lists any entity that submitted no entries for the period.

---

## 7. Get the consolidated report

```bash
curl -s "http://localhost:8000/report/$PERIOD_ID" | jq .
```

What to look for in the response:

| Field | What it shows |
|-------|--------------|
| `balance_sheet.equity.NCI_EQUITY` | SubsidiaryB's 25% minority share |
| `balance_sheet.equity.EQUITY` | Eliminated subsidiary equity (parent share) |
| `eliminations_summary` | One entry per elimination: `interco_receivable`, `interco_payable`, `equity_investment`, `equity_subsidiary`, `nci_equity` |
| `warnings` | Empty if all three entities submitted |

---

## 8. Lock the period

```bash
curl -s -X POST "http://localhost:8000/periods/$PERIOD_ID/lock" | jq .
```

Verify that ingestion is now blocked:

```bash
curl -s -X POST "http://localhost:8000/ingest/SubsidiaryA?period_id=$PERIOD_ID" \
  -F "file=@sub_a.csv" | jq .
# → {"detail": "Reporting period 'FY-2024' is locked; ingestion is not allowed."}
```

---

## 9. View all periods

```bash
curl -s http://localhost:8000/periods | jq .
```

---

## Swagger UI

All steps above are also available at **http://localhost:8000/docs** — no curl needed.
