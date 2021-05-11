"""
asgi.py

Loads the EDI app attribute for ASGI processing
"""
from edi.main import get_app

app = get_app()
