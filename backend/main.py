from contextlib import asynccontextmanager

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from middleware.request_id import RequestIDMiddleware
from httpxC.http_client import http_client
from cache.redis import redis_manager
from api.v1.api import api_router
from core.config import settings
from core.errors import ScrappyError

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()

    yield

    await redis_manager.disconnect()
    await http_client.aclose()


app = FastAPI(
    title="Scrappy's Scrapyard API",
    lifespan=lifespan,
)


@app.exception_handler(ScrappyError)
async def handle_scrappy_error(request: Request, exc: ScrappyError) -> JSONResponse:
    logger.exception("Application error for %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=502,
        content={"detail": "A dependent service failed while processing the request."},
    )

app.add_middleware(RequestIDMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Accept",
        "Authorization",
        "Content-Type",
        "Origin",
    ],
)

app.include_router(api_router, prefix="/api/v1")
