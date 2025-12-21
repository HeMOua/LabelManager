from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class LoginParams(BaseModel):
    """登录参数"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=5, max_length=50, description="密码")
    captcha: Optional[bool] = Field(True, description="是否需要验证码")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "admin",
                "password": "admin",
                "captcha": True
            }
        }
    )


class LoginResult(BaseModel):
    """登录返回结果"""
    access_token: str = Field(..., alias="accessToken", description="访问令牌")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )


class RefreshTokenResult(BaseModel):
    """刷新token返回结果"""
    data: str = Field(..., description="新的访问令牌")
    status: int = Field(default=0, description="状态码")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "status": 0
            }
        }
    )