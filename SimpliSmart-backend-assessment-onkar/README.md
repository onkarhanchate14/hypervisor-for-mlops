# Hypervisor-like Service for MLOps Platform

## Overview
This is a FastAPI-based technical assessment designed to evaluate backend system design and implementation skills. The project implements a cluster management system with session-based authentication, organization management, and deployment scheduling.

## Assessment Tasks

### 1. User Authentication and Organization Management
- [ ] Implement session-based user authentication (login/logout)
- [ ] Complete user registration with password hashing
- [ ] Add organization creation with random invite codes
- [ ] Implement organization joining via invite codes

### 2. Cluster Management
- [ ] Create clusters with resource limits (CPU, RAM, GPU)
- [ ] Implement resource tracking and availability
- [ ] Add cluster listing for organization members
- [ ] Validate resource constraints

### 3. Deployment Management
- [ ] Develop a preemption-based scheduling algorithm to prioritize high-priority deployments
- [ ] Create deployment endpoints with resource requirements
- [ ] Implement basic scheduling algorithm
- [ ] Add deployment status tracking
- [ ] Handle resource allocation/deallocation

### 4. Advanced Features (Optional)
- [ ] Add support for deployment dependency management (e.g., Deployment A must complete before Deployment B starts)
- [ ] Implement Role-Based Access Control (RBAC)
- [ ] Add rate limiting
- [ ] Create comprehensive test coverage
- [ ] Enhance API documentation

## Project Structure
```
.
├── app
│   ├── api
│   │   └── v1
│   │       ├── endpoints
│   │       │   ├── auth.py        # Authentication endpoints
│   │       │   ├── clusters.py    # Cluster management
│   │       │   ├── deployments.py # Deployment handling
│   │       │   └── organizations.py # Organization management
│   │       └── api.py
│   ├── core
│   │   ├── config.py   # Configuration settings
│   │   ├── deps.py     # Dependencies and utilities
│   │   └── security.py # Security functions
│   ├── db
│   │   ├── base.py    # Database setup
│   │   └── session.py # Database session
│   ├── models         # SQLAlchemy models
│   │   ├── cluster.py
│   │   ├── deployment.py
│   │   ├── organization.py
│   │   └── user.py
│   ├── schemas       # Pydantic schemas
│   │   ├── cluster.py
│   │   ├── deployment.py
│   │   ├── organization.py
│   │   └── user.py
│   └── main.py      # Application entry point
└── tests
    ├── conftest.py  # Test configuration
    └── test_api     # API tests
```

## Authentication Flow
1. Register a new user (`POST /api/v1/auth/register`)
2. Login with credentials (`POST /api/v1/auth/login`)
   - Server sets a secure session cookie
3. Use session cookie for authenticated requests
4. Logout when finished (`POST /api/v1/auth/logout`)

## Organization Management
1. Create organization (generates invite code)
2. Share invite code with team members
3. Members join using invite code
4. Access organization resources (clusters, deployments)

## Testing
Run the test suite:
```bash
pytest
```

## Evaluation Criteria

### 1. Code Quality (40%)
- Clean, readable, and well-organized code
- Proper error handling
- Effective use of FastAPI features
- Type hints and validation

### 2. System Design (30%)
- Authentication implementation
- Resource management approach
- Scheduling algorithm design
- API structure

### 3. Functionality (20%)
- Working authentication system
- Proper resource tracking
- Successful deployment scheduling
- Error handling

### 4. Testing & Documentation (10%)
- Test coverage
- API documentation
- Code comments
- README completeness

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL database

### Setup Instructions
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Session Configuration
SECRET_KEY=your-secret-key  # For secure session encryption
SESSION_COOKIE_NAME=session  # Cookie name for the session
SESSION_MAX_AGE=1800        # Session duration in seconds (30 minutes)
```

3. Run the application:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

4. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Notes
- Focus on implementing core features first
- Use appropriate error handling throughout
- Document your design decisions
- Consider edge cases in your implementation