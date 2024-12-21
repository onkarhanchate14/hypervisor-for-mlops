from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core import deps
from app.schemas.cluster import Cluster, ClusterCreate
from app.models.cluster import Cluster as ClusterModel
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=Cluster)
def create_cluster(
    *,
    db: Session = Depends(deps.get_db),
    cluster_in: ClusterCreate,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Create a new cluster with resource limits
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization to create clusters"
        )
    
    # Create cluster with initial resources
    cluster = ClusterModel(
        name=cluster_in.name,
        organization_id=current_user.organization_id,
        cpu_limit=cluster_in.cpu_limit,
        ram_limit=cluster_in.ram_limit,
        gpu_limit=cluster_in.gpu_limit,
        # Initially, available resources equal the limits
        cpu_available=cluster_in.cpu_limit,
        ram_available=cluster_in.ram_limit,
        gpu_available=cluster_in.gpu_limit
    )
    
    db.add(cluster)
    db.commit()
    db.refresh(cluster)
    return cluster

@router.get("/", response_model=List[Cluster])
def list_clusters(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    List all clusters in user's organization
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization to view clusters"
        )
    
    clusters = db.query(ClusterModel).filter(
        ClusterModel.organization_id == current_user.organization_id
    ).all()
    
    return clusters
