from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

from app.core.response import CamelCaseModel


class TagBase(CamelCaseModel):
    name: str
    category: str
    color: str = Field(default="#007bff", description="标签颜色")


class TagCreate(TagBase):
    project_id: Optional[int] = Field(None, description="项目ID，为空表示创建全局标签")


class TagUpdate(TagBase):
    pass


class Tag(TagBase):
    id: int
    project_id: Optional[int]
    created_at: datetime
    tag_type: Literal["global", "project"]
    is_global: bool

    class Config:
        from_attributes = True


class TagWithCount(Tag):
    image_count: int = 0


class TagWithProject(Tag):
    project_name: Optional[str] = None