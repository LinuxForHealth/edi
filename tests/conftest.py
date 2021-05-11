"""
conftest.py

Global PyTest fixtures
"""
import pytest
from edi.config import Settings
from httpx import AsyncClient
from edi.main import get_app


@pytest.fixture
def settings() -> Settings:
    """
    :return: Application Settings
    """
    settings_fields = {
        "uvicorn_app": "edi.asgi:edi",
        "uvicorn_reload": False,
        "edi_cert_key_name": "./edi-test.key",
        "edi_cert_name": "./edi-test.pem",
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
