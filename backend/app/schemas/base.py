from pydantic import BaseModel, ConfigDict
from typing import Optional, TypeVar, Generic, List
from datetime import datetime


# ==================== 基础 Schema ====================

class BaseSchema(BaseModel):
    """基础 Schema - 所有字段可选"""
    remark: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class BaseInDBSchema(BaseSchema):
    """数据库基础 Schema - 包含审计字段"""
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_by: Optional[int] = None
    updated_at: Optional[datetime] = None


# ==================== 通用分页响应 ====================

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """
    通用分页响应
    适用于所有列表接口

    使用示例：
        ProjectListResponse = PaginatedResponse[Project]
        ImageListResponse = PaginatedResponse[Image]
    """
    total: int
    items: List[T]
    page: int
    page_size: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 100,
                "items": [],
                "page": 1,
                "page_size": 20
            }
        }
    )


# ==================== 通用响应 ====================

class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Operation successful"
            }
        }
    )