"""Factory utilities to spawn Digital Sanhedrin agents."""
from __future__ import annotations

from typing import Any

from langchain_community.chat_models import ChatLiteLLM
from langgraph.prebuilt import create_react_agent

from app.agents.registry import get_system_prompt
from app.core.config import config


def build_llm() -> ChatLiteLLM:
    """Create a LiteLLM-backed chat model targeting the configured Ollama endpoint."""

    return ChatLiteLLM(
        model=config.ollama_model,
        api_base=config.ollama_base_url,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )


def get_agent(role_name: str) -> Any:
    """Initialize a LangGraph agent for the requested role name."""

    system_prompt = get_system_prompt(role_name)
    llm = build_llm()
    agent = create_react_agent(
        llm,
        tools=[],
        state_modifier=system_prompt,
    )
    return agent
