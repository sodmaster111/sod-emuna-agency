FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY tg_gateway/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY tg_gateway /app/tg_gateway

EXPOSE 7000

CMD ["python", "-m", "tg_gateway.bot.main"]
