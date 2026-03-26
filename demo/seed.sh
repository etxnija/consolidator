#!/usr/bin/env bash
# demo/seed.sh — Seed a fresh stack with a 3-entity consolidation group and run FY-2024.
#
# Usage:  bash demo/seed.sh [BASE_URL]
# Default BASE_URL: http://localhost:8000
#
# Requires: curl, jq, sed, mktemp (all standard on macOS and modern Linux)
set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

die() { echo "ERROR: $*" >&2; exit 1; }

check_deps() {
  for cmd in curl jq sed mktemp; do
    command -v "$cmd" >/dev/null 2>&1 || die "Required command not found: $cmd"
  done
}

wait_healthy() {
  local url="$BASE_URL/health"
  local max=20 attempt=0
  echo "Waiting for backend at $url ..."
  until curl -sf "$url" >/dev/null 2>&1; do
    attempt=$((attempt + 1))
    [ $attempt -ge $max ] && die "Backend not healthy after ${max} attempts"
    sleep 1
  done
  echo "Backend is healthy."
}

post_json() {
  # post_json <path> <json-body>
  local path="$1" body="$2"
  curl -sf -X POST "$BASE_URL$path" \
    -H "Content-Type: application/json" \
    -d "$body"
}

# ---------------------------------------------------------------------------
# 1. Pre-flight
# ---------------------------------------------------------------------------

check_deps
wait_healthy

# ---------------------------------------------------------------------------
# 2. Create entities
# ---------------------------------------------------------------------------

echo ""
echo "==> Creating entities..."

PARENT=$(post_json /entities '{"name":"ParentCo"}')
PARENT_ID=$(echo "$PARENT" | jq -r '.entity_id')
echo "  ParentCo: $PARENT_ID"

SUB_A=$(post_json /entities "{\"name\":\"SubA\",\"parent_entity_id\":\"$PARENT_ID\",\"ownership_pct\":100}")
SUB_A_ID=$(echo "$SUB_A" | jq -r '.entity_id')
echo "  SubA (100%): $SUB_A_ID"

SUB_B=$(post_json /entities "{\"name\":\"SubB\",\"parent_entity_id\":\"$PARENT_ID\",\"ownership_pct\":75}")
SUB_B_ID=$(echo "$SUB_B" | jq -r '.entity_id')
echo "  SubB (75%): $SUB_B_ID"

# ---------------------------------------------------------------------------
# 3. Create reporting period
# ---------------------------------------------------------------------------

echo ""
echo "==> Creating period FY-2024..."

PERIOD=$(post_json /periods '{"label":"FY-2024","period_start":"2024-01-01","period_end":"2024-12-31"}')
PERIOD_ID=$(echo "$PERIOD" | jq -r '.period_id')
echo "  Period: $PERIOD_ID"

# ---------------------------------------------------------------------------
# 4. Substitute UUID placeholders and ingest CSVs
# ---------------------------------------------------------------------------

echo ""
echo "==> Ingesting trial balances..."

TMPDIR_WORK=$(mktemp -d)
trap 'rm -rf "$TMPDIR_WORK"' EXIT

ingest() {
  # ingest <entity-name> <csv-template-path>
  local entity="$1" src="$2"
  local tmp="$TMPDIR_WORK/${entity}.csv"

  sed \
    -e "s/PARENT_UUID/$PARENT_ID/g" \
    -e "s/SUB_A_UUID/$SUB_A_ID/g" \
    -e "s/SUB_B_UUID/$SUB_B_ID/g" \
    "$src" > "$tmp"

  local result
  result=$(curl -sf -X POST "$BASE_URL/ingest/$entity?period_id=$PERIOD_ID" \
    -F "file=@${tmp};type=text/csv")
  local mapped unmapped
  mapped=$(echo "$result" | jq -r '.entries_committed')
  unmapped=$(echo "$result" | jq -r '.unmapped_count')
  echo "  $entity: ${mapped} entries committed, ${unmapped} unmapped"
  [ "$unmapped" -gt 0 ] && echo "    Unmapped codes: $(echo "$result" | jq -r '.unmapped_codes[]')"
}

ingest "ParentCo" "$SCRIPT_DIR/parent.csv"
ingest "SubA"     "$SCRIPT_DIR/sub_a.csv"
ingest "SubB"     "$SCRIPT_DIR/sub_b.csv"

# ---------------------------------------------------------------------------
# 5. Run consolidation
# ---------------------------------------------------------------------------

echo ""
echo "==> Running consolidation for FY-2024..."

CONSOL=$(post_json "/consolidate/$PERIOD_ID" '{}')
ELIM_COUNT=$(echo "$CONSOL" | jq -r '.eliminations_created')
echo "  Eliminations created: $ELIM_COUNT"

WARNINGS=$(echo "$CONSOL" | jq -r '.warnings[]' 2>/dev/null || true)
[ -n "$WARNINGS" ] && echo "  Warnings: $WARNINGS"

# ---------------------------------------------------------------------------
# 6. Verify acceptance criteria
# ---------------------------------------------------------------------------

echo ""
echo "==> Verifying report..."

REPORT=$(curl -sf "$BASE_URL/report/$PERIOD_ID")
NCI=$(echo "$REPORT" | jq -r '.balance_sheet.equity.NCI_EQUITY // "0"')

echo "  NCI_EQUITY: $NCI"
echo "  Elimination entries: $ELIM_COUNT"

if python3 -c "exit(0 if float('$NCI') > 0 else 1)" 2>/dev/null; then
  echo "  [PASS] NCI_EQUITY > 0"
else
  echo "  [WARN] NCI_EQUITY is not > 0 (got: $NCI)"
fi

if [ "$ELIM_COUNT" -ge 6 ]; then
  echo "  [PASS] eliminations >= 6"
else
  echo "  [WARN] only $ELIM_COUNT eliminations (expected >= 6)"
fi

# ---------------------------------------------------------------------------
# 7. Print report URL
# ---------------------------------------------------------------------------

echo ""
echo "================================================================"
echo "  Report URL: $BASE_URL/report/$PERIOD_ID"
echo "  Dashboard:  ${FRONTEND_URL:-http://localhost:8501}"
echo "================================================================"
