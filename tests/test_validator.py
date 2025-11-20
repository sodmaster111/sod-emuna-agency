import pytest

from app.agents.cko import validator
from app.agents.cko.validator import validate_action


@pytest.fixture(autouse=True)
def stub_sefaria(monkeypatch: pytest.MonkeyPatch) -> None:
    """Avoid real HTTP calls to Sefaria during tests."""

    def fake_consult(query: str):
        return {"title": "Pirkei Avot 1:2", "text": [f"source for {query}"], "sources": ["Sefaria"]}

    monkeypatch.setattr(validator, "consult_sefaria", fake_consult)


def test_greed_trap_vetoes_exploitative_plan(monkeypatch: pytest.MonkeyPatch) -> None:
    llm_calls = {}

    def fake_completion(model: str, messages: list[dict]):  # noqa: ANN001
        llm_calls["payload"] = messages
        return {"choices": [{"message": {"content": "REJECT: harms the vulnerable"}}]}

    monkeypatch.setattr(validator.litellm, "completion", fake_completion)

    result = validate_action("maximize profit even if it harms the poor")

    assert result["verdict"] == "rejected"
    assert "REJECT" in result["reason"].upper()
    assert llm_calls["payload"][0]["content"] == validator.AGENTS_CONFIG.get("CKO", {}).get("system_message", "")


def test_heresy_trap_short_circuits(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {"llm": 0}

    def fake_completion(*_args, **_kwargs):  # noqa: ANN001
        called["llm"] += 1
        return {"choices": [{"message": {"content": "APPROVE"}}]}

    monkeypatch.setattr(validator.litellm, "completion", fake_completion)

    result = validate_action("promote idolatry and abandon mitzvot")

    assert result["verdict"] == "rejected"
    assert "veto".upper() in result["reason"].upper()
    assert called["llm"] == 0


def test_conflict_trap_passes_sources_into_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    captured_user_prompt = {}

    def fake_completion(model: str, messages: list[dict]):  # noqa: ANN001
        captured_user_prompt["text"] = messages[1]["content"]
        assert "Pirkei Avot" in messages[1]["content"]
        return {"choices": [{"message": {"content": "APPROVE with safeguards"}}]}

    monkeypatch.setattr(validator.litellm, "completion", fake_completion)

    result = validate_action("coordinate charity event before Shabbat")

    assert result["verdict"] == "approved"
    assert "charity" in captured_user_prompt["text"].lower()
    assert "APPROVE" in result["reason"].upper()
