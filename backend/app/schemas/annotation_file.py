from pydantic import Field, ConfigDict
from typing import Optional

from app.schemas.base import BaseSchema, BaseInDBSchema, PaginatedResponse


# ==================== AnnotationFile ====================

class AnnotationFileBase(BaseSchema):
    """标注文件基础 Schema - 所有字段可选"""
    annotation_group_id: Optional[int] = Field(None, gt=0, description="标注组ID")
    image_id: Optional[int] = Field(None, gt=0, description="图片ID")
    content: Optional[str] = Field(None, description="标注内容")
    format: Optional[str] = Field(None, max_length=16, description="标注格式")
    version: Optional[int] = Field(None, ge=1, description="版本号")


class AnnotationFileCreate(AnnotationFileBase):
    """创建标注文件 Schema - 标注必填字段"""
    annotation_group_id: int = Field(..., gt=0)
    image_id: int = Field(..., gt=0)
    content: str = Field(..., min_length=1)
    format: str = Field(..., min_length=1, max_length=16)
    version: int = Field(default=1, ge=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "annotation_group_id": 1,
                "image_id": 1,
                "content": '{"objects": [{"type": "car", "bbox": [100, 100, 200, 200]}]}',
                "format": "json",
                "version": 1,
                "remark": "初始版本"
            }
        }
    )


class AnnotationFileUpdate(AnnotationFileBase):
    """更新标注文件 Schema - 所有字段可选"""
    pass


class AnnotationFile(BaseInDBSchema):
    """标注文件响应 Schema"""
    annotation_group_id: int
    image_id: int
    content: str
    format: str
    version: int


class AnnotationFileDetail(AnnotationFile):
    """标注文件详情 Schema - 包含关联信息"""
    image_filename: Optional[str] = Field(None, description="图片文件名")
    annotation_group_name: Optional[str] = Field(None, description="标注组名称")


# 使用通用分页响应
AnnotationFileListResponse = PaginatedResponse[AnnotationFile]