from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):

    BASE_URL: str = ""

    # 数据库配置
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/label_manager"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379"
    
    # MinIO配置
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_BUCKET_NAME: str = "images"
    MINIO_SECURE: bool = False
    
    # 存储配置
    STORAGE_TYPE: str = "local"  # "local" 或 "minio"
    LOCAL_STORAGE_PATH: str = "uploads"
    
    # JWT配置
    SECRET_KEY: str = "fqee24fdsasfwec"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    
    # 缩略图配置
    THUMBNAIL_SIZE: tuple = (200, 200)
    THUMBNAIL_QUALITY: int = 85
    
    class Config:
        env_file = ".env"

settings = Settings()