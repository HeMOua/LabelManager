from pydantic import Field, ConfigDict
from typing import Optional

from app.schemas.base import BaseSchema, BaseInDBSchema, PaginatedResponse


# ==================== Project ====================

class ProjectBase(BaseSchema):
    """项目基础 Schema - 所有字段可选"""
    name: Optional[str] = Field(None, max_length=100, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")


class ProjectCreate(ProjectBase):
    """创建项目 Schema - 标注必填字段"""
    name: str = Field(..., min_length=1, max_length=100, description="项目名称")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "智能驾驶标注项目",
                "description": "用于自动驾驶场景的图像标注",
                "remark": "第一期项目"
            }
        }
    )


class ProjectUpdate(ProjectBase):
    """更新项目 Schema - 所有字段可选"""
    pass


class Project(BaseInDBSchema):
    """项目响应 Schema"""
    name: str
    description: Optional[str] = None


class ProjectDetail(Project):
    """项目详情 Schema - 包含统计信息"""
    image_count: int = Field(0, description="图片数量")
    label_count: int = Field(0, description="标签数量")
    annotation_group_count: int = Field(0, description="标注组数量")


# 使用通用分页响应
ProjectListResponse = PaginatedResponse[Project]