#!/usr/bin/env bash
set -u

APP_URL="http://localhost:8000/status"
TIMEOUT=30

printf "Waiting for server at %s...\n" "$APP_URL"
ready=0
for i in $(seq 1 $TIMEOUT); do
    if curl -sSf "$APP_URL" >/dev/null 2>&1; then
        ready=1
        break
    fi
    sleep 1
done

if [[ $ready -ne 1 ]]; then
    echo "Server did not become ready within ${TIMEOUT}s."
    echo "Report Card: FAILED"
    exit 1
fi

echo "Server is online. Running pytest..."
if pytest; then
    echo "Report Card: PASSED"
    exit 0
else
    status=$?
    echo "Report Card: FAILED"
    exit "$status"
fi
