from pydantic import BaseModel
from typing import Optional

class OrganizationBase(BaseModel):
    name: str

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: int
    invite_code: str

    class Config:
        from_attributes = True

class OrganizationInvite(BaseModel):
    invite_code: str
