from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Cluster(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    organization_id = Column(Integer, ForeignKey("organization.id"))
    
    # Resource limits
    cpu_limit = Column(Float)
    ram_limit = Column(Float)
    gpu_limit = Column(Float)
    
    # Available resources
    cpu_available = Column(Float)
    ram_available = Column(Float)
    gpu_available = Column(Float)
    
    # Relationships
    organization = relationship("Organization", back_populates="clusters")
    deployments = relationship("Deployment", back_populates="cluster")
