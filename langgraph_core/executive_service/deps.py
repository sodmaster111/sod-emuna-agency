"""Dependency helpers for the executive service."""

from .graph import compiled_graph


def get_graph():
    """Return the compiled LangGraph instance."""

    return compiled_graph
