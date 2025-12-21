from pydantic import Field, ConfigDict
from typing import Optional

from app.schemas.base import BaseSchema, BaseInDBSchema, PaginatedResponse


# ==================== Label ====================

class LabelBase(BaseSchema):
    """标签基础 Schema - 所有字段可选"""
    name: Optional[str] = Field(None, max_length=100, description="标签名称")
    category: Optional[str] = Field(None, max_length=100, description="标签分类")
    project_id: Optional[int] = Field(None, gt=0, description="项目ID")


class LabelCreate(LabelBase):
    """创建标签 Schema - 标注必填字段"""
    name: str = Field(..., min_length=1, max_length=100)
    project_id: int = Field(..., gt=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "汽车",
                "category": "交通工具",
                "project_id": 1,
                "remark": "用于标注各类汽车"
            }
        }
    )


class LabelUpdate(LabelBase):
    """更新标签 Schema - 所有字段可选"""
    pass


class Label(BaseInDBSchema):
    """标签响应 Schema"""
    name: str
    category: Optional[str] = None
    project_id: int


class LabelDetail(Label):
    """标签详情 Schema - 包含使用统计"""
    image_count: int = Field(0, description="关联的图片数量")


# 使用通用分页响应
LabelListResponse = PaginatedResponse[Label]