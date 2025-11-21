# Coolify Deployment — Frontend (Next.js)

Deploy the standalone frontend app via Coolify using the Dockerfile build pack.

## Build configuration
- **Base directory:** `/frontend`
- **Dockerfile path:** `/frontend/Dockerfile`
- **Exposed port:** `3000`
- **Domain:** `https://www.sodmaster.online`

## Environment variables
Set these in the Coolify UI for the app:
- `NEXT_PUBLIC_BACKEND_URL=https://api.sodmaster.online`
- `NEXT_PUBLIC_TG_GATEWAY_URL=https://tg.sodmaster.online`
- `NEXT_PUBLIC_WA_GATEWAY_URL=https://wa.sodmaster.online`

## Traefik labels
Add the following labels in Coolify:
```
traefik.enable=true
traefik.http.routers.front.rule=Host(`www.sodmaster.online`)
traefik.http.routers.front.entryPoints=https
traefik.http.routers.front.tls.certresolver=myresolver
traefik.http.services.front.loadbalancer.server.port=3000
```
