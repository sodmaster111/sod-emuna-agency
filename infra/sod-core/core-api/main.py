from fastapi import FastAPI

app = FastAPI(title="SOD Core API")


@app.get("/")
def read_root():
    return {"status": "SOD Core API is online"}


@app.get("/health")
def health_check():
    return {"health": "ok"}
