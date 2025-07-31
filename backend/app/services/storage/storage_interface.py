from abc import ABC, abstractmethod
from typing import Optional


class StorageInterface(ABC):
    """存储服务接口"""
    
    @abstractmethod
    async def ensure_storage_ready(self) -> None:
        """确保存储已准备就绪"""
        pass
    
    @abstractmethod
    async def upload_file(self, file_data: bytes, object_name: str, content_type: str = "application/octet-stream") -> bool:
        """上传文件"""
        pass
    
    @abstractmethod
    async def download_file(self, object_name: str) -> Optional[bytes]:
        """下载文件"""
        pass
    
    @abstractmethod
    async def delete_file(self, object_name: str) -> bool:
        """删除文件"""
        pass
    
    @abstractmethod
    async def get_file_url(self, object_name: str, expires: int = 3600) -> Optional[str]:
        """获取文件URL"""
        pass
    
    @abstractmethod
    async def file_exists(self, object_name: str) -> bool:
        """检查文件是否存在"""
        pass
