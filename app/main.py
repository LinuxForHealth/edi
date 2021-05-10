"""
main.py

Bootstraps the Fast API application and Uvicorn processes
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
import uvicorn
from app.config import get_settings
from app.routes.api import router
from app import __version__
from app.server_handlers import (
    configure_logging,
    log_configuration,
    http_exception_handler,
)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
import os


def get_app() -> FastAPI:
    """
    Creates the Fast API application instance
    :return: The application instance
    """
    settings = get_settings()

    app = FastAPI(
        title="Fast API Template App",
        description="Fast API Application Quickstart",
        version=__version__,
    )
    app.add_middleware(HTTPSRedirectMiddleware)
    app.include_router(router)
    app.add_event_handler("startup", configure_logging)
    app.add_event_handler("startup", log_configuration)
    app.add_exception_handler(HTTPException, http_exception_handler)

    # use the slowapi rate limiter
    app.add_middleware(SlowAPIMiddleware)
    limiter = Limiter(
        key_func=get_remote_address, default_limits=[settings.app_rate_limit]
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    return app


if __name__ == "__main__":
    settings = get_settings()

    uvicorn_params = {
        "app": settings.uvicorn_app,
        "host": settings.uvicorn_host,
        "log_config": None,
        "port": settings.uvicorn_port,
        "reload": settings.uvicorn_reload,
        "ssl_keyfile": os.path.join(settings.app_ca_path, settings.app_cert_key_name),
        "ssl_certfile": os.path.join(settings.app_ca_path, settings.app_cert_name),
    }

    uvicorn.run(**uvicorn_params)
