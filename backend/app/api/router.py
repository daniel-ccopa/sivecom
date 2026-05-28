from fastapi import APIRouter

from app.api.routes_expedientes import router as expedientes_router

api_router = APIRouter()
api_router.include_router(expedientes_router, prefix="/expedientes", tags=["expedientes"])
