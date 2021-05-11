"""
test_status.py
Tests the /status API endpoints
"""
import pytest
from edi.config import get_settings


@pytest.mark.asyncio
async def test_status_get(async_test_client, settings, monkeypatch):
    """
    Tests /status [GET]
    :param async_test_client: Fast API async test client
    :param settings: Settings test fixture
    :param monkeypatch: MonkeyPatch instance used to mock test cases
    """
    with monkeypatch.context():

        async with async_test_client as ac:
            settings.uvicorn_reload = False
            ac._transport.app.dependency_overrides[get_settings] = lambda: settings
            actual_response = await ac.get("/status")

            assert actual_response.status_code == 200

            actual_json = actual_response.json()
            assert "application_version" in actual_json
            assert "elapsed_time" in actual_json
            assert actual_json["elapsed_time"] > 0.0

            expected = {
                "application": "edi.asgi:edi",
                "application_version": actual_json["application_version"],
                "is_reload_enabled": False,
                "elapsed_time": actual_json["elapsed_time"],
            }
            assert actual_json == expected
