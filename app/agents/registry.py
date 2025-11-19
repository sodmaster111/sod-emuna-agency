"""Registry of the 12 Digital Sanhedrin agents."""
from __future__ import annotations

from typing import Dict

from autogen import AssistantAgent

from app.core.config import config


AGENT_ROLES: Dict[str, str] = {
    "CEO": "Nasi / Chairman. Align all efforts to strategic goals and call approvals.",
    "CKO": "Chief Knowledge Officer (Torah). Ethics, halacha, and veto authority.",
    "CFO": "Treasurer. Financial logic, risk and treasury management for TON.",
    "CMO": "Marketing lead. Drive virality, hype, and user/community growth.",
    "CTO": "Technology lead. Architect scalable systems and technical innovation.",
    "COO": "Operations lead. Ensure execution discipline and process reliability.",
    "CPO": "Product lead. Define offers, experiences, and conversion levers.",
    "CCO": "Customer officer. Voice of users, support quality, community health.",
    "CLO": "Legal officer. Compliance, contracts, and regulatory foresight.",
    "CIO": "Information officer. Data pipelines, observability, and infosec.",
    "CDO": "Data/AI officer. Analytics, modeling, and insight activation.",
    "CRO": "Revenue/Growth officer. Monetization experiments and partnerships.",
    "CVO": "Chief Visionary Officer. Moonshot strategy and 10-year horizon.",
    "CSO": "Chief Strategy Officer. Competitive roadmap and risk navigation.",
}

AGENT_PROMPTS: Dict[str, str] = {
    "CEO": (
        "You are the CEO of the Digital Sanhedrin. Use Decision Matrix logic to weigh impact, "
        "effort, risk, and speed before approving paths. Align all efforts to strategic goals and call approvals."
    ),
    "CKO": (
        "You are the CKO (Torah). Act as a Gadol Hador ensuring strict ethical and Halachic compliance with "
        "veto authority over any breach."
    ),
    "CFO": (
        "You are the CFO. Apply the Kelly Criterion for risk-aware capital allocation and treasury management for TON."
    ),
    "CMO": (
        "You are the CMO. Use Cialdini’s 6 Principles of Persuasion and Viral Loops to drive virality, hype, and user/community growth."
    ),
    "CVO": (
        "You are the CVO. Use 'First Principles Thinking'. Ignore current limitations. Focus on Moonshot ideas and the 10-year horizon. "
        "Your goal is to find the 'Blue Ocean'."
    ),
    "CSO": (
        "You are the CSO. Use 'Game Theory' and 'OODA Loop'. Turn the CVO's visions into a winning roadmap. "
        "Analyze competitors and risks."
    ),
}

BASE_COLLAB_PROMPT = (
    "Collaborate concisely, cite tools you intend to trigger, and respect the CKO's ethical guardrails. "
    "When the CEO says 'APPROVED', the meeting ends."
)


def create_agent(name: str, system_prompt: str) -> AssistantAgent:
    """Instantiate an AutoGen assistant configured for the Sanhedrin."""

    return AssistantAgent(
        name=name,
        system_message=system_prompt,
        llm_config=config.llm_config,
        human_input_mode="NEVER",
    )


def build_prompt(title: str, description: str) -> str:
    """Build the system prompt for a given agent title."""

    specific_prompt = AGENT_PROMPTS.get(
        title,
        f"You are the {title} of the Digital Sanhedrin. {description}",
    )
    return f"{specific_prompt} {BASE_COLLAB_PROMPT}"


def build_sanhedrin() -> Dict[str, AssistantAgent]:
    """Construct the 12 agents with dedicated system prompts."""

    agents: Dict[str, AssistantAgent] = {}
    for title, description in AGENT_ROLES.items():
        prompt = build_prompt(title, description)
        agents[title] = create_agent(title, prompt)
    return agents
