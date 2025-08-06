from asyncpg.pgproto.pgproto import timedelta
from minio import Minio
from minio.error import S3Error
import io
from typing import Optional, Dict, Any
import logging

from app.core.config import settings
from app.services.storage.base import StorageInterface
from loguru import logger

class MinioService(StorageInterface):
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
    
    async def ensure_storage_ready(self):
        """确保存储已准备就绪"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error creating bucket: {e}")
            raise
    
    async def upload_file(self, file_data: bytes, object_name: str, content_type: str = "application/octet-stream") -> bool:
        """上传文件到MinIO"""
        try:
            file_stream = io.BytesIO(file_data)
            self.client.put_object(
                self.bucket_name,
                object_name,
                file_stream,
                length=len(file_data),
                content_type=content_type
            )
            return True
        except S3Error as e:
            logger.error(f"Error uploading file {object_name}: {e}")
            return False
    
    async def download_file(self, object_name: str) -> Optional[bytes]:
        """从MinIO下载文件"""
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            return response.read()
        except S3Error as e:
            logger.error(f"Error downloading file {object_name}: {e}")
            return None
        finally:
            if 'response' in locals():
                response.close()
                response.release_conn()
    
    async def delete_file(self, object_name: str) -> bool:
        """从MinIO删除文件"""
        try:
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            logger.error(f"Error deleting file {object_name}: {e}")
            return False
    
    async def get_file_url(self, object_name: str, expires: int = 3600) -> Optional[str]:
        """获取文件的预签名URL"""
        try:
            return self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=timedelta(seconds=expires)
            )
        except S3Error as e:
            logger.error(f"Error getting file URL {object_name}: {e}")
            return None
    
    async def file_exists(self, object_name: str) -> bool:
        """检查文件是否存在"""
        try:
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            if e.code == 'NoSuchKey':
                return False
            logger.error(f"Error checking file existence {object_name}: {e}")
            return False

    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """获取MinIO文件信息"""
        try:
            # 使用MinIO客户端获取文件统计信息
            stat = self.client.stat_object(self.bucket_name, file_path)
            return {
                "file_name": file_path.split('/')[-1],
                "file_size": stat.size,
                "content_type": stat.content_type,
                "created_time": stat.last_modified.timestamp() if stat.last_modified else None,
                "etag": stat.etag,
                "version_id": stat.version_id
            }
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None
