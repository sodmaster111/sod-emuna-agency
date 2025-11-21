"""Factory utilities to spawn Digital Sanhedrin agents on demand."""
from __future__ import annotations

from typing import Any, Dict, Iterable, Tuple

from autogen import AssistantAgent, GroupChat, GroupChatManager
from langchain_community.chat_models import ChatLiteLLM
from langgraph.prebuilt import create_react_agent

from app.agents.registry import get_system_prompt
from app.core.config import get_settings
from app.core.tracing import get_callback_handler, start_trace

SettingsDict = Dict[str, Any]


def _build_llm_config() -> SettingsDict:
    """Return an AutoGen/LiteLLM configuration dictionary using OLLAMA_BASE_URL."""

    settings = get_settings()
    return {
        "config_list": [
            {
                "model": settings.ollama_model,
                "api_key": "na",  # Ollama-style backends typically ignore the key.
                "base_url": settings.ollama_base_url,
            }
        ]
    }


def build_langgraph_agent(role_name: str, tools: Iterable[Any] | None = None) -> Any:
    """Initialize a LangGraph agent tailored to the specified role."""

    settings = get_settings()
    system_prompt = get_system_prompt(role_name)
    handler = get_callback_handler()
    llm_kwargs: Dict[str, Any] = {
        "model": settings.ollama_model,
        "api_base": settings.ollama_base_url,
        "temperature": settings.temperature,
        "max_tokens": settings.max_tokens,
    }
    if handler:
        llm_kwargs["callbacks"] = [handler]

    start_trace(
        name=f"{role_name}-root",
        input=system_prompt,
        metadata={"agent": role_name, "framework": "langgraph"},
    )

    llm = ChatLiteLLM(**llm_kwargs)
    return create_react_agent(
        llm,
        tools=list(tools or []),
        state_modifier=system_prompt,
    )


def build_autogen_agent(role_name: str) -> AssistantAgent:
    """Create an AutoGen AssistantAgent with the correct system prompt."""

    system_prompt = get_system_prompt(role_name)
    handler = get_callback_handler()
    llm_config = _build_llm_config()
    if handler:
        llm_config["callbacks"] = [handler]

    start_trace(
        name=f"{role_name}-root",
        input=system_prompt,
        metadata={"agent": role_name, "framework": "autogen"},
    )

    return AssistantAgent(
        name=role_name,
        system_message=system_prompt,
        llm_config=llm_config,
    )


def build_board_group_chat(topic: str = "Board meeting: advance the mission") -> Tuple[GroupChat, GroupChatManager]:
    """Create a GroupChat stub for CEO/CKO/CFO/CMO deliberations."""

    agents = [build_autogen_agent(role) for role in ("CEO", "CKO", "CFO", "CMO")]
    group_chat = GroupChat(
        agents=agents,
        messages=[],
        speaker_selection_method="auto",
        max_round=12,
        send_introductions=True,
    )
    manager = GroupChatManager(
        groupchat=group_chat,
        llm_config=_build_llm_config(),
        system_message=(
            "Facilitate a Digital Sanhedrin board meeting using the AMAC cycle. Ensure "
            "the CEO synthesizes input and concludes with 'APPROVED' when the topic is "
            f"resolved. Agenda: {topic}."
        ),
    )
    return group_chat, manager


def get_agent(role_name: str, framework: str = "langgraph") -> Any:
    """Initialize an agent with the requested framework backend."""

    if framework == "langgraph":
        return build_langgraph_agent(role_name)
    if framework == "autogen":
        return build_autogen_agent(role_name)
    raise ValueError(f"Unsupported framework '{framework}'. Choose 'langgraph' or 'autogen'.")


__all__ = [
    "build_langgraph_agent",
    "build_autogen_agent",
    "build_board_group_chat",
    "get_agent",
]
