from fastapi import APIRouter

from api.v1.endpoints import auth, health, blob, file_jobs

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(blob.router, prefix="/blob", tags=["blob"])
api_router.include_router(file_jobs.router, prefix="/file-jobs", tags=["file_jobs"])
