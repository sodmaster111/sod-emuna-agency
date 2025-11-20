import os
import sys
import types
from pathlib import Path

import pytest

# Ensure project root is on the import path for tests and disable DB usage.
os.environ.setdefault("DISABLE_DATABASE", "1")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# Provide lightweight stand-ins for the AutoGen package to avoid test-time imports.
class _StubAssistant:
    def __init__(self, *args, **kwargs):  # noqa: ANN001, D401
        """Minimal stand-in for autogen.AssistantAgent."""


class _StubGroupChat:
    def __init__(self, *args, **kwargs):  # noqa: ANN001, D401
        """Minimal stand-in for autogen.GroupChat."""


class _StubGroupChatManager:
    def __init__(self, *args, **kwargs):  # noqa: ANN001, D401
        """Minimal stand-in for autogen.GroupChatManager."""


class _StubBrowserAgent:
    async def arun(self, *_args, **_kwargs):  # pragma: no cover - no-op
        return "stubbed"


sys.modules.setdefault(
    "autogen",
    types.SimpleNamespace(
        AssistantAgent=_StubAssistant,
        GroupChat=_StubGroupChat,
        GroupChatManager=_StubGroupChatManager,
    ),
)

sys.modules.setdefault(
    "browser_use.agent",
    types.SimpleNamespace(Agent=_StubBrowserAgent),
)


@pytest.fixture
def anyio_backend() -> str:
    """Force AnyIO to run tests with asyncio backend only."""

    return "asyncio"
