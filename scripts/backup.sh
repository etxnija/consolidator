#!/usr/bin/env bash
# backup.sh — pg_dump-based backup for the consolidator PostgreSQL database.
#
# Usage:
#   bash scripts/backup.sh
#
# Environment variables (required or defaulted):
#   POSTGRES_USER     — database user     (default: consolidator)
#   POSTGRES_DB       — database name     (default: consolidator)
#   POSTGRES_PASSWORD — database password (default: consolidator)
#   POSTGRES_HOST     — database host     (default: localhost)
#   POSTGRES_PORT     — database port     (default: 5432)
#   BACKUP_RETAIN     — number of backups to keep (default: 7)
#   BACKUP_DIR        — directory for dumps (default: backups/)
#
# The dump is written in PostgreSQL custom format (-Fc), which is compressed
# and supports selective restore via pg_restore.

set -euo pipefail

# ── Configuration ──────────────────────────────────────────────────────────────
PGUSER="${POSTGRES_USER:-consolidator}"
PGDATABASE="${POSTGRES_DB:-consolidator}"
PGPASSWORD="${POSTGRES_PASSWORD:-consolidator}"
PGHOST="${POSTGRES_HOST:-localhost}"
PGPORT="${POSTGRES_PORT:-5432}"
BACKUP_RETAIN="${BACKUP_RETAIN:-7}"
BACKUP_DIR="${BACKUP_DIR:-$(dirname "$0")/../backups}"

export PGPASSWORD

# ── Helpers ────────────────────────────────────────────────────────────────────
log() { echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] $*"; }
die() { log "ERROR: $*" >&2; exit 1; }

# ── Setup ──────────────────────────────────────────────────────────────────────
mkdir -p "$BACKUP_DIR"
BACKUP_DIR="$(cd "$BACKUP_DIR" && pwd)"

TIMESTAMP="$(date -u '+%Y%m%d_%H%M%S')"
DUMP_FILE="${BACKUP_DIR}/consolidator_${TIMESTAMP}.dump"

log "Starting backup of database '${PGDATABASE}' on ${PGHOST}:${PGPORT}"

# ── pg_dump ────────────────────────────────────────────────────────────────────
pg_dump \
    --host="$PGHOST" \
    --port="$PGPORT" \
    --username="$PGUSER" \
    --dbname="$PGDATABASE" \
    --format=custom \
    --no-password \
    --file="$DUMP_FILE" \
  || die "pg_dump failed — no backup written"

if [[ ! -s "$DUMP_FILE" ]]; then
    die "Dump file is empty: $DUMP_FILE"
fi

DUMP_SIZE="$(du -sh "$DUMP_FILE" | cut -f1)"
log "Backup complete: ${DUMP_FILE} (${DUMP_SIZE})"

# ── Retention ──────────────────────────────────────────────────────────────────
log "Applying retention policy: keep last ${BACKUP_RETAIN} backups"
# List dumps sorted oldest-first; delete anything beyond the retain count.
mapfile -t ALL_DUMPS < <(ls -1t "${BACKUP_DIR}"/consolidator_*.dump 2>/dev/null)
TOTAL="${#ALL_DUMPS[@]}"
DELETE_COUNT=$(( TOTAL - BACKUP_RETAIN ))

if (( DELETE_COUNT > 0 )); then
    for dump in "${ALL_DUMPS[@]: -$DELETE_COUNT}"; do
        log "Deleting old backup: ${dump}"
        rm -f "$dump"
    done
    log "Deleted ${DELETE_COUNT} old backup(s)"
else
    log "No old backups to delete (${TOTAL}/${BACKUP_RETAIN} slots used)"
fi

log "Backup job finished successfully"
