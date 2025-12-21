from fastapi import APIRouter
from .endpoints import router as endpoints

api_router = APIRouter()

api_router.include_router(endpoints, prefix="/v1")

