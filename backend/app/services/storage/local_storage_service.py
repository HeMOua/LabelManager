from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger
from app.services.storage.base import StorageInterface
from app.utils.web import get_content_type_by_extension


class LocalStorageService(StorageInterface):
    """本地存储服务实现"""
    
    def __init__(self, base_path: str = "uploads"):
        self.base_path = Path(base_path)
        
    async def ensure_storage_ready(self) -> None:
        """确保存储目录存在"""
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Local storage directory ready: {self.base_path}")
        except Exception as e:
            logger.error(f"Error creating storage directory: {e}")
            raise
    
    async def upload_file(self, file_data: bytes, object_name: str, content_type: str = "application/octet-stream") -> bool:
        """上传文件到本地存储"""
        try:
            file_path = self.base_path / object_name
            # 确保父目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            logger.info(f"File uploaded successfully: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error uploading file {object_name}: {e}")
            return False
    
    async def download_file(self, object_name: str) -> Optional[bytes]:
        """从本地存储下载文件"""
        try:
            file_path = self.base_path / object_name
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                return None
                
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error downloading file {object_name}: {e}")
            return None
    
    async def delete_file(self, object_name: str) -> bool:
        """从本地存储删除文件"""
        try:
            file_path = self.base_path / object_name
            if file_path.exists():
                file_path.unlink()
                logger.info(f"File deleted successfully: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error deleting file {object_name}: {e}")
            return False
    
    async def get_file_url(self, object_name: str, expires: int = 3600) -> Optional[str]:
        """获取本地文件URL（通过API端点）"""
        try:
            file_path = self.base_path / object_name
            if file_path.exists():
                # 返回相对路径，实际URL由API端点处理
                return f"/api/v1/files/{object_name}"
            return None
        except Exception as e:
            logger.error(f"Error getting file URL {object_name}: {e}")
            return None
    
    async def file_exists(self, object_name: str) -> bool:
        """检查文件是否存在"""
        try:
            file_path = self.base_path / object_name
            return file_path.exists()
        except Exception as e:
            logger.error(f"Error checking file existence {object_name}: {e}")
            return False

    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """获取本地文件信息"""
        try:
            full_path = Path(self.base_path) / file_path
            if full_path.exists():
                stat = full_path.stat()
                return {
                    "file_name": full_path.name,
                    "file_size": stat.st_size,
                    "content_type": get_content_type_by_extension(full_path.suffix),
                    "created_time": stat.st_ctime,
                    "modified_time": stat.st_mtime
                }
            return None
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None
