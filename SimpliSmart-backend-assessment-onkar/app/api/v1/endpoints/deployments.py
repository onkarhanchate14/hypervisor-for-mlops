from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Response
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import asyncio
from datetime import datetime, timedelta
from redis import Redis
from app.core import deps
from app.core.redis import get_redis
from app.core.config import settings
from app.schemas.deployment import Deployment, DeploymentCreate
from app.models.deployment import Deployment as DeploymentModel, DeploymentStatus
from app.models.cluster import Cluster
from app.models.user import User
from fastapi.responses import Response
from sqlalchemy import func

router = APIRouter()

def check_resource_availability(cluster: Cluster, deployment: DeploymentCreate) -> bool:
    """Check if cluster has enough resources for deployment"""
    return (
        cluster.cpu_available >= deployment.cpu_required and
        cluster.ram_available >= deployment.ram_required and
        cluster.gpu_available >= deployment.gpu_required
    )

def allocate_resources(db: Session, cluster: Cluster, deployment: DeploymentCreate):
    """Allocate resources from cluster for deployment"""
    cluster.cpu_available -= deployment.cpu_required
    cluster.ram_available -= deployment.ram_required
    cluster.gpu_available -= deployment.gpu_required
    db.commit()

def deallocate_resources(db: Session, cluster: Cluster, deployment: DeploymentModel):
    """Return resources to cluster and trigger rescheduling"""
    cluster.cpu_available += deployment.cpu_required
    cluster.ram_available += deployment.ram_required
    cluster.gpu_available += deployment.gpu_required
    db.commit()
    
    # Trigger rescheduling of pending deployments
    schedule_pending_deployments(db, cluster)

def schedule_pending_deployments(db: Session, cluster: Cluster):
    """
    Schedule pending deployments based on priority and resource availability
    """
    redis = get_redis()
    
    # Get pending deployments from Redis queue
    while True:
        # Get highest priority pending deployment for this cluster
        pending_deployment_data = redis.zrevrange(
            f"cluster:{cluster.id}:pending_deployments",
            0, 0,
            withscores=True
        )
        
        if not pending_deployment_data:
            break
            
        deployment_json, priority = pending_deployment_data[0]
        deployment_data = json.loads(deployment_json)
        
        # Get deployment from database
        deployment = db.query(DeploymentModel).get(deployment_data['id'])
        
        if deployment and deployment.status == DeploymentStatus.PENDING:
            if check_resource_availability(cluster, deployment):
                # Allocate resources and start deployment
                allocate_resources(db, cluster, deployment)
                deployment.status = DeploymentStatus.RUNNING
                deployment.started_at = datetime.utcnow()
                db.commit()
                
                # Remove from pending queue
                redis.zrem(
                    f"cluster:{cluster.id}:pending_deployments",
                    deployment_json
                )
                
                # Set expiration timer
                asyncio.create_task(
                    handle_deployment_timeout(
                        db,
                        deployment.id,
                        settings.DEPLOYMENT_TIMEOUT_SECONDS
                    )
                )
            else:
                break
        else:
            # Remove invalid entry from queue
            redis.zrem(
                f"cluster:{cluster.id}:pending_deployments",
                deployment_json
            )

async def handle_deployment_timeout(db: Session, deployment_id: int, timeout_seconds: int):
    """Handle deployment completion after timeout"""
    await asyncio.sleep(timeout_seconds)
    
    deployment = db.query(DeploymentModel).get(deployment_id)
    if deployment and deployment.status == DeploymentStatus.RUNNING:
        cluster = db.query(Cluster).get(deployment.cluster_id)
        if cluster:
            # Mark deployment as completed
            deployment.status = DeploymentStatus.COMPLETED
            deployment.completed_at = datetime.utcnow()
            
            # Deallocate resources and trigger rescheduling
            deallocate_resources(db, cluster, deployment)
            db.commit()

@router.post("/", response_model=Deployment)
async def create_deployment(
    *,
    db: Session = Depends(deps.get_db),
    redis: Redis = Depends(get_redis),
    deployment_in: DeploymentCreate,
    current_user: User = Depends(deps.get_current_user)
):
    """Create a new deployment"""
    cluster = db.query(Cluster).filter(
        Cluster.id == deployment_in.cluster_id,
        Cluster.organization_id == current_user.organization_id
    ).first()
    
    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found or access denied"
        )
    
    # Create deployment
    deployment = DeploymentModel(
        name=deployment_in.name,
        cluster_id=deployment_in.cluster_id,
        docker_image=deployment_in.docker_image,
        cpu_required=deployment_in.cpu_required,
        ram_required=deployment_in.ram_required,
        gpu_required=deployment_in.gpu_required,
        priority=deployment_in.priority,
        status=DeploymentStatus.PENDING
    )
    
    db.add(deployment)
    db.commit()
    db.refresh(deployment)
    
    # Add to Redis pending queue
    deployment_data = {
        "id": deployment.id,
        "name": deployment.name,
        "cpu_required": deployment.cpu_required,
        "ram_required": deployment.ram_required,
        "gpu_required": deployment.gpu_required
    }
    
    redis.zadd(
        f"cluster:{cluster.id}:pending_deployments",
        {json.dumps(deployment_data): deployment.priority}
    )
    
    # Try to schedule pending deployments
    schedule_pending_deployments(db, cluster)
    
    return deployment

@router.get("/", response_model=List[Deployment])
def list_deployments(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    cluster_id: Optional[int] = None,
    deployment_status: Optional[DeploymentStatus] = None,
    priority: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    List deployments with optional filters:
    - cluster_id: Filter by specific cluster
    - status: Filter by deployment status
    - priority: Filter by priority level
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User must belong to an organization to view deployments"
        )

    # Start with base query
    query = db.query(DeploymentModel).join(
        Cluster, DeploymentModel.cluster_id == Cluster.id
    ).filter(
        Cluster.organization_id == current_user.organization_id
    )

    # Apply filters if provided
    if cluster_id is not None:
        query = query.filter(DeploymentModel.cluster_id == cluster_id)
    
    if deployment_status is not None:
        query = query.filter(DeploymentModel.status == deployment_status)
    
    if priority is not None:
        query = query.filter(DeploymentModel.priority == priority)

    # Order by creation time newest first and priority
    query = query.order_by(
        DeploymentModel.priority.desc(),
        DeploymentModel.created_at.desc()
    )

    # Apply pagination
    total = query.count()
    deployments = query.offset(skip).limit(limit).all()

    # Add total count in response headers
    response = Response()
    response.headers["X-Total-Count"] = str(total)
    
    return deployments

@router.get("/stats")
async def get_deployment_stats(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get deployment statistics for the organization
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization"
        )

    # Base query for organization's deployments
    base_query = db.query(DeploymentModel).join(
        Cluster, DeploymentModel.cluster_id == Cluster.id
    ).filter(
        Cluster.organization_id == current_user.organization_id
    )

    # Get counts by status
    status_counts = {
        status.value: base_query.filter(DeploymentModel.status == status).count()
        for status in DeploymentStatus
    }

    # Get priority distribution
    priority_counts = db.query(
        DeploymentModel.priority,
        func.count(DeploymentModel.id)
    ).join(
        Cluster, DeploymentModel.cluster_id == Cluster.id
    ).filter(
        Cluster.organization_id == current_user.organization_id
    ).group_by(
        DeploymentModel.priority
    ).all()

    # Calculate average completion time for completed deployments
    completed_deployments = base_query.filter(
        DeploymentModel.status == DeploymentStatus.COMPLETED,
        DeploymentModel.started_at.isnot(None),
        DeploymentModel.completed_at.isnot(None)
    ).all()

    avg_completion_time = None
    if completed_deployments:
        total_time = sum(
            (d.completed_at - d.started_at).total_seconds()
            for d in completed_deployments
        )
        avg_completion_time = total_time / len(completed_deployments)

    return {
        "total_deployments": base_query.count(),
        "status_distribution": status_counts,
        "priority_distribution": dict(priority_counts),
        "average_completion_time_seconds": avg_completion_time,
        "active_deployments": status_counts["running"],
        "pending_deployments": status_counts["pending"]
    }

@router.get("/{deployment_id}", response_model=Deployment)
async def get_deployment(
    deployment_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get detailed information about a specific deployment
    """
    deployment = db.query(DeploymentModel).join(
        Cluster, DeploymentModel.cluster_id == Cluster.id
    ).filter(
        DeploymentModel.id == deployment_id,
        Cluster.organization_id == current_user.organization_id
    ).first()

    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found or access denied"
        )

    return deployment

@router.post("/{deployment_id}/cancel", response_model=Deployment)
async def cancel_deployment(
    *,
    db: Session = Depends(deps.get_db),
    redis: Redis = Depends(get_redis),
    deployment_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """Cancel a deployment and deallocate its resources"""
    deployment = db.query(DeploymentModel).join(
        Cluster, DeploymentModel.cluster_id == Cluster.id
    ).filter(
        DeploymentModel.id == deployment_id,
        Cluster.organization_id == current_user.organization_id
    ).first()
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found or access denied"
        )
    
    cluster = db.query(Cluster).get(deployment.cluster_id)
    
    if deployment.status == DeploymentStatus.RUNNING:
        # Deallocate resources and trigger rescheduling
        deallocate_resources(db, cluster, deployment)
    elif deployment.status == DeploymentStatus.PENDING:
        # Remove from pending queue
        deployment_data = {
            "id": deployment.id,
            "name": deployment.name,
            "cpu_required": deployment.cpu_required,
            "ram_required": deployment.ram_required,
            "gpu_required": deployment.gpu_required
        }
        redis.zrem(
            f"cluster:{cluster.id}:pending_deployments",
            json.dumps(deployment_data)
        )
    
    deployment.status = DeploymentStatus.FAILED
    deployment.completed_at = datetime.utcnow()
    db.commit()
    
    return deployment
