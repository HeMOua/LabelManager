from pydantic import Field, ConfigDict
from typing import Optional

from app.schemas.base import BaseSchema, BaseInDBSchema, PaginatedResponse


# ==================== AnnotationGroup ====================

class AnnotationGroupBase(BaseSchema):
    """标注组基础 Schema - 所有字段可选"""
    project_id: Optional[int] = Field(None, gt=0, description="项目ID")
    name: Optional[str] = Field(None, max_length=100, description="标注组名称")
    description: Optional[str] = Field(None, description="标注组描述")


class AnnotationGroupCreate(AnnotationGroupBase):
    """创建标注组 Schema - 标注必填字段"""
    project_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=100)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "project_id": 1,
                "name": "第一批标注",
                "description": "2024年第一批标注数据",
                "remark": "包含500张图片"
            }
        }
    )


class AnnotationGroupUpdate(AnnotationGroupBase):
    """更新标注组 Schema - 所有字段可选"""
    pass


class AnnotationGroup(BaseInDBSchema):
    """标注组响应 Schema"""
    project_id: int
    name: str
    description: Optional[str] = None


class AnnotationGroupDetail(AnnotationGroup):
    """标注组详情 Schema - 包含统计信息"""
    annotation_file_count: int = Field(0, description="标注文件数量")


# 使用通用分页响应
AnnotationGroupListResponse = PaginatedResponse[AnnotationGroup]