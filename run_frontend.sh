#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/frontend"
export NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:8000}"

npm install
npm run dev -- --hostname 0.0.0.0 --port "${PORT:-3000}"
