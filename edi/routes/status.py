"""
status.py

Implements the system /status API endpoint
"""
from fastapi import Depends
from fastapi.routing import APIRouter
from pydantic.main import BaseModel
from edi import __version__
from edi.config import get_settings
import time

router = APIRouter()


class StatusResponse(BaseModel):
    """
    Status check response model.
    The response provides component specific and overall status information
    """

    application: str
    application_version: str
    is_reload_enabled: bool
    elapsed_time: float

    class Config:
        schema_extra = {
            "example": {
                "application": "edi.main:app",
                "application_version": "0.25.0",
                "is_reload_enabled": False,
                "elapsed_time": 0.080413915000008,
            }
        }


@router.get("", response_model=StatusResponse)
async def get_status(settings=Depends(get_settings)):
    """
    :return: the current system status
    """

    start_time = time.perf_counter()
    status_fields = {
        "application": settings.uvicorn_app,
        "application_version": __version__,
        "is_reload_enabled": settings.uvicorn_reload,
        "elapsed_time": time.perf_counter() - start_time,
    }
    return StatusResponse(**status_fields)
