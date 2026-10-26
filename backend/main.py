from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from middleware.request_id import RequestIDMiddleware
from httpxC.http_client import http_client
from cache.redis import redis_manager
from api.v1.api import api_router


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

app.add_middleware(RequestIDMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dscrappy.johnmgrubbs.io",
    ],
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