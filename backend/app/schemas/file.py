from typing import Optional
from app.core.response import CamelCaseModel


class FileResponseBase(CamelCaseModel):
    """文件响应模型"""
    url: str
    file_type: str  # 'local' 或 'minio'
    file_path: str
    content_type: Optional[str] = None
    file_size: Optional[int] = None
