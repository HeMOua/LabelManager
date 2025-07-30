from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
import os

from app.core.database import get_db
from app.core.config import settings
from app.services.image_service import ImageService
from app.services.minio_service import MinioService
from app.schemas import ImageWithTags
from app.models import Image

router = APIRouter()

@router.post("/upload/{project_id}", response_model=ImageWithTags)
async def upload_image(
    project_id: int,
    file: UploadFile = File(...),
    tag_ids: str = Form("[]"),  # JSON字符串形式的标签ID列表
    db: Session = Depends(get_db)
):
    """上传图片"""
    # 验证文件类型
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # 验证文件大小
    file_data = await file.read()
    if len(file_data) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE} bytes"
        )
    
    image_service = ImageService(db)
    
    try:
        # 上传图片
        db_image = await image_service.upload_image(
            project_id=project_id,
            file_data=file_data,
            filename=file.filename,
            content_type=file.content_type
        )
        
        # 添加标签
        import json
        try:
            tag_ids_list = json.loads(tag_ids)
            if tag_ids_list:
                image_service.add_tags_to_image(db_image.id, tag_ids_list)
        except json.JSONDecodeError:
            pass  # 忽略标签解析错误
        
        # 返回带标签的图片信息
        return image_service.get_image_with_tags(db_image.id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/project/{project_id}", response_model=List[ImageWithTags])
def get_project_images(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取项目的图片列表"""
    image_service = ImageService(db)
    images = db.query(Image).filter(Image.project_id == project_id).offset(skip).limit(limit).all()
    
    result = []
    for image in images:
        image_with_tags = image_service.get_image_with_tags(image.id)
        if image_with_tags:
            result.append(image_with_tags)
    
    return result

@router.get("/{image_id}", response_model=ImageWithTags)
def get_image(image_id: int, db: Session = Depends(get_db)):
    """获取图片详情"""
    image_service = ImageService(db)
    image = image_service.get_image_with_tags(image_id)
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

@router.put("/{image_id}/tags")
def update_image_tags(
    image_id: int,
    tag_ids: List[int],
    db: Session = Depends(get_db)
):
    """更新图片标签"""
    image_service = ImageService(db)
    
    # 检查图片是否存在
    if not db.query(Image).filter(Image.id == image_id).first():
        raise HTTPException(status_code=404, detail="Image not found")
    
    if image_service.add_tags_to_image(image_id, tag_ids):
        return {"message": "Tags updated successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update tags")

@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(image_id: int, db: Session = Depends(get_db)):
    """删除图片"""
    image_service = ImageService(db)
    if not image_service.delete_image(image_id):
        raise HTTPException(status_code=404, detail="Image not found")

@router.get("/{image_id}/url")
def get_image_url(image_id: int, thumbnail: bool = False, db: Session = Depends(get_db)):
    """获取图片URL"""
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    minio_service = MinioService()
    file_path = image.thumbnail_path if thumbnail and image.thumbnail_path else image.file_path
    url = minio_service.get_file_url(file_path)
    
    if not url:
        raise HTTPException(status_code=500, detail="Failed to generate file URL")
    
    return {"url": url}