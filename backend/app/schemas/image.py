from pydantic import Field, ConfigDict
from typing import Optional, Dict, Any, List

from app.schemas.base import BaseSchema, BaseInDBSchema, PaginatedResponse


# ==================== Image ====================

class ImageBase(BaseSchema):
    """图片基础 Schema - 所有字段可选"""
    filename: Optional[str] = Field(None, max_length=255, description="文件名")
    image_path: Optional[str] = Field(None, max_length=500, description="图片路径")
    thumbnail_path: Optional[str] = Field(None, max_length=500, description="缩略图路径")
    file_size: Optional[int] = Field(None, ge=0, description="文件大小（字节）")
    width: Optional[int] = Field(None, ge=0, description="图片宽度")
    height: Optional[int] = Field(None, ge=0, description="图片高度")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据（JSON）")
    project_id: Optional[int] = Field(None, gt=0, description="项目ID")


class ImageCreate(ImageBase):
    """创建图片 Schema - 标注必填字段"""
    filename: str = Field(..., min_length=1, max_length=255)
    image_path: str = Field(..., min_length=1, max_length=500)
    project_id: int = Field(..., gt=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "IMG_001.jpg",
                "image_path": "/uploads/projects/1/images/IMG_001.jpg",
                "thumbnail_path": "/uploads/projects/1/thumbnails/IMG_001_thumb.jpg",
                "file_size": 2048576,
                "width": 1920,
                "height": 1080,
                "metadata": {"camera": "Canon EOS R5", "iso": 400},
                "project_id": 1
            }
        }
    )


class ImageUpdate(ImageBase):
    """更新图片 Schema - 所有字段可选"""
    pass


class Image(BaseInDBSchema):
    """图片响应 Schema"""
    filename: str
    image_path: str
    thumbnail_path: Optional[str] = None
    file_size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    project_id: int


class ImageDetail(Image):
    """图片详情 Schema - 包含关联数据"""
    labels: List["LabelSimple"] = Field(default_factory=list, description="标签列表")
    annotation_count: int = Field(0, description="标注数量")


# 使用通用分页响应
ImageListResponse = PaginatedResponse[Image]


# ==================== Image Label Association ====================

class ImageLabelAssociation(BaseSchema):
    """图片标签关联 Schema"""
    image_id: int = Field(..., gt=0, description="图片ID")
    label_ids: List[int] = Field(..., min_length=1, description="标签ID列表")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "image_id": 1,
                "label_ids": [1, 2, 3]
            }
        }
    )


# 简化标签模型（避免循环导入）
class LabelSimple(BaseSchema):
    """标签简化 Schema"""
    id: int
    name: str
    category: Optional[str] = None


# 更新 ImageDetail 的模型
ImageDetail.model_rebuild()