"""
test_status_api.py
Tests the /status API endpoints
"""
from edi.api.config import get_settings


def test_status_get(test_client, settings):
    """
    Tests /status [GET]
    :param test_client: Fast API \test client
    :param settings: Settings test fixture
    """
    with test_client as tc:
        settings.uvicorn_reload = False
        tc.app.dependency_overrides[get_settings] = lambda: settings
        actual_response = tc.get("/edi/status")

        assert actual_response.status_code == 200

        actual_json = actual_response.json()
        assert "applicationVersion" in actual_json

        expected = {
            "application": "edi.asgi:edi",
            "applicationVersion": actual_json["applicationVersion"],
            "isReloadEnabled": False,
        }
        assert actual_json == expected
