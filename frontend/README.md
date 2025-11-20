# SOD Command Center Frontend

A Next.js 14 dashboard for monitoring the Digital Sanhedrin and dispatching commands to the orchestrator backend.

## Getting started

1. Install dependencies (Node 18+):

```bash
npm install
```

2. Create an environment file:

```bash
cp .env.local.example .env.local
```

3. Run the dev server:

```bash
npm run dev
```

The app expects the FastAPI backend on port `8000`. Configure `NEXT_PUBLIC_API_BASE_URL` if the backend is hosted elsewhere.

## Production

```bash
npm run build
npm start
```

The included `Dockerfile` builds a production image and is wired into `docker-compose.yml` for Traefik-based routing on `sodmaster.online`.
