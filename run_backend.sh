#!/usr/bin/env bash
set -euo pipefail

# Defaults for local debugging; override as needed.
export DATABASE_URL="${DATABASE_URL:-sqlite+aiosqlite:///./app.db}"
export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
export OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://localhost:11434}"
export MISSION_GOAL="${MISSION_GOAL:-Grow the Digital Sanhedrin's assets while remaining halachically and ethically compliant.}"
export PYTHONPATH="${PYTHONPATH:-.}"

uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
