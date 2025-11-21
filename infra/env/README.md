# Environment configuration templates

This directory centralizes example environment files for all services. Copy each `*.example` file to its runtime `.env` counterpart before starting the stack.

## Files
- `.env.backend.example` → backend service
- `.env.frontend.example` → frontend (Next.js) service
- `.env.tg.example` → Telegram gateway
- `.env.wa.example` → WhatsApp gateway
- `.env.ton.example` → TON services

## Usage
1. Copy the example files to their working names:
   ```bash
   cp infra/env/.env.backend.example infra/env/.env.backend
   cp infra/env/.env.frontend.example infra/env/.env.frontend
   cp infra/env/.env.tg.example infra/env/.env.tg
   cp infra/env/.env.wa.example infra/env/.env.wa
   cp infra/env/.env.ton.example infra/env/.env.ton
   ```
2. Replace placeholder values (e.g., `CHANGE_ME`, secrets, and URLs) with real values.
3. Keep the `.env.*` files out of version control—do not commit live credentials.

## docker-compose integration (example)
Use the copied `.env` files via the `env_file` directive for each service:

```yaml
services:
  backend:
    # env_file loads settings from infra/env/.env.backend
    env_file:
      - ./infra/env/.env.backend

  frontend:
    # env_file loads settings from infra/env/.env.frontend
    env_file:
      - ./infra/env/.env.frontend

  telegram_gateway:
    # env_file loads settings from infra/env/.env.tg
    env_file:
      - ./infra/env/.env.tg

  whatsapp_gateway:
    # env_file loads settings from infra/env/.env.wa
    env_file:
      - ./infra/env/.env.wa

  ton_services:
    # env_file loads settings from infra/env/.env.ton
    env_file:
      - ./infra/env/.env.ton

  monitoring:
    # provide an env file if the monitoring stack needs one
    env_file:
      - ./infra/env/.env.monitoring
```

> Tip: The structure mirrors common secret managers, making future migration easier (e.g., mapping these keys into Vault or cloud secret stores).
