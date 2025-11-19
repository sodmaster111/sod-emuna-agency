# SOD Core Infrastructure (Docker)

Эта папка содержит базовый стек для проекта SOD:

- Traefik — reverse proxy
- PostgreSQL — основная база данных
- Redis — кэш и очереди
- SOD Core API (FastAPI) — базовый сервис ядра

## Подготовка

Файл `docker-compose.yml` находится в этой директории. Скопируйте `.env.example` в `.env` и при необходимости обновите значения:

```bash
cp .env.example .env
```

## Запуск

```bash
docker compose up -d
```

После запуска:

- Traefik слушает порт 80
- SOD Core API доступен по адресу http://localhost/ (или по домену из `SOD_CORE_HOST`)

## Проверка

```bash
curl http://localhost/
curl http://localhost/health
```
