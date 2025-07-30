from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProjectWithImageCount(Project):
    image_count: int = 0