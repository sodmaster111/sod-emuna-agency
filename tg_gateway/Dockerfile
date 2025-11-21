FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY tg_gateway/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY tg_gateway /app/tg_gateway

EXPOSE 7000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=10s \
    CMD curl -f http://localhost:7000/api/status || exit 1

CMD ["python", "-m", "tg_gateway.bot.main"]
