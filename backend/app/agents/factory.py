from typing import Any, Dict

from app.agents.registry import AGENT_REGISTRY


def get_agent_profile(agent_name: str) -> Dict[str, Any]:
    """Fetch agent configuration from registry."""
    if agent_name not in AGENT_REGISTRY:
        raise KeyError(f"Agent {agent_name} not found in registry")
    return AGENT_REGISTRY[agent_name]
