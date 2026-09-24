from __future__ import annotations

import logging

from app.config import settings

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO if settings.environment != "production" else logging.WARNING,
        format=LOG_FORMAT,
        handlers=[logging.StreamHandler()],
    )

from fastapi import Request


async def log_request(request: Request, call_next):
    logger.info("Incoming request: %s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.info("Response status: %s", response.status_code)
    return response


logger = logging.getLogger("hireflow")
