FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL="sqlite+aiosqlite:///./app.db" \
    REDIS_URL="redis://localhost:6379/0" \
    OLLAMA_BASE_URL="http://localhost:11434" \
    MISSION_GOAL="Grow the Digital Sanhedrin's assets while remaining halachically and ethically compliant."

RUN apt-get update && apt-get install -y git curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m playwright install-deps chromium && playwright install chromium

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
