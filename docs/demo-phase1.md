# Phase 1 Demo Runbook — North Star Consolidator

_Date: 2026-03-31_
_Platform: IFRS 10 financial consolidation — FastAPI + PostgreSQL + Podman_

---

## Prerequisites

- Podman and `podman compose` installed and working
- `curl` and `jq` available on PATH
- Working directory: `/Users/nils/gt/consolidator/mayor/rig` (all commands run from here)
- Demo CSV files present in `demo/`: `parent.csv`, `sub_a.csv`, `sub_b.csv`

---

## Overview

This runbook demonstrates the 11 Phase 1 gate criteria end-to-end:

1. Stack startup and health
2. User registration with JWT
3. Login and token confirmation
4. Entity creation (ParentCo, SubA 100%, SubB 75%)
5. Reporting period creation (FY-2026)
6. CSV ingestion for all three entities
7. IFRS 10 consolidation run
8. Consolidated report — confirm NCI_EQUITY > 0
9. Tenant isolation — second user sees no data
10. pg_dump backup
11. Health degradation when DB is stopped

---

## Step 1 — Stack Startup

**Description:** Build all images from source and start the four services
(postgres, backend, engine, frontend) in detached mode. Then poll the health
endpoint until the backend confirms the database is reachable.

Services and ports (from `docker-compose.yml`):

| Service  | Exposed port |
|----------|-------------|
| backend  | 8000        |
| frontend | 8501        |
| postgres | internal only |
| engine   | internal only (8001) |

```bash
cd /Users/nils/gt/consolidator/mayor/rig

podman compose up --build -d
```

Expected output (abbreviated):

```
[+] Building ...
 ✔ backend  Built
 ✔ engine   Built
 ✔ frontend Built
[+] Running 4/4
 ✔ Container rig-postgres-1   Healthy
 ✔ Container rig-backend-1    Healthy
 ✔ Container rig-engine-1     Started
 ✔ Container rig-frontend-1   Started
```

**Health check** (wait up to 60 s for backend to be ready):

```bash
curl -s http://localhost:8000/health | jq .
```

Expected output:

```json
{
  "status": "ok",
  "db": "up"
}
```

If `db` is `"down"`, wait 10 seconds and retry — postgres may still be
completing its `start_period`.

---

## Step 2 — Register User

**Description:** Register the primary demo user. Because no `tenant_id` is
supplied, the backend generates a new UUID and embeds it in the returned JWT.
All subsequent resources created by this user belong to that tenant.

```bash
export TOKEN=$(curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "founder", "password": "Demo1234!"}' \
  | jq -r '.access_token')

echo "TOKEN=$TOKEN"
```

Expected output (the `access_token` is a signed HS256 JWT):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3ZjQ4YzNkMi0xYTJiLTQzNGUtOGE1Zi05YzJkZTFmNGE2MGIiLCJ1c2VybmFtZSI6ImZvdW5kZXIiLCJ0ZW5hbnRfaWQiOiJhMWIyYzNkNC1lNWY2LTc4OTAtYWJjZC1lZjAxMjM0NTY3ODkiLCJleHAiOjE3NTQ4NzYwMDB9.XsK2mRpLqT8vNwYjZcAeHdFbGiPlOuQrTyUvWxMnJkE",
  "token_type": "bearer"
}
```

After this step `$TOKEN` is set in your shell. Confirm it is non-empty:

```bash
echo $TOKEN | cut -c1-20
```

Expected: `eyJhbGciOiJIUzI1NiIs`

---

## Step 3 — Login

**Description:** Verify that existing credentials authenticate correctly and
return a fresh token. This confirms the bcrypt hash stored at registration is
valid and JWT signing works end-to-end.

```bash
export TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "founder", "password": "Demo1234!"}' \
  | jq -r '.access_token')

echo "Login OK — TOKEN starts with: $(echo $TOKEN | cut -c1-20)"
```

Expected output:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3ZjQ4YzNkMi0xYTJiLTQzNGUtOGE1Zi05YzJkZTFmNGE2MGIiLCJ1c2VybmFtZSI6ImZvdW5kZXIiLCJ0ZW5hbnRfaWQiOiJhMWIyYzNkNC1lNWY2LTc4OTAtYWJjZC1lZjAxMjM0NTY3ODkiLCJleHAiOjE3NTQ4NzYwMDB9.XsK2mRpLqT8vNwYjZcAeHdFbGiPlOuQrTyUvWxMnJkE",
  "token_type": "bearer"
}
```

A non-empty `access_token` confirms authentication is working.

---

## Step 4 — Create Entities

**Description:** Register the three-entity consolidation group. The entity
hierarchy is:

```
ParentCo (ultimate parent — no parent_entity_id, no ownership_pct)
├── SubA  (100% owned by ParentCo)
└── SubB  (75% owned by ParentCo — NCI = 25%)
```

The entity name is also the identifier used in the GCoA mapping table and as
the path parameter to the CSV ingest endpoint. Names must match exactly:
`ParentCo`, `SubA`, `SubB`.

### 4a — Create ParentCo

```bash
export PARENT_ID=$(curl -s -X POST http://localhost:8000/entities \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "ParentCo"}' \
  | jq -r '.entity_id')

echo "PARENT_ID=$PARENT_ID"
```

Expected output:

```json
{
  "entity_id": "a1b2c3d4-e5f6-7890-abcd-ef0123456789",
  "name": "ParentCo",
  "parent_entity_id": null,
  "ownership_pct": null
}
```

### 4b — Create SubA (100% owned)

```bash
export SUB_A_ID=$(curl -s -X POST http://localhost:8000/entities \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"SubA\", \"parent_entity_id\": \"$PARENT_ID\", \"ownership_pct\": 100}" \
  | jq -r '.entity_id')

echo "SUB_A_ID=$SUB_A_ID"
```

Expected output:

```json
{
  "entity_id": "b2c3d4e5-f6a7-8901-bcde-f01234567890",
  "name": "SubA",
  "parent_entity_id": "a1b2c3d4-e5f6-7890-abcd-ef0123456789",
  "ownership_pct": "100"
}
```

### 4c — Create SubB (75% owned — triggers NCI)

```bash
export SUB_B_ID=$(curl -s -X POST http://localhost:8000/entities \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"SubB\", \"parent_entity_id\": \"$PARENT_ID\", \"ownership_pct\": 75}" \
  | jq -r '.entity_id')

echo "SUB_B_ID=$SUB_B_ID"
```

Expected output:

```json
{
  "entity_id": "c3d4e5f6-a7b8-9012-cdef-012345678901",
  "name": "SubB",
  "parent_entity_id": "a1b2c3d4-e5f6-7890-abcd-ef0123456789",
  "ownership_pct": "75"
}
```

### 4d — Confirm all three entities

```bash
curl -s http://localhost:8000/entities \
  -H "Authorization: Bearer $TOKEN" | jq .
```

Expected output:

```json
[
  {
    "entity_id": "a1b2c3d4-e5f6-7890-abcd-ef0123456789",
    "name": "ParentCo",
    "parent_entity_id": null,
    "ownership_pct": null
  },
  {
    "entity_id": "b2c3d4e5-f6a7-8901-bcde-f01234567890",
    "name": "SubA",
    "parent_entity_id": "a1b2c3d4-e5f6-7890-abcd-ef0123456789",
    "ownership_pct": "100"
  },
  {
    "entity_id": "c3d4e5f6-a7b8-9012-cdef-012345678901",
    "name": "SubB",
    "parent_entity_id": "a1b2c3d4-e5f6-7890-abcd-ef0123456789",
    "ownership_pct": "75"
  }
]
```

---

## Step 5 — Create Reporting Period

**Description:** Create the FY-2026 annual period. The period enforces
`period_end > period_start` at the database level. Status starts as `open`,
which allows ingestion.

```bash
export PERIOD_ID=$(curl -s -X POST http://localhost:8000/periods \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"label": "FY-2026", "period_start": "2026-01-01", "period_end": "2026-12-31"}' \
  | jq -r '.period_id')

echo "PERIOD_ID=$PERIOD_ID"
```

Expected output:

```json
{
  "period_id": "d4e5f6a7-b8c9-0123-defa-123456789012",
  "label": "FY-2026",
  "period_start": "2026-01-01",
  "period_end": "2026-12-31",
  "status": "open"
}
```

---

## Step 6 — Upload CSV Trial Balances

**Description:** Upload the three demo CSVs from `demo/`. The ingest endpoint
path parameter is the entity **name** (not UUID) — it must match the name
registered in Step 4 exactly, because the GCoA mapping table is keyed by name.

The demo CSVs use account codes that are all registered in the GCoA map
(`gcoa_map.py`) under the `ParentCo`, `SubA`, and `SubB` sections. No
unmapped codes are expected for any of the three entities.

**Note on intercompany placeholders:** The CSV files contain placeholder values
`SUB_A_UUID`, `SUB_B_UUID`, and `PARENT_UUID` in the `counterparty_entity_id`
and `subsidiary_entity_id` columns. These are stored in the ledger metadata
for engine use. They do not affect ingestion or the mapped/unmapped count.

### 6a — Upload ParentCo trial balance

```bash
curl -s -X POST \
  "http://localhost:8000/ingest/ParentCo?period_id=$PERIOD_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@demo/parent.csv" \
  | jq .
```

Expected output:

```json
{
  "entity_id": "ParentCo",
  "total_rows": 10,
  "mapped_count": 10,
  "unmapped_count": 0,
  "unmapped_codes": [],
  "entries_committed": 10
}
```

### 6b — Upload SubA trial balance

```bash
curl -s -X POST \
  "http://localhost:8000/ingest/SubA?period_id=$PERIOD_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@demo/sub_a.csv" \
  | jq .
```

Expected output:

```json
{
  "entity_id": "SubA",
  "total_rows": 11,
  "mapped_count": 11,
  "unmapped_count": 0,
  "unmapped_codes": [],
  "entries_committed": 11
}
```

### 6c — Upload SubB trial balance

```bash
curl -s -X POST \
  "http://localhost:8000/ingest/SubB?period_id=$PERIOD_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@demo/sub_b.csv" \
  | jq .
```

Expected output:

```json
{
  "entity_id": "SubB",
  "total_rows": 13,
  "mapped_count": 13,
  "unmapped_count": 0,
  "unmapped_codes": [],
  "entries_committed": 13
}
```

All three uploads must show `unmapped_count: 0` and `entries_committed` equal
to `mapped_count`.

---

## Step 7 — Run Consolidation

**Description:** Trigger the IFRS 10 consolidation engine. The backend loads
all non-elimination ledger entries for the period, sends them to the engine
service (port 8001, internal), and persists the returned elimination journal
entries. The engine performs:

- Investment elimination (INVEST_SUB vs EQUITY_SHARE_CAP)
- Intercompany receivable/payable elimination (INTERCO_REC / INTERCO_PAY)
- Intercompany revenue/COGS elimination (INTERCO_REV / INTERCO_COGS)
- Dividend elimination (DIVIDEND_REC / DIVIDEND_PAID)
- NCI equity posting for SubB's 25% non-controlling interest

```bash
curl -s -X POST \
  "http://localhost:8000/consolidate/$PERIOD_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | jq .
```

Expected output:

```json
{
  "period_id": "d4e5f6a7-b8c9-0123-defa-123456789012",
  "eliminations_created": 12,
  "warnings": []
}
```

`eliminations_created` should be greater than 0 (typically 10–15 entries
covering all the intercompany eliminations and the NCI posting). An empty
`warnings` array confirms all three entities submitted data for this period.

---

## Step 8 — View Consolidated Report

**Description:** Retrieve the consolidated financial statements and verify that
`NCI_EQUITY` appears in the equity section of the balance sheet with a
positive value. NCI_EQUITY is generated by the engine to represent the 25%
minority interest in SubB's net assets (SubB equity = 200,000 + 107,500 =
307,500; NCI 25% = 76,875).

```bash
curl -s \
  "http://localhost:8000/report/$PERIOD_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | jq .
```

Expected output (abbreviated — amounts shown are representative):

```json
{
  "period": {
    "period_id": "d4e5f6a7-b8c9-0123-defa-123456789012",
    "label": "FY-2026",
    "period_start": "2026-01-01",
    "period_end": "2026-12-31",
    "status": "open"
  },
  "balance_sheet": {
    "assets": {
      "1100": "800000.00",
      "1200": "160000.00",
      "1300": "90000.00",
      "1500": "1300000.00"
    },
    "liabilities": {
      "2100": "-280000.00",
      "2500": "-600000.00"
    },
    "equity": {
      "EQUITY_SHARE_CAP": "-1000000.00",
      "3200": "-762500.00",
      "NCI_EQUITY": "-76875.00"
    }
  },
  "income_statement": {
    "revenue": {
      "4100": "-450000.00"
    },
    "cogs": {
      "5100": "550000.00"
    },
    "operating_expenses": {}
  },
  "eliminations_summary": [
    {
      "elimination_type": "investment",
      "entity_id": "a1b2c3d4-e5f6-7890-abcd-ef0123456789",
      "account_code": "INVEST_SUB",
      "amount": "-825000.00"
    },
    {
      "elimination_type": "interco_balance",
      "entity_id": "b2c3d4e5-f6a7-8901-bcde-f01234567890",
      "account_code": "INTERCO_PAY",
      "amount": "80000.00"
    },
    {
      "elimination_type": "interco_revenue",
      "entity_id": "b2c3d4e5-f6a7-8901-bcde-f01234567890",
      "account_code": "INTERCO_REV",
      "amount": "100000.00"
    },
    {
      "elimination_type": "nci",
      "entity_id": "c3d4e5f6-a7b8-9012-cdef-012345678901",
      "account_code": "NCI_EQUITY",
      "amount": "-76875.00"
    }
  ],
  "warnings": []
}
```

**Gate check:** `balance_sheet.equity.NCI_EQUITY` must be present and
non-zero. A value of approximately `-76875.00` (negative because equity is
credit-normal) confirms SubB's 25% NCI is correctly calculated.

To extract the NCI value directly:

```bash
curl -s \
  "http://localhost:8000/report/$PERIOD_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.balance_sheet.equity.NCI_EQUITY'
```

Expected output: `"-76875.00"` (or close, depending on engine rounding).

---

## Step 9 — Tenant Isolation

**Description:** Register a second user without supplying a `tenant_id`. The
backend generates a new, independent tenant UUID. When this second user
queries entities and periods, the results must be empty — proving that
tenant data is fully isolated via the JWT `tenant_id` claim.

### 9a — Register second user

```bash
export TOKEN2=$(curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "auditor", "password": "Audit9876!"}' \
  | jq -r '.access_token')

echo "TOKEN2 set: $(echo $TOKEN2 | cut -c1-20)"
```

Expected output:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4ZTU5ZDRlMy0yYjNjLTU0NWYtOWI2Zy0wZDNlZjJnNWI3MWMiLCJ1c2VybmFtZSI6ImF1ZGl0b3IiLCJ0ZW5hbnRfaWQiOiJmMGUxZDJjMy1iNGE1LTY3ODktYWJjZC0xMjM0NTY3ODkwMTIiLCJleHAiOjE3NTQ4NzYwMDB9.AbCdEfGhIjKlMnOpQrStUvWxYzAbCdEfGhIjKlMnOp",
  "token_type": "bearer"
}
```

### 9b — Confirm second tenant sees no entities

```bash
curl -s http://localhost:8000/entities \
  -H "Authorization: Bearer $TOKEN2" | jq .
```

Expected output:

```json
[]
```

### 9c — Confirm second tenant sees no periods

```bash
curl -s http://localhost:8000/periods \
  -H "Authorization: Bearer $TOKEN2" | jq .
```

Expected output:

```json
[]
```

Both responses must be empty arrays. Any non-empty result indicates a tenant
isolation failure and is a blocking issue.

---

## Step 10 — Backup

**Description:** Run the `pg_dump`-based backup script directly on the host.
The script reads PostgreSQL connection details from environment variables and
writes a compressed `.dump` file to `backups/`. It also enforces a retention
policy (default: keep the last 7 backups).

The backup script is at `scripts/backup.sh`. It requires PostgreSQL client
tools (`pg_dump`) installed on the host, or can be run inside a container
via `podman compose run --rm backup` (uses the `postgres:16-alpine` image
which includes `pg_dump`).

### Option A — Run via podman compose (recommended, no host pg_dump required)

```bash
cd /Users/nils/gt/consolidator/mayor/rig

podman compose --profile backup run --rm backup
```

Expected output:

```
[2026-03-31T14:00:00Z] Starting backup of database 'consolidator' on postgres:5432
[2026-03-31T14:00:02Z] Backup complete: /backups/consolidator_20260331_140000.dump (48K)
[2026-03-31T14:00:02Z] Applying retention policy: keep last 7 backups
[2026-03-31T14:00:02Z] No old backups to delete (1/7 slots used)
[2026-03-31T14:00:02Z] Backup job finished successfully
```

### Option B — Run directly on host (requires pg_dump on PATH)

```bash
cd /Users/nils/gt/consolidator/mayor/rig

POSTGRES_HOST=localhost \
POSTGRES_PORT=5432 \
POSTGRES_USER=consolidator \
POSTGRES_PASSWORD=consolidator \
POSTGRES_DB=consolidator \
BACKUP_DIR=./backups \
bash scripts/backup.sh
```

Expected output:

```
[2026-03-31T14:00:00Z] Starting backup of database 'consolidator' on localhost:5432
[2026-03-31T14:00:02Z] Backup complete: /Users/nils/gt/consolidator/mayor/rig/backups/consolidator_20260331_140000.dump (48K)
[2026-03-31T14:00:02Z] Applying retention policy: keep last 7 backups
[2026-03-31T14:00:02Z] No old backups to delete (1/7 slots used)
[2026-03-31T14:00:02Z] Backup job finished successfully
```

**Verify the file exists:**

```bash
ls -lh /Users/nils/gt/consolidator/mayor/rig/backups/consolidator_*.dump
```

Expected output:

```
-rw-r--r-- 1 nils staff 48K Mar 31 14:00 /Users/nils/gt/consolidator/mayor/rig/backups/consolidator_20260331_140000.dump
```

The dump must be non-zero in size. The script exits non-zero and logs an error
if `pg_dump` fails or if the output file is empty.

---

## Step 11 — Health Degradation

**Description:** Stop the postgres container to simulate a database outage.
The backend health endpoint must return HTTP 503 with `"db": "down"`. This
confirms the health check performs a real connectivity probe (not just a
static `{"status": "ok"}`). Restart postgres and confirm recovery.

### 11a — Stop the database

```bash
podman compose stop postgres
```

Expected output:

```
[+] Stopping 1/1
 ✔ Container rig-postgres-1  Stopped
```

### 11b — Hit the health endpoint — expect 503

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health
```

Expected output: `503`

To see the full response body:

```bash
curl -s http://localhost:8000/health | jq .
```

Expected output:

```json
{
  "status": "degraded",
  "db": "down",
  "detail": "could not connect to server: Connection refused\n\tIs the server running on host \"postgres\" (172.20.0.2) and accepting\n\tTCP/IP connections on port 5432?"
}
```

HTTP status code must be `503`. Any `200` here means the health endpoint is
not doing a real DB check and is a defect.

### 11c — Restart the database and confirm recovery

```bash
podman compose start postgres
```

Expected output:

```
[+] Running 1/1
 ✔ Container rig-postgres-1  Started
```

Wait ~15 seconds for postgres to become healthy, then confirm recovery:

```bash
sleep 15 && curl -s http://localhost:8000/health | jq .
```

Expected output:

```json
{
  "status": "ok",
  "db": "up"
}
```

---

## Sign-Off Checklist

The founder physically checks each box after observing the expected result.

- [ ] **Step 1** — `GET /health` returns `{"status": "ok", "db": "up"}` after stack startup
- [ ] **Steps 2–3** — Registration and login both return a non-empty `access_token`; subsequent authenticated requests succeed
- [ ] **Steps 4–6** — Three entities created; three CSVs ingested with `unmapped_count: 0`; second tenant's `GET /entities` returns `[]`
- [ ] **Step 7–8** — Consolidation runs without error; `GET /report` balance sheet contains `NCI_EQUITY` with a non-zero value
- [ ] **Step 10** — Backup script exits 0 and a non-empty `.dump` file is present in `backups/`
- [ ] **Step 11** — `GET /health` returns HTTP 503 with `"db": "down"` while postgres is stopped; recovers to 200 after restart

All six boxes checked = Phase 1 gate passed. Phase 2 may begin.

---

_Runbook written: 2026-03-31. Review and update after any backend schema or routing changes._
