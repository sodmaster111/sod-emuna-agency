FROM python:3.11-slim

WORKDIR /app

COPY sod/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY sod /app/sod

CMD ["uvicorn", "sod.main:app", "--host", "0.0.0.0", "--port", "8000"]
