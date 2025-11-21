from langgraph_core.executive_service.deps import get_graph


class ExecServiceError(Exception):
    """Raised when the executive service cannot produce a decision."""


def exec_decide(question: str, context: dict | None = None) -> dict:
    """Run the executive service graph to produce a decision."""

    graph = get_graph()
    try:
        result = graph.invoke({"question": question, "context": context})
    except Exception as exc:  # pragma: no cover - pass-through to HTTP layer
        raise ExecServiceError(f"Executive service failed: {exc}") from exc

    return {
        "decision": result.get("decision"),
        "reasoning_summary": result.get("reasoning_summary"),
    }
