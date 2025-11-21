# SOD Command Center Frontend

A Next.js 14 dashboard for monitoring the Digital Sanhedrin and dispatching commands to the orchestrator backend.

## Getting started

1. Install dependencies (Node 18+):

```bash
npm install
```

2. Create an environment file:

```bash
cp .env.example .env.local
```

3. Run the dev server:

```bash
npm run dev
```

The app expects the backend on port `8000` in development. Configure `NEXT_PUBLIC_BACKEND_URL` if the backend is hosted elsewhere.

## Production

```bash
npm run build
npm start
```

The included `Dockerfile` builds a production image for deployment behind the shared nginx proxy on `sodmaster.online`.

### Docker Compose service snippet

Use this service definition in the root `docker-compose.yml` (or your deployment stack) to run the frontend with the expected environment and proxy labels:

```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
  restart: unless-stopped
  environment:
    - NODE_ENV=production
    - NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL}
    - NEXT_PUBLIC_TG_GATEWAY_URL=${NEXT_PUBLIC_TG_GATEWAY_URL}
    - NEXT_PUBLIC_WA_GATEWAY_URL=${NEXT_PUBLIC_WA_GATEWAY_URL}
    - VIRTUAL_HOST=www.sodmaster.online
    - LETSENCRYPT_HOST=www.sodmaster.online
    - LETSENCRYPT_EMAIL=${LETSENCRYPT_EMAIL}
  ports:
    - "3000:3000"
  depends_on:
    - backend
```
