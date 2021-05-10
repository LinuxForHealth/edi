"""
conftest.py

Global PyTest fixtures
"""
import pytest
from app.config import Settings
from httpx import AsyncClient
from app.main import get_app


@pytest.fixture
def settings() -> Settings:
    """
    :return: Application Settings
    """
    settings_fields = {
        "uvicorn_app": "app.asgi:app",
        "uvicorn_reload": False,
        "app_cert_key_name": "./test.key",
        "app_cert_name": "./test.pem",
    }
    return Settings(**settings_fields)


@pytest.fixture
def async_test_client(monkeypatch) -> AsyncClient:
    """
    Creates an HTTPX AsyncClient for async API testing
    :param monkeypatch: monkeypatch fixture
    :return: HTTPX async test client
    """
    return AsyncClient(app=get_app(), base_url="http://testserver")
