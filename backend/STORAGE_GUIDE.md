# 存储服务策略模式使用指南

## 概述

本项目使用策略模式实现了灵活的存储服务，支持本地存储和MinIO对象存储两种方式。

## 存储策略

### 1. 本地存储 (LocalStorageService)

- 文件存储在本地文件系统中
- 通过API端点提供文件访问
- 适合开发环境和小规模部署

### 2. MinIO存储 (MinioService)

- 文件存储在MinIO对象存储中
- 支持分布式存储和高可用
- 适合生产环境和大规模部署

## 配置方式

### 本地存储配置

```env
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=uploads
```

### MinIO存储配置

```env
STORAGE_TYPE=minio
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_BUCKET_NAME=images
MINIO_SECURE=false
```

## 使用方式

### 1. 获取存储服务实例

```python
from app.services.storage.storage_service import get_storage_service

storage_service = get_storage_service()
```

### 2. 基本操作

```python
# 初始化存储
await storage_service.ensure_storage_ready()

# 上传文件
success = await storage_service.upload_file(
    file_data=file_bytes,
    object_name="images/photo.jpg",
    content_type="image/jpeg"
)

# 下载文件
file_data = await storage_service.download_file("images/photo.jpg")

# 获取文件URL
url = await storage_service.get_file_url("images/photo.jpg")

# 检查文件是否存在
exists = await storage_service.file_exists("images/photo.jpg")

# 删除文件
success = await storage_service.delete_file("images/photo.jpg")
```

## 扩展新的存储策略

1. 实现 `StorageInterface` 接口：

```python
from app.services.storage.storage_interface import StorageInterface


class NewStorageService(StorageInterface):
    async def ensure_storage_ready(self) -> None:
        # 实现存储准备逻辑
        pass

    async def upload_file(self, file_data: bytes, object_name: str, content_type: str) -> bool:
        # 实现文件上传逻辑
        pass

    # ... 实现其他接口方法
```

2. 在 `StorageFactory` 中添加新策略：

```python
class StorageType(Enum):
    LOCAL = "local"
    MINIO = "minio"
    NEW_STORAGE = "new_storage"  # 新增

class StorageFactory:
    @staticmethod
    def create_storage(storage_type: StorageType, **kwargs) -> StorageInterface:
        if storage_type == StorageType.NEW_STORAGE:
            return NewStorageService(**kwargs)
        # ... 其他策略
```

## 文件访问

### 本地存储

文件通过API端点访问：`/api/v1/files/{file_path}`

### MinIO存储

通过预签名URL访问文件，URL由MinIO服务生成。

## 注意事项

1. 切换存储类型时，需要迁移现有文件
2. 本地存储的文件路径需要在API端点的安全范围内
3. MinIO存储需要确保网络连接和认证配置正确
4. 生产环境建议使用MinIO或其他对象存储服务
