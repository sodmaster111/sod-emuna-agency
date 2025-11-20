import asyncio

import pytest
from httpx import ASGITransport, AsyncClient

import main


class FakeCouncil:
    def __init__(self, db_session=None) -> None:  # noqa: ANN001
        self.db_session = db_session
        self.mission_goal = "Test the Digital Sanhedrin"

    async def convene(self) -> list[str]:
        return ["APPROVED: Execute test plan", "CFO: Budget confirmed"]


@pytest.fixture(autouse=True)
def patch_council(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure API tests never hit a real LLM."""

    monkeypatch.setattr(main, "SanhedrinCouncil", FakeCouncil)


@pytest.mark.anyio
async def test_status_endpoint_returns_200() -> None:
    transport = ASGITransport(app=main.app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/status")

    assert response.status_code == 200
    payload = response.json()
    assert "agents" in payload
    assert "mission_goal" in payload


@pytest.mark.anyio
async def test_logs_endpoint_returns_200() -> None:
    transport = ASGITransport(app=main.app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/logs")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_start_meeting_returns_200() -> None:
    # Ensure database startup runs before hitting the endpoint.
    if main.app.router.on_startup:
        await asyncio.gather(*(handler() for handler in main.app.router.on_startup))

    transport = ASGITransport(app=main.app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/start-meeting")

    assert response.status_code == 200
    data = response.json()
    assert data["mission_goal"] == "Test the Digital Sanhedrin"
    assert data["transcript"][0].startswith("APPROVED")
