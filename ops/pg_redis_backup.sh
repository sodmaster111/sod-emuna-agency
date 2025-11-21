#!/usr/bin/env bash
set -euo pipefail

# Daily logical backup for Postgres and optional Redis RDB snapshot.
# Required env vars:
#   PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE
#   REDIS_HOST, REDIS_PORT (optional if Redis not used)
#   BACKUP_DIR (e.g. /var/backups/sod)
# Optional S3 env vars for upload (stubbed):
#   AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, S3_BUCKET

if [[ -z "${BACKUP_DIR:-}" ]]; then
  echo "BACKUP_DIR is required" >&2
  exit 1
fi

# Verify postgres env vars
required_pg_vars=(PGHOST PGPORT PGUSER PGPASSWORD PGDATABASE)
for var in "${required_pg_vars[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    echo "Missing required env var: $var" >&2
    exit 1
  fi
done

DATE_PREFIX=$(date +%Y%m%d)
TIMESTAMP=$(date +%Y%m%d-%H%M)
TARGET_DIR="$BACKUP_DIR/$DATE_PREFIX"
mkdir -p "$TARGET_DIR"

# Postgres logical backup
PG_FILE="$TARGET_DIR/postgres-$TIMESTAMP.sql.gz"
echo "[INFO] Starting Postgres pg_dump to $PG_FILE"
export PGHOST PGPORT PGUSER PGPASSWORD PGDATABASE
pg_dump --format=p | gzip > "$PG_FILE"
echo "[INFO] Postgres backup complete"

# Redis snapshot if redis-cli exists
if command -v redis-cli >/dev/null 2>&1; then
  if [[ -n "${REDIS_HOST:-}" && -n "${REDIS_PORT:-}" ]]; then
    echo "[INFO] Triggering Redis SAVE"
    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" save
    REDIS_SOURCE="$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" config get dir | awk 'NR==2')/dump.rdb"
    if [[ -f "$REDIS_SOURCE" ]]; then
      REDIS_FILE="$TARGET_DIR/redis-$TIMESTAMP.rdb"
      cp "$REDIS_SOURCE" "$REDIS_FILE"
      echo "[INFO] Redis snapshot copied to $REDIS_FILE"
    else
      echo "[WARN] Redis dump.rdb not found at $REDIS_SOURCE" >&2
    fi
  else
    echo "[INFO] REDIS_HOST/REDIS_PORT not set; skipping Redis backup"
  fi
else
  echo "[INFO] redis-cli not installed; skipping Redis backup"
fi

# Optional S3 upload stub
# Uncomment and ensure aws cli is installed to enable
# if [[ -n "${S3_BUCKET:-}" ]]; then
#   echo "[INFO] Uploading backups to s3://$S3_BUCKET"
#   for FILE in "$TARGET_DIR"/*; do
#     aws s3 cp "$FILE" "s3://$S3_BUCKET/$(basename "$FILE")"
#   done
# fi

echo "[INFO] Backup process finished"
