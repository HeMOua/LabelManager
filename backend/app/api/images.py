from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy import func
from sqlalchemy.orm import Session
import os
import json

from app.core.database import get_db
from app.core.config import settings
from app.schemas.base import ApiResponseList
from app.services.persistence.image_service import ImageService
from app.services.storage.storage_service import get_storage_service
from app.schemas import ImageWithTags, ApiResponse
from app.models import Image

router = APIRouter()


@router.post("/upload/{project_id}", response_model=ApiResponse[ImageWithTags])
async def upload_image(
        project_id: int,
        file: UploadFile = File(...),
        tag_ids: str = Form("[]"),  # JSON字符串形式的标签ID列表
        db: Session = Depends(get_db)
):
    """上传图片"""
    try:
        # 验证文件类型
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            return ApiResponse.bad_request(
                message=f"文件类型不支持。支持的类型: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

        # 验证文件大小
        file_data = await file.read()
        if len(file_data) > settings.MAX_FILE_SIZE:
            return ApiResponse.bad_request(
                message=f"文件过大。最大限制: {settings.MAX_FILE_SIZE} bytes"
            )

        image_service = ImageService(db)

        # 上传图片
        db_image = await image_service.upload_image(
            project_id=project_id,
            file_data=file_data,
            filename=file.filename,
            content_type=file.content_type
        )

        # 添加标签
        try:
            tag_ids_list = json.loads(tag_ids)
            if tag_ids_list:
                image_service.add_tags_to_image(db_image.id, tag_ids_list)
        except json.JSONDecodeError:
            pass  # 忽略标签解析错误

        # 返回带标签的图片信息
        image_with_tags = image_service.get_image_with_tags(db_image.id)
        return ApiResponse.success(data=image_with_tags, message="图片上传成功")

    except Exception as e:
        return ApiResponse.error(message=f"图片上传失败: {str(e)}")


@router.get("/project/{project_id}", response_model=ApiResponseList[ImageWithTags])
def get_project_images(
        project_id: int,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """获取项目的图片列表"""
    try:
        image_service = ImageService(db)
        total = db.query(Image).filter(Image.project_id == project_id).count()
        images = db.query(Image).filter(Image.project_id == project_id).offset(skip).limit(limit).all()

        result = []
        for image in images:
            image_with_tags = image_service.get_image_with_tags(image.id)
            if image_with_tags:
                result.append(image_with_tags)

        return ApiResponseList.success(data=result, total=total, message="获取项目图片列表成功")
    except Exception as e:
        return ApiResponse.error(message=f"获取项目图片列表失败: {str(e)}")


@router.get("/{image_id}", response_model=ApiResponse[ImageWithTags])
def get_image(image_id: int, db: Session = Depends(get_db)):
    """获取图片详情"""
    try:
        image_service = ImageService(db)
        image = image_service.get_image_with_tags(image_id)
        if image is None:
            return ApiResponse.not_found(message="图片不存在")
        return ApiResponse.success(data=image, message="获取图片详情成功")
    except Exception as e:
        return ApiResponse.error(message=f"获取图片详情失败: {str(e)}")


@router.put("/{image_id}/tags", response_model=ApiResponse[None])
def update_image_tags(
        image_id: int,
        tag_ids: List[int],
        db: Session = Depends(get_db)
):
    """更新图片标签"""
    try:
        image_service = ImageService(db)

        # 检查图片是否存在
        if not db.query(Image).filter(Image.id == image_id).first():
            return ApiResponse.not_found(message="图片不存在")

        if image_service.add_tags_to_image(image_id, tag_ids):
            return ApiResponse.success(message="标签更新成功")
        else:
            return ApiResponse.error(message="标签更新失败")
    except Exception as e:
        return ApiResponse.error(message=f"标签更新失败: {str(e)}")


@router.delete("/{image_id}", response_model=ApiResponse[None])
async def delete_image(image_id: int, db: Session = Depends(get_db)):
    """删除图片"""
    try:
        image_service = ImageService(db)
        if not await image_service.delete_image(image_id):
            return ApiResponse.not_found(message="图片不存在")
        return ApiResponse.success(message="图片删除成功")
    except Exception as e:
        return ApiResponse.error(message=f"图片删除失败: {str(e)}")


@router.get("/{image_id}/url", response_model=ApiResponse[dict])
async def get_image_url(image_id: int, thumbnail: bool = False, db: Session = Depends(get_db)):
    """获取图片URL"""
    try:
        image = db.query(Image).filter(Image.id == image_id).first()
        if not image:
            return ApiResponse.not_found(message="图片不存在")

        storage_service = get_storage_service()
        file_path = image.thumbnail_path if thumbnail and image.thumbnail_path else image.file_path
        url = await storage_service.get_file_url(file_path)

        if not url:
            return ApiResponse.error(message="生成文件URL失败")

        return ApiResponse.success(data={"url": url}, message="获取图片URL成功")
    except Exception as e:
        return ApiResponse.error(message=f"获取图片URL失败: {str(e)}")
