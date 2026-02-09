from fastapi import APIRouter
from app.api.v1.endpoints import auth, analysis, dashboard, export, share

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(export.router, prefix="/export", tags=["Export"])
api_router.include_router(share.router, prefix="/share", tags=["Sharing"])
