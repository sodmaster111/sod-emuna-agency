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
    def get_agent(key: str) -> AgentProfile:
        agent_data = AGENTS.get(key)
        if not agent_data:
            raise KeyError(f"Agent {key} not found")
        return AgentProfile(
            key=key,
            name=agent_data["name"],
            role=agent_data.get("role", ""),
            dna_prompt=agent_data["dna_prompt"],
            tools=agent_data.get("tools", []),
        )

    @staticmethod
    def list_agents() -> List[AgentProfile]:
        return [AgentFactory.get_agent(key) for key in AGENTS]

    @staticmethod
    def to_model_payload(agent: AgentProfile) -> Dict[str, str]:
        return {
            "name": agent.name,
            "role": agent.role,
            "dna_prompt": agent.dna_prompt,
            "tools": agent.tools,
        }

    @staticmethod
    def total_agents() -> int:
        return TOTAL_AGENTS
