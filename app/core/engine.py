"""LLM engine initialization for Ollama-backed AutoGen agents."""
from __future__ import annotations

import os
from typing import Dict, List

import litellm


class Engine:
    """Configure LiteLLM and provide AutoGen-ready model settings."""

    def __init__(self) -> None:
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3")
        self.api_key = os.getenv("OLLAMA_API_KEY", "")
        self.loop_interval = int(os.getenv("CYCLE_SLEEP_SECONDS", "300"))
        self._configure_litellm()

    def _configure_litellm(self) -> None:
        """Wire LiteLLM to the Ollama endpoint."""

        litellm.api_base = self.ollama_base_url
        litellm.model = self.model
        if self.api_key:
            litellm.api_key = self.api_key

    @property
    def llm_config(self) -> Dict[str, List[Dict[str, str]]]:
        """AutoGen llm_config using Ollama via LiteLLM."""

        return {
            "config_list": [
                {
                    "model": self.model,
                    "api_base": self.ollama_base_url,
                    "api_type": "ollama",
                    "api_key": self.api_key,
                }
            ]
        }
