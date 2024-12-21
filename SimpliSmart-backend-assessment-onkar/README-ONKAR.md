# A FastAPI-based service for managing compute clusters and deployments with priority-based scheduling. The system provides organization management, resource tracking, and automated deployment scheduling.

## Features

### Authentication & Organization Management

- Session-based authentication (can be extended to JWT)
- User registration with password hashing
- Organization creation with invite codes
- Organization joining via invite codes

### Cluster Management

- Create clusters with resource limits (CPU, RAM, GPU)
- Track resource availability
- List clusters for organization members
- Resource constraint validation

### Deployment Management

- Priority-based deployment scheduling
- Resource allocation/deallocation
- Automatic deployment timeout handling
- Deployment status tracking
- Redis-based queue for pending deployments

## Technology Stack

- **Framework**: FastAPI 0.115.6
- **Database**: PostgreSQL + SQLAlchemy ORM 2.0.36
- **Queue**: Redis 5.2.1
- **Authentication**: Session-based (can be extended to JWT)
- **Migration**: Alembic (In progress) 1.14.0
- **Password Hashing**: Passlib 1.7.4
- **API Documentation**: OpenAPI (Swagger UI)

## Prerequisites

1. Python 3.9+
2. PostgreSQL
3. Redis Server
4. Virtual Environment

## Installation & Setup

1. **Create virtual Environment**

- python -m venv venv
- source venv/bin/activate

2. **Install Requirements**

- pip install -r app/requirements.txt

3. **Create ENV variables**

Create a .env file and add the following keys
    PGHOST=
    PGUSER=
    PGPASSWORD=
    PGDATABASE=
    PGPORT=
    REDIS_HOST=
    REDIS_PORT=
    REDIS_DB=
    Deployment
    DEPLOYMENT_TIMEOUT_SECONDS=300 # 5 minutes

    DATABASE_URL=

    SECRET_KEY=  # For secure session encryption
    SESSION_COOKIE_NAME=  # Cookie name for the session
    SESSION_MAX_AGE=        # Session duration in seconds (30 minutes)

4. **Optional - clear DB**

- reset database (development only)
  python -m app.db.reset_db

5. **Run redis server**
   redis-server

6. **Run fastAPI Server**

- uvicorn app.main:app --reload
