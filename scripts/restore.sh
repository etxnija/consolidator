#!/usr/bin/env bash
# restore.sh — Restore a pg_dump custom-format backup for the consolidator DB.
#
# Usage:
#   bash scripts/restore.sh <backup-file>
#
# Environment variables (required or defaulted):
#   POSTGRES_USER     — database user     (default: consolidator)
#   POSTGRES_DB       — database name     (default: consolidator)
#   POSTGRES_PASSWORD — database password (default: consolidator)
#   POSTGRES_HOST     — database host     (default: localhost)
#   POSTGRES_PORT     — database port     (default: 5432)
#
# The script drops all existing objects in the target database and restores
# from the dump, then runs `alembic upgrade head` to ensure the schema is
# current.

set -euo pipefail

# ── Configuration ──────────────────────────────────────────────────────────────
PGUSER="${POSTGRES_USER:-consolidator}"
PGDATABASE="${POSTGRES_DB:-consolidator}"
PGPASSWORD="${POSTGRES_PASSWORD:-consolidator}"
PGHOST="${POSTGRES_HOST:-localhost}"
PGPORT="${POSTGRES_PORT:-5432}"

export PGPASSWORD

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/../backend"

# ── Helpers ────────────────────────────────────────────────────────────────────
log() { echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] $*"; }
die() { log "ERROR: $*" >&2; exit 1; }

# ── Args ───────────────────────────────────────────────────────────────────────
BACKUP_FILE="${1:-}"
[[ -n "$BACKUP_FILE" ]] || die "Usage: $0 <backup-file>"
[[ -f "$BACKUP_FILE" ]] || die "Backup file not found: $BACKUP_FILE"
BACKUP_FILE="$(cd "$(dirname "$BACKUP_FILE")" && pwd)/$(basename "$BACKUP_FILE")"

log "Restoring '${PGDATABASE}' on ${PGHOST}:${PGPORT} from: ${BACKUP_FILE}"

# ── Restore ────────────────────────────────────────────────────────────────────
log "Running pg_restore (--clean --if-exists)..."
pg_restore \
    --host="$PGHOST" \
    --port="$PGPORT" \
    --username="$PGUSER" \
    --dbname="$PGDATABASE" \
    --clean \
    --if-exists \
    --no-password \
    --verbose \
    "$BACKUP_FILE" \
  || die "pg_restore failed"

log "pg_restore complete"

# ── Alembic migration ──────────────────────────────────────────────────────────
log "Running alembic upgrade head to ensure schema is current..."
if [[ -d "$BACKEND_DIR" ]]; then
    (
        cd "$BACKEND_DIR"
        DATABASE_URL="postgresql://${PGUSER}:${PGPASSWORD}@${PGHOST}:${PGPORT}/${PGDATABASE}" \
            alembic upgrade head
    ) || die "alembic upgrade head failed"
    log "Alembic migrations applied"
else
    log "WARNING: backend directory not found at ${BACKEND_DIR} — skipping alembic step"
fi

log "Restore complete. Database '${PGDATABASE}' is ready."
