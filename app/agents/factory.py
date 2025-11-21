from dataclasses import dataclass
from typing import Dict, List

from app.agents.registry import AGENTS, TOTAL_AGENTS


@dataclass
class AgentProfile:
    key: str
    name: str
    role: str
    dna_prompt: str
    tools: List[str]


class AgentFactory:
    @staticmethod
    def get_agent(key: str):
        agent = AGENTS.get(key)
        if not agent:
            raise KeyError(f"Agent {key} not found")
        return agent

    @staticmethod
    def list_agents() -> List:
        return list(AGENTS.values())

    @staticmethod
    def to_model_payload(agent) -> Dict[str, str]:
        return {
            "name": agent.name,
            "role": agent.role,
            "dna_prompt": getattr(agent, "description", ""),
            "tools": list(agent.tools),
        }

    @staticmethod
    def total_agents() -> int:
        return TOTAL_AGENTS
