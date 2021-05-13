"""
asgi.py

Loads the EDI app attribute for ASGI processing
"""
from edi.api.main import get_app

app = get_app()
