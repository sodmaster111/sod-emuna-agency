FROM python:3.11-slim

WORKDIR /app

COPY sod/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY sod .

EXPOSE 8000

CMD ["uvicorn", "agency:app", "--host", "0.0.0.0", "--port", "8000"]
