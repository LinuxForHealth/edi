"""
asgi.py

Loads the app attribute for ASGI processing
"""
from app.main import get_app

app = get_app()
