# Coolify Postgres & Redis Backups

This guide adds daily Postgres logical backups (and optional Redis RDB snapshots) suitable for Coolify deployments.

## Backup script

Place `ops/pg_redis_backup.sh` in the repository (already included). It expects these environment variables:

- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`
- `REDIS_HOST`, `REDIS_PORT` (optional; Redis skipped if unset or `redis-cli` missing)
- `BACKUP_DIR` (e.g., `/var/backups/sod`)
- Optional S3 (stubbed): `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`, `S3_BUCKET`

The script creates a date-based folder under `BACKUP_DIR`, runs `pg_dump | gzip` to `postgres-YYYYmmdd-HHMM.sql.gz`, triggers `redis-cli save`, copies `dump.rdb` to `redis-YYYYmmdd-HHMM.rdb`, and includes a commented `aws s3 cp` loop for uploads.

## Coolify: persisting Postgres data

1. In your Coolify project, open the Postgres service.
2. Go to **Persistent Storage** and add a mount:
   - **Container path:** `/var/lib/postgresql/data`
   - **Host path / volume name:** choose a stable host path or named volume (e.g., `postgres-data`).
3. Deploy the service so data and dumps survive restarts.

## Running backups via a Coolify Simple Docker Service

You can run the script on a schedule inside a small container:

1. Create a `Dockerfile` next to the script (example):
   ```Dockerfile
   FROM debian:stable-slim
   RUN apt-get update \
     && apt-get install -y --no-install-recommends postgresql-client redis-tools awscli ca-certificates \
     && rm -rf /var/lib/apt/lists/*
   WORKDIR /app
   COPY ops/pg_redis_backup.sh /app/pg_redis_backup.sh
   RUN chmod +x /app/pg_redis_backup.sh
   CMD ["/bin/sh", "-c", "crond -f -d 8"]
   ```
2. Add a crontab file (e.g., `ops/backup.cron`) with:
   ```
   0 2 * * * BACKUP_DIR=/var/backups/sod /app/pg_redis_backup.sh >> /var/log/backup.log 2>&1
   ```
   Copy it into the image and start `crond` (update `CMD` accordingly), or use Coolify Scheduled Tasks instead.
3. In Coolify, create a **Simple Docker Service** using this Dockerfile.
4. Mount a **Persistent Storage** volume to the container at your `BACKUP_DIR` (e.g., `/var/backups/sod`). This keeps backups on disk and makes them visible for Coolify imports.
5. Configure environment variables in the service to match your Postgres/Redis hosts and credentials.

### Using Coolify Scheduled Tasks

Instead of running cron inside the container, you can use Coolify's **Scheduled Tasks** on the Simple Docker Service:

1. Deploy the service with the script available and the `BACKUP_DIR` volume mounted.
2. Add a Scheduled Task with a cron expression like `0 2 * * *` and the command:
   ```
   /app/pg_redis_backup.sh
   ```
3. Ensure the task uses the same environment variables set on the service.

### Importing backups in Coolify

When `BACKUP_DIR` is mounted as **Persistent Storage**, the generated `.sql.gz` and `.rdb` files appear under the service's storage in Coolify. You can use the **Import Backups** UI on your Postgres service and point it to these files for restore operations.

## Optional S3 uploads

The script contains a commented loop using `aws s3 cp` to push each generated file to `s3://$S3_BUCKET/`. Uncomment it and set AWS credentials plus `S3_BUCKET` to enable offsite copies.
