from pydantic import Field, BaseModel
from typing import Optional
from app.models.deployment import DeploymentStatus

class DeploymentBase(BaseModel):
    name: str
    docker_image: str
    cpu_required: float
    ram_required: float
    gpu_required: float
    priority: int = Field(1, ge=1, le=3)

class DeploymentCreate(DeploymentBase):
    cluster_id: int

class DeploymentUpdate(DeploymentBase):
    pass

class Deployment(DeploymentBase):
    id: int
    cluster_id: int
    status: DeploymentStatus

    class Config:
        from_attributes = True
