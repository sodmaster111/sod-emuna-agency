from fastapi import FastAPI

from .agents import register_agents
from .router import router as mission_router


app = FastAPI(title="SOD Hebrew AI Agency")


@app.on_event("startup")
async def startup_event():
    register_agents()


@app.get("/", tags=["health"])
async def root():
    return {"status": "SOD Hebrew AI Agency is online"}


app.include_router(mission_router)
