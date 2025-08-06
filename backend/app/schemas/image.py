from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
from .tag import Tag
from ..core.response import CamelCaseModel


class ImageBase(CamelCaseModel):
    filename: str
    file_path: str
    thumbnail_path: Optional[str] = None
    file_size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    meta_data: Optional[Dict[str, Any]] = None

class ImageCreate(BaseModel):
    project_id: int
    filename: str

class ImageUpdate(BaseModel):
    filename: Optional[str] = None

class Image(ImageBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ImageWithTags(Image):
    tags: List[Tag] = []