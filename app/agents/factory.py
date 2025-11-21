from dataclasses import dataclass
from dataclasses import dataclass
from typing import Dict, List

from app.agents.registry import TOTAL_AGENTS, get_agent, list_agents


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
        return get_agent(key)

    @staticmethod
    def list_agents() -> List:
        return list(list_agents().values())

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
