# Telegram Gateway Service

A lightweight aiogram-based bot that forwards Telegram commands to the core backend via HTTP.

## Environment variables
- `TELEGRAM_BOT_TOKEN` – bot token from BotFather (required).
- `BACKEND_BASE_URL` – base URL of the core backend (defaults to `http://localhost:8000`).
- `GATEWAY_REQUEST_TIMEOUT` – HTTP timeout in seconds (defaults to 15).

## Running locally
Install dependencies and start polling:

```bash
pip install -r requirements.txt
python -m telegram_gateway.main
```

Supported commands:
- `/schedule <task>` – submit a new task via `/commands/schedule`.
- `/status <task_id>` – check the task status via `/commands/status/{task_id}`.
- `/logs [limit]` – fetch recent Pinkas entries via `/pinkas`.
