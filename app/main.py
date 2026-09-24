from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.user import router as user_router
from app.routes.auth import router as auth_router
from app.config import settings
from app.middleware.error_handler import register_error_handlers
from app.config import parse_cors_origins
from app.logger import configure_logging, logger, log_request
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from app.database import Base, engine

configure_logging()

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("Application startup complete.")
    yield
    logger.info("Application shutdown complete.")

# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API for managing users",
    # lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=parse_cors_origins(settings.cors_origins),
)
app.middleware("http")(log_request)
register_error_handlers(app)

app.include_router(user_router)
app.include_router(auth_router)

@app.get("/", tags=["root"], summary="Root endpoint")
def root() -> dict[str, str]:
    return {"message": "Welcome to the Hireflow API!"}


