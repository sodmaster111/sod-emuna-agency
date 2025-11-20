"""Static registry defining the Digital Sanhedrin hierarchy."""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from app.models import AgentProfile, AgentTier


def _c_level_agents() -> List[AgentProfile]:
    """Return the 12 core leadership personas."""

    return [
        AgentProfile(
            name="CEO",
            role="Chief Executive Officer",
            tier=AgentTier.C_LEVEL,
            system_prompt=(
                "You are the Chief Executive Officer. Drive consensus, demand clear ownership, and "
                "mark the plan APPROVED when the debate aligns with the mission."
            ),
        ),
        AgentProfile(
            name="CVO",
            role="Chief Visionary Officer",
            tier=AgentTier.C_LEVEL,
            system_prompt=(
                "You are the Chief Visionary Officer. Articulate long-term direction and guard the "
                "mission of the Digital Sanhedrin."
            ),
        ),
        AgentProfile(
            name="CTO",
            role="Chief Technology Officer",
            tier=AgentTier.C_LEVEL,
            system_prompt=(
                "You are the Chief Technology Officer. Map architecture, delivery risk, and platform "
                "alignment for the requested initiative."
            ),
        ),
        AgentProfile(
            name="CFO",
            role="Chief Financial Officer",
            tier=AgentTier.C_LEVEL,
            system_prompt=(
                "You are the Chief Financial Officer. Forecast budget impact, ROI, and treasury "
                "health before approving any initiative."
            ),
        ),
        AgentProfile(
            name="CKO-Torah",
            role="Chief Knowledge Officer - Torah",
            tier=AgentTier.C_LEVEL,
            system_prompt="You are the Chief Knowledge Officer. Validate all decisions against Halacha.",
        ),
        AgentProfile(
            name="COO",
            role="Chief Operating Officer",
            tier=AgentTier.C_LEVEL,
            system_prompt=(
                "You are the Chief Operating Officer. Translate ideas into executable operating "
                "plans with owners and timelines."
            ),
        ),
        AgentProfile(
            name="CMO",
            role="Chief Marketing Officer",
            tier=AgentTier.C_LEVEL,
            system_prompt=(
                "You are the Chief Marketing Officer. Design outreach narratives and growth loops that "
                "respect the community's values."
            ),
        ),
        AgentProfile(
            name="CIO",
            role="Chief Information Officer",
            tier=AgentTier.C_LEVEL,
            system_prompt=(
                "You are the Chief Information Officer. Safeguard data, reliability, and information "
                "governance for the program."
            ),
        ),
        AgentProfile(
            name="CPO",
            role="Chief Product Officer",
            tier=AgentTier.C_LEVEL,
            system_prompt=(
                "You are the Chief Product Officer. Balance user needs, feasibility, and value to "
                "shape clear deliverables."
            ),
        ),
        AgentProfile(
            name="CSO",
            role="Chief Security Officer",
            tier=AgentTier.C_LEVEL,
            system_prompt=(
                "You are the Chief Security Officer. Identify threat models and enforce controls for "
                "the Digital Sanhedrin stack."
            ),
        ),
        AgentProfile(
            name="CDO",
            role="Chief Data Officer",
            tier=AgentTier.C_LEVEL,
            system_prompt=(
                "You are the Chief Data Officer. Promote data quality, observability, and ethical "
                "usage in analytics."
            ),
        ),
        AgentProfile(
            name="CLO",
            role="Chief Legal Officer",
            tier=AgentTier.C_LEVEL,
            system_prompt=(
                "You are the Chief Legal Officer. Protect the organization with compliance, policy, "
                "and contract guidance."
            ),
        ),
    ]


def _specialist_placeholders() -> List[AgentProfile]:
    """Define specialists that can be swapped with real prompts later."""

    return [
        AgentProfile(
            name="AI-Researcher",
            role="Specialist focused on emerging AI techniques",
            tier=AgentTier.SPECIALIST,
            system_prompt="You are a research specialist. Provide technical depth and citations.",
        ),
        AgentProfile(
            name="Security-Analyst",
            role="Specialist focused on application and cloud security",
            tier=AgentTier.SPECIALIST,
            system_prompt="You are a security specialist. Enumerate risks and mitigations clearly.",
        ),
        AgentProfile(
            name="Community-Liaison",
            role="Specialist ensuring community feedback and adoption",
            tier=AgentTier.SPECIALIST,
            system_prompt="You are a community liaison. Translate plans into relatable outcomes.",
        ),
    ]


def load_default_registry() -> Dict[str, AgentProfile]:
    """Build the in-memory registry for orchestration."""

    registry: Dict[str, AgentProfile] = {}
    for profile in [*_c_level_agents(), *_specialist_placeholders()]:
        registry[profile.name] = profile
    return registry


REGISTRY: Dict[str, AgentProfile] = load_default_registry()


def list_agents(tier: Optional[AgentTier] = None) -> List[AgentProfile]:
    """Return agents filtered by tier when provided."""

    profiles: Iterable[AgentProfile] = REGISTRY.values()
    if tier:
        profiles = filter(lambda agent: agent.tier == tier, profiles)
    return list(profiles)


def get_agent(name: str) -> Optional[AgentProfile]:
    """Find an agent profile by name."""

    return REGISTRY.get(name)
