from fastapi import APIRouter, HTTPException, Path as FastAPIPath
from pathlib import Path as FilePath
from starlette.responses import FileResponse
from app.core.config import settings
from app.schemas.file import FileResponseBase
from app.services.storage.storage_service import get_storage_service
from app.schemas import ApiResponse
from app.utils.web import get_content_type_by_extension

router = APIRouter()


@router.get("/files/url/{file_path:path}", response_model=ApiResponse[FileResponseBase])
async def serve_file(file_path: str = FastAPIPath(..., description="文件路径")):
    """提供文件访问服务"""
    try:
        storage_service = get_storage_service()
        storage_type = getattr(settings, 'STORAGE_TYPE', 'local').lower()

        # 检查文件是否存在
        if not await storage_service.file_exists(file_path):
            return ApiResponse.not_found(message="文件不存在")

        if storage_type == 'local':
            # 本地存储：返回本地访问URL
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
            file_url = f"{base_url}/api/v1/files/direct/{file_path}"

            # 获取文件信息
            base_path = getattr(settings, 'LOCAL_STORAGE_PATH', 'uploads')
            full_path = FilePath(base_path) / file_path

            file_size = None
            content_type = None

            if full_path.exists():
                file_size = full_path.stat().st_size
                # 根据文件扩展名推断content_type
                suffix = full_path.suffix.lower()
                content_type_map = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.gif': 'image/gif',
                    '.webp': 'image/webp',
                    '.bmp': 'image/bmp',
                    '.svg': 'image/svg+xml',
                    '.pdf': 'application/pdf',
                    '.txt': 'text/plain',
                    '.json': 'application/json',
                }
                content_type = content_type_map.get(suffix, 'application/octet-stream')

            file_response = FileResponseBase(
                url=file_url,
                file_type='local',
                file_path=file_path,
                content_type=content_type,
                file_size=file_size
            )

            return ApiResponse.success(
                data=file_response,
                message="获取本地文件URL成功"
            )

        elif storage_type == 'minio':
            # MinIO存储：返回预签名URL
            try:
                # 获取预签名URL（默认1小时有效期）
                expires_in = getattr(settings, 'PRESIGNED_URL_EXPIRES', 3600)
                presigned_url = await storage_service.get_file_url(file_path, expires_in)

                if not presigned_url:
                    return ApiResponse.error(message="生成预签名URL失败")

                # 获取文件元数据
                file_info = await storage_service.get_file_info(file_path)

                file_response = FileResponseBase(
                    url=presigned_url,
                    file_type='minio',
                    file_path=file_path,
                    content_type=file_info.get('content_type') if file_info else None,
                    file_size=file_info.get('size') if file_info else None
                )

                return ApiResponse.success(
                    data=file_response,
                    message="获取MinIO预签名URL成功"
                )

            except Exception as e:
                return ApiResponse.error(message=f"获取MinIO文件URL失败: {str(e)}")

        else:
            return ApiResponse.error(message=f"不支持的存储类型: {storage_type}")

    except Exception as e:
        return ApiResponse.error(message=f"获取文件失败: {str(e)}")


@router.get("/files/direct/{file_path:path}")
async def serve_file_direct(file_path: str = FastAPIPath(..., description="文件路径")):
    """直接提供本地文件（仅限本地存储）"""
    # 只有在使用本地存储时才提供此服务
    storage_type = getattr(settings, 'STORAGE_TYPE', 'local').lower()
    if storage_type != 'local':
        raise HTTPException(status_code=404, detail="File not found")

    storage_service = get_storage_service()

    # 检查文件是否存在
    if not await storage_service.file_exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # 构建完整的文件路径
    base_path = getattr(settings, 'LOCAL_STORAGE_PATH', 'uploads')
    full_path = FilePath(base_path) / file_path

    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # 检查文件是否在允许的目录内（安全检查）
    try:
        full_path.resolve().relative_to(FilePath(base_path).resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")

    # 根据文件类型设置适当的媒体类型
    suffix = full_path.suffix.lower()
    media_type_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.bmp': 'image/bmp',
        '.svg': 'image/svg+xml',
        '.pdf': 'application/pdf',
        '.txt': 'text/plain',
        '.json': 'application/json',
    }
    media_type = media_type_map.get(suffix, 'application/octet-stream')

    return FileResponse(
        full_path,
        media_type=media_type,
        filename=full_path.name
    )


@router.get("/files/info/{file_path:path}", response_model=ApiResponse[dict])
async def get_file_info(file_path: str = FastAPIPath(..., description="文件路径")):
    """获取文件信息"""
    try:
        storage_service = get_storage_service()
        storage_type = getattr(settings, 'STORAGE_TYPE', 'local').lower()

        # 检查文件是否存在
        if not await storage_service.file_exists(file_path):
            return ApiResponse.not_found(message="文件不存在")

        if storage_type == 'local':
            base_path = getattr(settings, 'LOCAL_STORAGE_PATH', 'uploads')
            full_path = FilePath(base_path) / file_path

            if full_path.exists():
                stat = full_path.stat()
                file_info = {
                    "file_path": file_path,
                    "file_name": full_path.name,
                    "file_size": stat.st_size,
                    "created_time": stat.st_ctime,
                    "modified_time": stat.st_mtime,
                    "storage_type": "local",
                    "content_type": get_content_type_by_extension(full_path.suffix)
                }
            else:
                return ApiResponse.not_found(message="文件不存在")

        elif storage_type == 'minio':
            # 获取MinIO文件信息
            file_info = await storage_service.get_file_info(file_path)
            if file_info:
                file_info.update({
                    "file_path": file_path,
                    "storage_type": "minio"
                })
            else:
                return ApiResponse.not_found(message="文件不存在")

        else:
            return ApiResponse.error(message=f"不支持的存储类型: {storage_type}")

        return ApiResponse.success(data=file_info, message="获取文件信息成功")

    except Exception as e:
        return ApiResponse.error(message=f"获取文件信息失败: {str(e)}")
