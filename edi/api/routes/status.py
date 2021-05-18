"""
status.py

Implements the system /status API endpoint
"""
from fastapi import Depends
from fastapi.routing import APIRouter
from edi import __version__
from edi.api.config import get_settings
from edi.core.models import StatusResponse

router = APIRouter()


@router.get("", response_model=StatusResponse)
def get_status(settings=Depends(get_settings)):
    """
    Returns the current application info and status.

    Fields returned include:

    * Application Name
    * Application Version
    * Debugging/Reload Enabled
    """
    status_fields = {
        "application": settings.uvicorn_app,
        "applicationVersion": __version__,
        "isReloadEnabled": settings.uvicorn_reload,
    }
    return StatusResponse(**status_fields)
