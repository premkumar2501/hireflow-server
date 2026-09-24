from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("hireflow")


def _error_payload(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
            },
        },
    )


def _format_validation_errors(exc: RequestValidationError) -> str:
    messages = []

    for error in exc.errors():
        location = ".".join(str(item) for item in error.get("loc", ()))
        message = error.get("msg", "Invalid value")
        if not location:
            location = "body"
        messages.append(f"{location}: {message}")

    return "; ".join(messages) if messages else "Validation failed"


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        message = exc.detail if isinstance(exc.detail, str) else "An unexpected error occurred"
        return _error_payload(exc.status_code, "HTTP_ERROR", message)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        message = _format_validation_errors(exc)
        return _error_payload(422, "VALIDATION_ERROR", message)

    @app.exception_handler(ValueError)
    async def value_error_handler(_: Request, exc: ValueError) -> JSONResponse:
        return _error_payload(400, "BAD_REQUEST", str(exc))

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled application exception: %s", exc)
        return _error_payload(500, "SOMETHING WENT WRONG", "An unexpected error occurred")
