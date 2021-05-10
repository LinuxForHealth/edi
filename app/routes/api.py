"""
api.py

Configures the API Router for the Fast API application
"""
from fastapi import APIRouter
from app.routes import status

router = APIRouter()
router.include_router(status.router, prefix="/status")
