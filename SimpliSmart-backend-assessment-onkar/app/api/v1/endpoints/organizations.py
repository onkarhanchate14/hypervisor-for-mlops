from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import secrets
from app.core import deps
from app.schemas.organization import Organization, OrganizationCreate, OrganizationInvite
from app.models.organization import Organization as OrganizationModel
from app.models.user import User

router = APIRouter()

def generate_invite_code() -> str:
    """Generate a random 8-character invite code"""
    return secrets.token_urlsafe(6)[:8]

@router.post("/", response_model=Organization)
def create_organization(
    *,
    db: Session = Depends(deps.get_db),
    organization_in: OrganizationCreate,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Create a new organization and set the current user as a member
    """
    if current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already belongs to an organization"
        )
    
    # Create organization with invite code
    try:
        organization = OrganizationModel(
            name=organization_in.name,
            invite_code=generate_invite_code()
        )
        db.add(organization)
        db.commit()
        db.refresh(organization)
        
        # Add current user to organization
        current_user.organization_id = organization.id
        db.commit()
        
        return organization
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization already exists"

        )

@router.post("/{invite_code}/join")
def join_organization(
    *,
    db: Session = Depends(deps.get_db),
    invite_code: str,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Join an organization using an invite code
    """
    if current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already belongs to an organization"
        )
    
    organization = db.query(OrganizationModel).filter(
        OrganizationModel.invite_code == invite_code
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invite code"
        )
    
    current_user.organization_id = organization.id
    db.commit()
    
    return {"message": f"Successfully joined organization: {organization.name}"}

@router.get("/share/invite", response_model=OrganizationInvite)
def get_invite(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Share organization invite
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User doesn't belongs to an organization"
        )
    
    try:
        organization = db.query(OrganizationModel).filter(
        OrganizationModel.id == current_user.organization_id
    ).first()
        return organization
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization doesn't exists"

        )

    
