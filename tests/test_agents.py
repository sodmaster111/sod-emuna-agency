import asyncio

import pytest

from app.agents.registry import AGENTS_CONFIG
from app.core import sanhedrin as sanhedrin_module
from app.core.sanhedrin import SanhedrinCouncil


class DummyAssistant:
    def __init__(self, name: str, system_message: str, llm_config: dict | None = None) -> None:
        self.name = name
        self.system_message = system_message
        self.llm_config = llm_config or {}


class DummyGroupChat:
    def __init__(
        self,
        agents=None,
        messages=None,
        speaker_selection_method: str | None = None,
        max_round: int | None = None,
        send_introductions: bool | None = None,
    ) -> None:
        self.agents = agents or []
        self.messages = messages or []
        self.speaker_selection_method = speaker_selection_method
        self.max_round = max_round
        self.send_introductions = send_introductions
        self.termination_condition = None

    def initiate_chat(self, manager, message: str) -> None:  # noqa: ANN001
        # Simulate a minimal chat log containing an approval.
        self.messages.append({"name": "CEO", "content": f"APPROVED: {message}"})


class DummyGroupChatManager:
    def __init__(self, groupchat=None, llm_config=None, system_message: str | None = None) -> None:
        self.groupchat = groupchat
        self.llm_config = llm_config or {}
        self.system_message = system_message


class DummyTonWallet:
    def get_balance(self, address: str | None = None) -> str:  # noqa: ANN001
        return "0"


class DummyKnowledgeTool:
    async def lookup(self, *_args, **_kwargs) -> str:  # pragma: no cover - no-op
        return "stub"


class DummyWebAgent:
    async def visit_url(self, *_args, **_kwargs) -> str:  # pragma: no cover - no-op
        return "stub"


@pytest.fixture(autouse=True)
def patch_autogen(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace AutoGen classes with lightweight stand-ins."""

    monkeypatch.setattr(sanhedrin_module, "AssistantAgent", DummyAssistant)
    monkeypatch.setattr(sanhedrin_module, "GroupChat", DummyGroupChat)
    monkeypatch.setattr(sanhedrin_module, "GroupChatManager", DummyGroupChatManager)
    monkeypatch.setattr(sanhedrin_module, "TonWalletTool", DummyTonWallet)
    monkeypatch.setattr(sanhedrin_module, "KnowledgeTool", DummyKnowledgeTool)
    monkeypatch.setattr(sanhedrin_module, "WebAgent", DummyWebAgent)


def test_sanhedrin_initializes_expected_agents() -> None:
    council = SanhedrinCouncil()

    assert set(council.agents.keys()) == set(AGENTS_CONFIG.keys())
    for name, agent in council.agents.items():
        assert isinstance(agent, DummyAssistant)
        assert agent.system_message == AGENTS_CONFIG[name]["system_message"]
        assert "config_list" in agent.llm_config


@pytest.mark.anyio
async def test_convene_uses_mocked_chat(monkeypatch: pytest.MonkeyPatch) -> None:
    council = SanhedrinCouncil()

    # Ensure execution tools do not run during the test.
    async def noop(*_: object) -> None:
        return None

    monkeypatch.setattr(council, "_execute_tools", noop)

    # Provide a deterministic chat log instead of calling Ollama.
    def fake_run_group_chat(prompt: str):  # noqa: ANN001
        return [
            {"name": "CEO", "content": "APPROVED: Move forward"},
            {"name": "CFO", "content": "Budget secured"},
        ]

    monkeypatch.setattr(council, "_run_group_chat", fake_run_group_chat)

    transcript = await council.convene()

    assert transcript[0].startswith("APPROVED")
    assert any("Budget" in entry for entry in transcript)
