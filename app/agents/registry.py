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
}


def create_agent(name: str, system_prompt: str) -> AssistantAgent:
    """Instantiate an AutoGen assistant configured for the Sanhedrin."""

    return AssistantAgent(
        name=name,
        system_message=system_prompt,
        llm_config=config.llm_config,
        human_input_mode="NEVER",
    )


def build_sanhedrin() -> Dict[str, AssistantAgent]:
    """Construct the 12 agents with dedicated system prompts."""

    agents: Dict[str, AssistantAgent] = {}
    for title, description in AGENT_ROLES.items():
        prompt = (
            f"You are the {title} of the Digital Sanhedrin. {description} "
            "Collaborate concisely, cite tools you intend to trigger, and respect the CKO's ethical guardrails. "
            "When the CEO says 'APPROVED', the meeting ends."
        )
        agents[title] = create_agent(title, prompt)
    return agents
