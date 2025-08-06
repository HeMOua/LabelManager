from enum import Enum
from typing import Optional
import logging

from app.services.storage.base import StorageInterface
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


# 全局存储服务实例
def get_storage_service() -> StorageInterface:
    """获取存储服务实例"""
    # 从配置中获取存储类型，默认使用本地存储
    storage_type_str = getattr(settings, 'STORAGE_TYPE', 'local')
    
    try:
        storage_type = StorageType(storage_type_str.lower())
    except ValueError:
        logger.warning(f"Invalid storage type: {storage_type_str}, falling back to local storage")
        storage_type = StorageType.LOCAL
    
    # 创建存储服务
    storage_path = getattr(settings, 'LOCAL_STORAGE_PATH', 'uploads')
    storage_service = StorageFactory.create_storage(storage_type, base_path=storage_path)
    
    return storage_service
