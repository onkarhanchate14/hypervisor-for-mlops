from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from app.core import deps, security
from app.schemas.user import UserCreate, User
from app.models.user import User as UserModel
from sqlalchemy.exc import IntegrityError

router = APIRouter()

@router.post("/login")
async def login(
    request: Request,
    response: Response,
    username: str,
    password: str,
    db: Session = Depends(deps.get_db)
):
    """
    Login endpoint that sets a session cookie
    """
    # Find user by username
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user or not security.verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Set user_id in session
    request.session["user_id"] = user.id
    del user.hashed_password
    
    return user

@router.post("/register", response_model=User)
async def register(
    *,
    request: Request,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate
):
    """
    Register a new user
    """
    # Check if username already exists
    if db.query(UserModel).filter(UserModel.username == user_in.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    try:
        # Create new user with hashed password
        user = UserModel(
            username=user_in.username,
            email=user_in.email,
            hashed_password=security.get_password_hash(user_in.password),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        request.session["user_id"] = user.id
        return user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

@router.post("/logout")
async def logout(request: Request):
    """
    Clear user session
    """
    if(not request.session.get("user_id", None)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not logged in"
        )
    request.session.clear()
    return {"message": "Successfully logged out"}
