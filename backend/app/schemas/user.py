from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# ==================== 用户基础信息 ====================

class UserBase(BaseModel):
    """用户基础信息"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    real_name: Optional[str] = Field(None, max_length=100)
    avatar: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    home_path: Optional[str] = None
    desc: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    """创建用户"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=5, max_length=50)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "admin",
                "password": "admin123",
                "real_name": "管理员",
                "email": "admin@example.com"
            }
        }
    )


class UserUpdate(UserBase):
    """更新用户"""
    password: Optional[str] = Field(None, min_length=6, max_length=50)


class User(UserBase):
    """用户响应"""
    id: int
    username: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserInfo(BaseModel):
    """用户详细信息（包含角色和token）"""
    user_id: str = Field(..., alias="userId", description="用户ID")
    username: str = Field(..., description="用户名")
    real_name: str = Field(..., alias="realName", description="真实姓名")
    avatar: str = Field(..., description="头像")
    desc: str = Field(..., description="用户描述")
    home_path: str = Field(..., alias="homePath", description="首页地址")
    roles: List[str] = Field(default_factory=list, description="角色列表")
    token: Optional[str] = Field(None, description="访问令牌")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "userId": "1",
                "username": "admin",
                "realName": "管理员",
                "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=admin",
                "desc": "系统管理员",
                "homePath": "/dashboard",
                "roles": ["admin", "user"],
                "token": "eyJhbGc..."
            }
        }
    )


# 分页响应
class UserListResponse(BaseModel):
    """用户列表响应模型"""
    total: int
    items: list[User]
    page: int
    page_size: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 100,
                "items": [],
                "page": 1,
                "page_size": 10
            }
        }
    )