from enum import Enum
from typing import Optional
import logging

from app.services.storage.storage_interface import StorageInterface
from app.services.storage.local_storage_service import LocalStorageService
from app.services.storage.minio_service import MinioService
from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageType(Enum):
    """存储类型枚举"""
    LOCAL = "local"
    MINIO = "minio"


class StorageFactory:
    """存储服务工厂"""
    
    @staticmethod
    def create_storage(storage_type: StorageType, **kwargs) -> StorageInterface:
        """创建存储服务实例"""
        if storage_type == StorageType.LOCAL:
            base_path = kwargs.get('base_path', 'uploads')
            return LocalStorageService(base_path=base_path)
        elif storage_type == StorageType.MINIO:
            return MinioService()
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")


class StorageContext:
    """存储上下文，实现策略模式"""
    
    def __init__(self, storage_service: StorageInterface):
        self._storage_service = storage_service
    
    def set_storage_service(self, storage_service: StorageInterface):
        """设置存储服务"""
        self._storage_service = storage_service
    
    async def ensure_storage_ready(self) -> None:
        """确保存储已准备就绪"""
        return await self._storage_service.ensure_storage_ready()
    
    async def upload_file(self, file_data: bytes, object_name: str, content_type: str = "application/octet-stream") -> bool:
        """上传文件"""
        return await self._storage_service.upload_file(file_data, object_name, content_type)
    
    async def download_file(self, object_name: str) -> Optional[bytes]:
        """下载文件"""
        return await self._storage_service.download_file(object_name)
    
    async def delete_file(self, object_name: str) -> bool:
        """删除文件"""
        return await self._storage_service.delete_file(object_name)
    
    async def get_file_url(self, object_name: str, expires: int = 3600) -> Optional[str]:
        """获取文件URL"""
        return await self._storage_service.get_file_url(object_name, expires)
    
    async def file_exists(self, object_name: str) -> bool:
        """检查文件是否存在"""
        return await self._storage_service.file_exists(object_name)


# 全局存储服务实例
def get_storage_service() -> StorageContext:
    """获取存储服务实例"""
    # 从配置中获取存储类型，默认使用本地存储
    storage_type_str = getattr(settings, 'STORAGE_TYPE', 'local')
    
    try:
        storage_type = StorageType(storage_type_str.lower())
    except ValueError:
        logger.warning(f"Invalid storage type: {storage_type_str}, falling back to local storage")
        storage_type = StorageType.LOCAL
    
    # 创建存储服务
    if storage_type == StorageType.LOCAL:
        storage_path = getattr(settings, 'LOCAL_STORAGE_PATH', 'uploads')
        storage_service = StorageFactory.create_storage(storage_type, base_path=storage_path)
    else:
        storage_service = StorageFactory.create_storage(storage_type)
    
    return StorageContext(storage_service)
