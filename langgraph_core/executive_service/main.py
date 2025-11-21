"""FastAPI entrypoint for the executive LangGraph service."""
from fastapi import FastAPI
from pydantic import BaseModel

from .config import get_settings
from .deps import get_graph


class DecisionRequest(BaseModel):
    """Request model for executive decisions."""

    question: str
    context: dict | None = None


settings = get_settings()
app = FastAPI(title="SOD Executive LangGraph Service")


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""

    return {"status": "ok", "service": "executive-langgraph"}


@app.post("/exec/decide")
def exec_decide(payload: DecisionRequest) -> dict:
    """Run the executive LangGraph to produce a decision."""

    graph = get_graph()
    result = graph.invoke({"question": payload.question, "context": payload.context})
    return {
        "decision": result.get("decision"),
        "reasoning_summary": result.get("reasoning_summary"),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "langgraph_core.executive_service.main:app",
        host="0.0.0.0",
        port=settings.LANGGRAPH_EXEC_PORT,
        reload=True,
    )
