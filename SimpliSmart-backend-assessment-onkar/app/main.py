from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import create_engine
from app.api.v1.api import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cluster Management API",
    description="""
    Technical Assessment API for managing organizations, clusters, and deployments.
    
    ## Features
    
    * **Users & Authentication** - Register, login, and manage user sessions
    * **Organizations** - Create and join organizations using invite codes
    * **Clusters** - Manage compute clusters with resource limits
    * **Deployments** - Schedule and manage deployments with priority queuing
    
    ## Authentication
    
    The API uses session-based authentication. To access protected endpoints:
    1. Register a new user account (`POST /api/v1/auth/register`)
    2. Login with your credentials (`POST /api/v1/auth/login`)
    3. The server will set a session cookie automatically
    4. Use this cookie for all subsequent requests
    5. Logout when finished (`POST /api/v1/auth/logout`)
    
    ## Organizations
    After authentication, users can:
    1. Create a new organization (generates an invite code)
    2. Join an existing organization using an invite code
    3. Access their organization's clusters and deployments
    
    ## Resource Management
    The system tracks and manages three types of resources:
    - CPU (in cores)
    - RAM (in GB)
    - GPU (in units)
    
    Deployments are scheduled based on:
    1. Available resources in the cluster
    2. Deployment priority
    3. Resource requirements
    """,
    version="1.0.0",
    openapi_tags=[
        {
            "name": "authentication",
            "description": "Operations with user authentication. Register new users and login."
        },
        {
            "name": "organizations",
            "description": "Manage organizations and handle user invitations."
        },
        {
            "name": "clusters",
            "description": "Create and manage compute clusters with resource tracking."
        },
        {
            "name": "deployments",
            "description": "Schedule and manage deployments with priority-based queuing."
        }
    ],
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS and Session
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie=settings.SESSION_COOKIE_NAME,
    max_age=settings.SESSION_MAX_AGE
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
