from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import FileResponse
from pathlib import Path as FilePath

from app.core.config import settings
from app.services.storage.storage_service import get_storage_service

router = APIRouter()

@router.get("/files/{file_path:path}")
async def serve_file(file_path: str = Path(..., description="文件路径")):
    """提供本地存储的文件访问"""
    # 只有在使用本地存储时才提供此服务
    if getattr(settings, 'STORAGE_TYPE', 'local').lower() != 'local':
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
    
    return FileResponse(full_path)
