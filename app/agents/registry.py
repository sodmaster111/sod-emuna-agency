"""Registry containing the core SOD-EMUNA agency agents generated from Corporate DNA."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

from app.agents.base import BaseAgent
from app.agents.protocols import AgentRequest, AgentResponse
from app.agents.registry_data import CORPORATE_DNA
from app.schemas.dna import DNAEntry, DNARegistry


@dataclass
class PersonaAgent(BaseAgent):
    response_style: str

    async def run(self, agent_input: AgentRequest) -> AgentResponse:
        self.log_to_pinkas("run", detail=f"payload={agent_input.payload}")
        styled_result = f"{self.response_style}: {agent_input.payload}"
        return AgentResponse(
            agent=self.name,
            result=styled_result,
            response_style=self.response_style,
            metadata={"role": self.role, "tools": list(self.tools)},
        )


REQUIRED_CORE_AGENTS: set[str] = {
    "nasi",
    "av_beit_din",
    "chief_executive_officer",
    "chief_technology_officer",
    "chief_knowledge_officer",
    "chief_risk_officer",
    "strategist",
    "scholar",
    "evangelist",
    "editor",
    "designer",
    "researcher",
}


def _validate_corporate_dna() -> Dict[str, DNAEntry]:
    registry = DNARegistry.model_validate(CORPORATE_DNA).entries
    missing = REQUIRED_CORE_AGENTS.difference(registry.keys())
    if missing:
        raise ValueError(f"Missing required corporate DNA entries: {', '.join(sorted(missing))}")
    return registry


DNA_REGISTRY: Dict[str, DNAEntry] = _validate_corporate_dna()


def _response_style_from_entry(entry: DNAEntry) -> str:
    return f"{entry.archetype} voice"


def _build_agent(internal_name: str, dna_entry: DNAEntry) -> PersonaAgent:
    agent = PersonaAgent(
        name=dna_entry.display_name,
        role=dna_entry.role,
        description=dna_entry.dna_prompt,
        tools=dna_entry.tools,
        response_style=_response_style_from_entry(dna_entry),
        dna={
            "tribe": dna_entry.tribe,
            "archetype": dna_entry.archetype,
            "risk_profile": dna_entry.risk_profile,
            "ethics_notes": dna_entry.ethics_notes,
        },
    )
    return agent


AGENTS: Dict[str, PersonaAgent] = {key: _build_agent(key, entry) for key, entry in DNA_REGISTRY.items()}
TOTAL_AGENTS: int = len(AGENTS)
ALL_AGENT_KEYS = list(AGENTS.keys())
AGENTS_CONFIG = DNA_REGISTRY


def get_agent(internal_name: str) -> BaseAgent:
    normalized = internal_name.lower()
    if normalized not in AGENTS:
        raise KeyError(f"Agent '{internal_name}' is not registered")
    return AGENTS[normalized]


def list_agents() -> Dict[str, BaseAgent]:
    return dict(AGENTS)


__all__ = [
    "AGENTS",
    "AGENTS_CONFIG",
    "ALL_AGENT_KEYS",
    "TOTAL_AGENTS",
    "get_agent",
    "list_agents",
    "PersonaAgent",
]
