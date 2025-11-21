FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY ton_service/service ./service

RUN pip install --no-cache-dir fastapi "uvicorn[standard]" requests tonsdk

EXPOSE 7500

LABEL traefik.enable="true" \
      traefik.http.routers.ton.rule="Host(`ton.sodmaster.online`)" \
      traefik.http.routers.ton.entryPoints="https" \
      traefik.http.routers.ton.tls.certresolver="myresolver" \
      traefik.http.services.ton.loadbalancer.server.port="7500"

CMD ["uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "7500"]
