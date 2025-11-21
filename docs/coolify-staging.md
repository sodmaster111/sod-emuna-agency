# Coolify Staging Environment — sodmaster.online

This guide documents how to provision the **staging** environment in Coolify, cloned from production but with isolated data and endpoints.

## Staging domains
- `https://api-staging.sodmaster.online`
- `https://www-staging.sodmaster.online`
- `https://tg-staging.sodmaster.online`
- `https://wa-staging.sodmaster.online`
- `https://ton-staging.sodmaster.online`

## Environment differences
Use this matrix to align environment variables when cloning each app.

| Component | Production | Staging |
| --- | --- | --- |
| Backend | `ENVIRONMENT=production`<br>`DATABASE_URL=postgres://.../sod`<br>`REDIS_URL=redis://.../0` | `ENVIRONMENT=staging`<br>`DATABASE_URL=postgres://<staging-postgres>/sod_staging`<br>`REDIS_URL=redis://<staging-redis>/0` |
| Frontend | `NEXT_PUBLIC_BACKEND_URL=https://api.sodmaster.online` | `NEXT_PUBLIC_BACKEND_URL=https://api-staging.sodmaster.online` |
| TG gateway | Backend URL: `https://api.sodmaster.online`<br>Prod tokens | Backend URL: `https://api-staging.sodmaster.online`<br>Sandbox tokens where available |
| WA gateway | Backend URL: `https://api.sodmaster.online`<br>Prod tokens | Backend URL: `https://api-staging.sodmaster.online`<br>Sandbox tokens where available |
| TON service | Backend URL: `https://api.sodmaster.online`<br>Prod tokens | Backend URL: `https://api-staging.sodmaster.online`<br>Sandbox/testnet keys where available |

## Traefik label example (backend)
Apply the labels below to the staging backend service in Coolify:

```
traefik.enable=true
traefik.http.routers.api-staging.rule=Host(`api-staging.sodmaster.online`)
traefik.http.routers.api-staging.entryPoints=https
traefik.http.routers.api-staging.tls.certresolver=myresolver
traefik.http.services.api-staging.loadbalancer.server.port=8001
```

## Database and Redis
- Create a **new PostgreSQL database** instance in Coolify for staging with database name **`sod_staging`**.
- Create a **new Redis instance** in Coolify dedicated to staging and point all staging apps to it.

## Coolify UI checklist
1. Duplicate each production app into the **staging** environment (backend, frontend, tg, wa, ton).
2. Update domains to the staging hosts listed above.
3. Point backend `DATABASE_URL` to the staging Postgres instance (`sod_staging`) and `REDIS_URL` to the staging Redis instance; set `ENVIRONMENT=staging`.
4. Update frontend `NEXT_PUBLIC_BACKEND_URL` to the staging API URL.
5. Update TG/WA/TON services to call the staging backend and swap in sandbox tokens/keys.
6. Apply the Traefik labels (example above) to the backend and equivalent host rules for the other services.
7. Deploy each app and verify TLS via `*.staging.sodmaster.online`.
