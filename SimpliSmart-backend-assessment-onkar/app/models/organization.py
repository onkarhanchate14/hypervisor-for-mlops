from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Organization(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    invite_code = Column(String, unique=True, index=True)
    
    # Relationships
    users = relationship("User", back_populates="organization")
    clusters = relationship("Cluster", back_populates="organization")
