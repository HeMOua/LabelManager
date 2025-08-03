from typing import Generic, TypeVar, Optional
from app.core.response import CamelCaseModel

T = TypeVar('T')


class ApiResponse(CamelCaseModel, Generic[T]):
    """统一的API响应格式"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None

    @classmethod
    def success(cls, data: T = None, message: str = "操作成功") -> "ApiResponse[T]":
        """成功响应"""
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(cls, code: int = 500, message: str = "操作失败", data: T = None) -> "ApiResponse[T]":
        """错误响应"""
        return cls(code=code, message=message, data=data)

    @classmethod
    def not_found(cls, message: str = "资源不存在") -> "ApiResponse[None]":
        """404响应"""
        return cls(code=404, message=message, data=None)

    @classmethod
    def bad_request(cls, message: str = "请求参数错误") -> "ApiResponse[None]":
        """400响应"""
        return cls(code=400, message=message, data=None)
