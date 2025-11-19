# Emuna Agency

Emuna Agency is a lightweight Telegram service that shares short messages of אמונה, תהילים, תפילה וסגולה a few times a day. It avoids Shabbat and configured holidays, so you can schedule it safely on a Linux host.

## Setup

1. Create `config.json` (not committed) in the project root or under `config/` by copying `config/config.example.json` and filling in your Telegram bot token, chat ID, timezone, slots, and holidays.
2. Create `data/library.json` (not committed) by copying `data/library.example.json` and adjusting or expanding the content items.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running manually

Use Python's module flag to trigger a slot:
```bash
python -m src.agency morning
```
Slots available: `morning`, `noon`, `night`.

## Scheduling

For cron usage, see [ops/cron.md](ops/cron.md). A systemd service/timer example is provided at [ops/systemd.service.example](ops/systemd.service.example).

## Docker

SOD Emuna Agency is a FastAPI-powered service that exposes the `sod.main:app` application for running the project's API.

Build and run the Docker container locally:

```bash
docker build -t sod-emuna-agency .
docker run -p 8000:8000 sod-emuna-agency
```
