FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir boto3 pyyaml

COPY ops/backup_runner.py /ops/backup_runner.py
COPY ops/backup_config.example.yml /ops/backup_config.example.yml

ENV BACKUP_CONFIG=/ops/backup.yml

CMD ["python", "/ops/backup_runner.py"]
