from fastapi import APIRouter
from app.api.v1.endpoints import auth, organizations, clusters, deployments

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(clusters.router, prefix="/clusters", tags=["clusters"])
api_router.include_router(deployments.router, prefix="/deployments", tags=["deployments"])
