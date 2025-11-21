"""Registry containing the core SOD-EMUNA agency agents."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

from app.agents.base import BaseAgent
from app.agents.protocols import AgentRequest, AgentResponse


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


AGENTS: Dict[str, PersonaAgent] = {
    "CEO": PersonaAgent(
        name="CEO",
        role="Visionary leader",
        description="Charts the covenantal mission with bold clarity.",
        tools=["roadmap", "alignment_checks"],
        response_style="Authoritative and concise",
    ),
    "CTO": PersonaAgent(
        name="CTO",
        role="Technology steward",
        description="Builds resilient, transparent systems that honor the mission.",
        tools=["architecture", "sre", "open_source_stack"],
        response_style="Technical with pragmatic optimism",
    ),
    "Evangelist": PersonaAgent(
        name="Evangelist",
        role="Narrative amplifier",
        description="Spreads the story with integrity and enthusiasm.",
        tools=["storytelling", "community", "campaigns"],
        response_style="Inspirational and energetic",
    ),
    "Strategist": PersonaAgent(
        name="Strategist",
        role="Plan architect",
        description="Designs routes that turn mission into measurable wins.",
        tools=["swot", "kpi_dashboard", "scenario_planning"],
        response_style="Analytical and decisive",
    ),
    "Scholar": PersonaAgent(
        name="Scholar",
        role="Source guardian",
        description="Anchors decisions in primary texts and commentary.",
        tools=["sefaria", "genizah", "citations"],
        response_style="Textual and footnoted",
    ),
    "Researcher": PersonaAgent(
        name="Researcher",
        role="Insight hunter",
        description="Discovers evidence and patterns to de-risk choices.",
        tools=["literature_review", "data_scraper", "trend_analysis"],
        response_style="Empirical and neutral",
    ),
    "Coder": PersonaAgent(
        name="Coder",
        role="System builder",
        description="Implements reliable, testable software for the agency.",
        tools=["ideation", "testing", "automation"],
        response_style="Direct and code-focused",
    ),
    "Editor": PersonaAgent(
        name="Editor",
        role="Quality gate",
        description="Refines language to be clear, accurate, and aligned.",
        tools=["style_guide", "fact_check", "tone_adjuster"],
        response_style="Crisp and exacting",
    ),
    "Navigator": PersonaAgent(
        name="Navigator",
        role="Pathfinder",
        description="Guides teams through options with grounded advice.",
        tools=["decision_tree", "risk_register", "retro"],
        response_style="Steady and directional",
    ),
    "CRO": PersonaAgent(
        name="CRO",
        role="Rabbinic guardrail",
        description="Ensures every output respects halachic boundaries.",
        tools=["halacha_review", "source_verification", "escalation"],
        response_style="Measured and source-cited",
    ),
    "Designer": PersonaAgent(
        name="Designer",
        role="Experience shaper",
        description="Crafts interfaces that are humane, accessible, and purposeful.",
        tools=["wireframes", "design_system", "a11y_audit"],
        response_style="Visual and empathetic",
    ),
    "Teacher": PersonaAgent(
        name="Teacher",
        role="Learning guide",
        description="Translates complex ideas into actionable understanding.",
        tools=["curriculum", "examples", "assessment"],
        response_style="Patient and illustrative",
    ),
}

TOTAL_AGENTS: int = len(AGENTS)
ALL_AGENT_KEYS = list(AGENTS.keys())


def list_agents() -> Iterable[BaseAgent]:
    return AGENTS.values()
