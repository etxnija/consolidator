#!/usr/bin/env bash
# test-restore.sh — End-to-end backup/restore verification.
#
# Procedure:
#   1. Create a backup from the running database.
#   2. Spin up a temporary PostgreSQL container.
#   3. Restore the backup into that container.
#   4. Run basic sanity queries to confirm data integrity.
#   5. Tear down the temporary container (always, even on failure).
#   6. Exit non-zero on any failure.
#
# Usage:
#   bash scripts/test-restore.sh
#
# Requirements:
#   - docker or podman on PATH (checked automatically)
#   - pg_dump / pg_restore / psql available
#   - Source DB running and accessible via POSTGRES_* env vars
#
# Environment variables (required or defaulted):
#   POSTGRES_USER     — source DB user     (default: consolidator)
#   POSTGRES_DB       — source DB name     (default: consolidator)
#   POSTGRES_PASSWORD — source DB password (default: consolidator)
#   POSTGRES_HOST     — source DB host     (default: localhost)
#   POSTGRES_PORT     — source DB port     (default: 5432)
#   BACKUP_DIR        — where test dump is written (default: backups/)

set -euo pipefail

# ── Configuration ──────────────────────────────────────────────────────────────
PGUSER="${POSTGRES_USER:-consolidator}"
PGDATABASE="${POSTGRES_DB:-consolidator}"
PGPASSWORD="${POSTGRES_PASSWORD:-consolidator}"
PGHOST="${POSTGRES_HOST:-localhost}"
PGPORT="${POSTGRES_PORT:-5432}"
BACKUP_DIR="${BACKUP_DIR:-$(dirname "$0")/../backups}"

export PGPASSWORD

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Temporary container configuration
TEST_CONTAINER="consolidator-test-restore-$$"
TEST_PORT="54321"
TEST_PGPASSWORD="testpassword$$"
TEST_PGUSER="$PGUSER"
TEST_PGDB="$PGDATABASE"

# ── Helpers ────────────────────────────────────────────────────────────────────
log()     { echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] $*"; }
die()     { log "ERROR: $*" >&2; exit 1; }
pass()    { log "PASS: $*"; }
fail()    { log "FAIL: $*" >&2; FAILURES=$(( FAILURES + 1 )); }

FAILURES=0

# ── Detect container runtime ───────────────────────────────────────────────────
if command -v docker &>/dev/null; then
    CONTAINER_CMD="docker"
elif command -v podman &>/dev/null; then
    CONTAINER_CMD="podman"
else
    die "Neither docker nor podman found on PATH — cannot run temporary container"
fi
log "Using container runtime: $CONTAINER_CMD"

# ── Cleanup trap ───────────────────────────────────────────────────────────────
cleanup() {
    log "Tearing down temporary container: ${TEST_CONTAINER}"
    "$CONTAINER_CMD" rm -f "$TEST_CONTAINER" &>/dev/null || true
    [[ -n "${TEST_DUMP_FILE:-}" && -f "${TEST_DUMP_FILE}" ]] && rm -f "$TEST_DUMP_FILE" || true
    log "Cleanup complete"
}
trap cleanup EXIT

# ── Step 1: Create a test backup ───────────────────────────────────────────────
log "=== Step 1: Creating test backup from source DB ==="
mkdir -p "$BACKUP_DIR"
BACKUP_DIR="$(cd "$BACKUP_DIR" && pwd)"
TIMESTAMP="$(date -u '+%Y%m%d_%H%M%S')"
TEST_DUMP_FILE="${BACKUP_DIR}/consolidator_test_${TIMESTAMP}.dump"

pg_dump \
    --host="$PGHOST" \
    --port="$PGPORT" \
    --username="$PGUSER" \
    --dbname="$PGDATABASE" \
    --format=custom \
    --no-password \
    --file="$TEST_DUMP_FILE" \
  || die "pg_dump failed"

[[ -s "$TEST_DUMP_FILE" ]] || die "Test dump is empty"
DUMP_SIZE="$(du -sh "$TEST_DUMP_FILE" | cut -f1)"
pass "Backup created: ${TEST_DUMP_FILE} (${DUMP_SIZE})"

# ── Step 2: Spin up temporary PostgreSQL container ─────────────────────────────
log "=== Step 2: Starting temporary PostgreSQL container ==="
"$CONTAINER_CMD" run -d \
    --name "$TEST_CONTAINER" \
    -e POSTGRES_USER="$TEST_PGUSER" \
    -e POSTGRES_DB="$TEST_PGDB" \
    -e POSTGRES_PASSWORD="$TEST_PGPASSWORD" \
    -p "${TEST_PORT}:5432" \
    postgres:16-alpine \
  || die "Failed to start test container"

log "Waiting for test container to be ready..."
READY=0
for i in $(seq 1 30); do
    if PGPASSWORD="$TEST_PGPASSWORD" pg_isready \
            --host=localhost --port="$TEST_PORT" \
            --username="$TEST_PGUSER" --dbname="$TEST_PGDB" &>/dev/null; then
        READY=1
        break
    fi
    sleep 1
done
[[ $READY -eq 1 ]] || die "Test container did not become ready within 30 seconds"
pass "Temporary container is ready on port ${TEST_PORT}"

# ── Step 3: Restore into temporary container ───────────────────────────────────
log "=== Step 3: Restoring backup into temporary container ==="
PGPASSWORD="$TEST_PGPASSWORD" pg_restore \
    --host=localhost \
    --port="$TEST_PORT" \
    --username="$TEST_PGUSER" \
    --dbname="$TEST_PGDB" \
    --clean \
    --if-exists \
    --no-password \
    "$TEST_DUMP_FILE" \
  || die "pg_restore failed"
pass "pg_restore completed successfully"

# ── Step 4: Sanity queries ─────────────────────────────────────────────────────
log "=== Step 4: Running sanity queries ==="

run_query() {
    local desc="$1"
    local sql="$2"
    local result
    result="$(PGPASSWORD="$TEST_PGPASSWORD" psql \
        --host=localhost \
        --port="$TEST_PORT" \
        --username="$TEST_PGUSER" \
        --dbname="$TEST_PGDB" \
        --no-password \
        --tuples-only \
        --command="$sql" 2>&1)" \
      || { fail "${desc}: query failed — ${result}"; return; }
    local trimmed
    trimmed="$(echo "$result" | tr -d '[:space:]')"
    pass "${desc}: ${trimmed}"
}

# Verify expected tables exist and are queryable
run_query "entity_metadata row count" \
    "SELECT COUNT(*) FROM entity_metadata;"

run_query "ledger_entries row count" \
    "SELECT COUNT(*) FROM ledger_entries;"

run_query "reporting_periods row count" \
    "SELECT COUNT(*) FROM reporting_periods;"

# Verify alembic_version table (migrations have been applied)
run_query "alembic_version present" \
    "SELECT version_num FROM alembic_version LIMIT 1;"

# ── Results ────────────────────────────────────────────────────────────────────
log "=== Test Results ==="
if [[ $FAILURES -gt 0 ]]; then
    die "${FAILURES} sanity check(s) failed — restore is NOT verified"
fi
pass "All sanity checks passed — restore procedure verified"
log "test-restore.sh completed successfully"
