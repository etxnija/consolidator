# Backup and Restore — Consolidator PostgreSQL

## Overview

Backups are `pg_dump` custom-format (`.dump`) files — compressed, split-capable,
and restoreable via `pg_restore`. Three scripts live in `scripts/`:

| Script | Purpose |
|---|---|
| `scripts/backup.sh` | Create a timestamped backup, apply retention policy |
| `scripts/restore.sh` | Restore a backup to the live database |
| `scripts/test-restore.sh` | End-to-end test: backup → restore to temp container → verify |

---

## Prerequisites

- PostgreSQL client tools on PATH: `pg_dump`, `pg_restore`, `psql`, `pg_isready`
- For `test-restore.sh`: `docker` or `podman` available
- For alembic step in `restore.sh`: `alembic` installed (`pip install alembic`)

---

## Environment Variables

All scripts read credentials from the environment — **never hardcoded**.

| Variable | Default | Description |
|---|---|---|
| `POSTGRES_USER` | `consolidator` | Database user |
| `POSTGRES_DB` | `consolidator` | Database name |
| `POSTGRES_PASSWORD` | `consolidator` | Database password |
| `POSTGRES_HOST` | `localhost` | Database host |
| `POSTGRES_PORT` | `5432` | Database port |
| `BACKUP_RETAIN` | `7` | Number of dumps to keep (backup.sh only) |
| `BACKUP_DIR` | `backups/` | Directory for dump files |

In production, load these from `.env` or your secrets manager before running the
scripts. The `docker-compose.yml` sets them via `env_file: .env`.

---

## Running a Backup Manually

```bash
# From the repo root (source DB running via docker-compose)
source .env   # or export POSTGRES_HOST=localhost etc.
bash scripts/backup.sh
```

Output example:
```
[2026-03-30T18:00:00Z] Starting backup of database 'consolidator' on localhost:5432
[2026-03-30T18:00:02Z] Backup complete: backups/consolidator_20260330_180002.dump (4.2M)
[2026-03-30T18:00:02Z] No old backups to delete (1/7 slots used)
[2026-03-30T18:00:02Z] Backup job finished successfully
```

Dump files are written to `backups/` and named `consolidator_YYYYMMDD_HHMMSS.dump`.

### From outside the container (docker exec)

```bash
# Run pg_dump inside the postgres container, write dump to host via stdout
docker compose exec -T postgres \
    pg_dump -U consolidator -d consolidator -Fc \
  > backups/consolidator_$(date +%Y%m%d_%H%M%S).dump
```

---

## Setting Up a Cron Job

Add the following to your crontab (`crontab -e`) to run a backup every night at
02:00 UTC:

```cron
0 2 * * * cd /path/to/consolidator && bash scripts/backup.sh >> /var/log/consolidator-backup.log 2>&1
```

Or use the environment-sourcing form:

```cron
0 2 * * * set -a; . /path/to/consolidator/.env; set +a; cd /path/to/consolidator && bash scripts/backup.sh >> /var/log/consolidator-backup.log 2>&1
```

Verify the log after the first run to confirm credentials are resolving correctly.

---

## Restore Procedure

> **Warning:** `restore.sh` replaces all data in the target database.
> Ensure you have a recent backup before restoring to a production instance.

### Step-by-step

1. **Identify the backup file** to restore from:
   ```bash
   ls -lh backups/
   ```

2. **Stop application services** (optional but recommended for production):
   ```bash
   docker compose stop backend engine frontend
   ```

3. **Run restore.sh:**
   ```bash
   bash scripts/restore.sh backups/consolidator_20260330_180002.dump
   ```
   The script:
   - Drops all existing objects (`pg_restore --clean --if-exists`)
   - Restores data from the dump
   - Runs `alembic upgrade head` to ensure the schema is current

4. **Restart application services:**
   ```bash
   docker compose start backend engine frontend
   ```

5. **Verify integrity** (see below).

---

## Verifying Restore Integrity

After a restore, run these queries to spot-check data:

```sql
-- Connect to the restored database
psql -h localhost -U consolidator -d consolidator

-- Check row counts
SELECT COUNT(*) FROM entity_metadata;
SELECT COUNT(*) FROM reporting_periods;
SELECT COUNT(*) FROM ledger_entries;

-- Check alembic migration state
SELECT version_num FROM alembic_version;

-- Spot-check a few entities
SELECT id, name, currency FROM entity_metadata LIMIT 5;
```

If row counts are non-zero and alembic version matches your expected migration,
the restore is complete.

---

## Testing the Restore Procedure

`test-restore.sh` provides automated end-to-end verification without touching the
live database:

```bash
bash scripts/test-restore.sh
```

It:
1. Takes a `pg_dump` from the running database
2. Starts a fresh temporary PostgreSQL container on port 54321
3. Restores the dump into it
4. Runs sanity queries (row counts on all tables, alembic_version check)
5. Tears down the container (even on failure)
6. Exits non-zero if any step fails

Run this before and after schema migrations, major upgrades, or when validating
backup files.

---

## Backup Rotation

`backup.sh` automatically deletes old dumps. By default it keeps the **7 most
recent** files. Change the retention count:

```bash
BACKUP_RETAIN=14 bash scripts/backup.sh
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `pg_dump: error: connection to server failed` | Wrong host/port or DB not running | Check `POSTGRES_HOST`, `POSTGRES_PORT`; verify `docker compose ps` |
| `pg_restore: error: role does not exist` | Dump contains ownership statements for a role that doesn't exist in target | Add `--no-owner --no-acl` to the `pg_restore` call in `restore.sh` |
| `alembic upgrade head` fails | Python env not active or `alembic` not installed | Run `pip install -r backend/requirements.txt` or activate your virtualenv |
| `test-restore.sh` port conflict | Port 54321 in use | Change `TEST_PORT` at the top of the script |
| Empty dump file | `pg_dump` ran but DB is empty | Normal for a fresh install; confirm the source DB has data |
