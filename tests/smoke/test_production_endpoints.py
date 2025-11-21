"""Smoke tests for production endpoints.

These tests are intentionally lightweight and target the public production
services. They are meant to detect obvious availability or DNS/SSL issues.
"""

import pytest
import httpx

TIMEOUT = httpx.Timeout(10.0, connect=5.0)


def _get(url: str) -> httpx.Response:
    """Perform a GET request with shared timeout and streaming disabled."""
    with httpx.Client(follow_redirects=True, timeout=TIMEOUT) as client:
        return client.get(url)


def test_frontend_homepage():
    response = _get("https://www.sodmaster.online")
    assert response.status_code == 200
    assert response.text, "Homepage response should not be empty"


def test_backend_health():
    response = _get("https://api.sodmaster.online/health")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    # Allow minor variations while ensuring the status field is OK.
    assert payload.get("status") == "ok"


def test_backend_health_deep():
    response = _get("https://api.sodmaster.online/health/deep")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    # Expect deep health keys for critical subsystems.
    for key in ("db", "celery"):
        assert key in payload, f"Expected '{key}' in deep health payload"


def test_tg_gateway_basic():
    response = _get("https://tg.sodmaster.online/api/status")
    assert response.status_code == 200


@pytest.mark.xfail(reason="WhatsApp gateway status endpoint pending implementation")
def test_wa_gateway_basic():
    response = _get("https://wa.sodmaster.online/api/status")
    assert response.status_code == 200
