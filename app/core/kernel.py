"""Semantic Kernel initialization and dynamic plugin loading utilities."""
from __future__ import annotations

import importlib
import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType
from typing import Dict, Iterable, Optional

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.llm.litellm import LiteLLMChatCompletion

from app.core.config import AppConfig, config


class PluginManager:
    """Load and unload plugins on demand to conserve memory."""

    def __init__(self, plugin_dir: Optional[Path] = None) -> None:
        self.plugin_dir = plugin_dir or Path(__file__).resolve().parent.parent / "plugins"
        self.loaded_plugins: Dict[str, ModuleType] = {}

    def available_plugins(self) -> Iterable[str]:
        """Return plugin module names available on disk."""

        if not self.plugin_dir.exists():
            return []
        return [p.stem for p in self.plugin_dir.glob("*.py") if p.name != "__init__.py"]

    def load_plugin(self, name: str) -> ModuleType:
        """Dynamically load a plugin module if not already loaded."""

        if name in self.loaded_plugins:
            return self.loaded_plugins[name]

        plugin_path = self.plugin_dir / f"{name}.py"
        if not plugin_path.exists():
            raise FileNotFoundError(f"Plugin '{name}' not found at {plugin_path}")

        spec = importlib.util.spec_from_file_location(name, plugin_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Unable to load plugin spec for {name}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        self.loaded_plugins[name] = module
        return module

    def unload_plugin(self, name: str) -> None:
        """Remove a plugin from memory."""

        module = self.loaded_plugins.pop(name, None)
        if module is None:
            return
        sys.modules.pop(name, None)

    def unload_all(self) -> None:
        """Unload all currently loaded plugins."""

        for name in list(self.loaded_plugins.keys()):
            self.unload_plugin(name)


def create_kernel(app_config: Optional[AppConfig] = None) -> Kernel:
    """Create a Semantic Kernel instance backed by a LiteLLM Ollama connector."""

    cfg = app_config or config
    kernel = Kernel()
    chat_service = LiteLLMChatCompletion(
        model_id=cfg.ollama_model,
        api_base=cfg.ollama_base_url,
        api_key=os.getenv("LITELLM_API_KEY", ""),
        temperature=cfg.temperature,
    )
    kernel.add_service(chat_service, service_id="ollama")
    return kernel
