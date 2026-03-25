from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import RequestResponseEndpoint

from app.database.session import init_db
from app.logger import configure_logging, get_logger
from app.routers import addresses_router
from config import settings

configure_logging(settings.LOG_LEVEL)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize shared resources during app startup."""
    logger.info("Starting %s", settings.APP_NAME)
    init_db()
    yield
    logger.info("Stopping %s", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Minimal FastAPI address book API with SQLite persistence, "
        "input validation, and nearby search by coordinates."
    ),
    lifespan=lifespan,
)

app.include_router(addresses_router)


@app.middleware("http")
async def log_requests(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
    logger.info("Request started: %s %s", request.method, request.url.path)
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Unhandled server error while processing %s %s", request.method, request.url.path)
        raise

    level = logging.INFO
    if response.status_code >= 500:
        level = logging.ERROR
    elif response.status_code >= 400:
        level = logging.WARNING

    logger.log(
        level,
        "Request completed: %s %s -> %s",
        request.method,
        request.url.path,
        response.status_code,
    )
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    error_payload = jsonable_encoder(exc.errors())
    logger.warning(
        "Validation failed for %s %s: %s",
        request.method,
        request.url.path,
        error_payload,
    )
    return JSONResponse(status_code=422, content={"detail": error_payload})


@app.get("/", tags=["Health"])
def root() -> dict[str, str]:
    return {
        "message": (
            f"Welcome to {settings.APP_NAME}. "
            "Visit /docs for interactive API documentation."
        )
    }


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
