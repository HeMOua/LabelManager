from fastapi import APIRouter, Depends, Query, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.core.database import get_async_db
from app.schemas.image import (
    Image,
    ImageCreate,
    ImageUpdate,
    ImageDetail,
    ImageListResponse,
    ImageLabelAssociation
)
from app.services.image import image_service
from app. api.deps import get_current_user_id

router = APIRouter()


@router.get(
    "/",
    response_model=ImageListResponse,
    summary="获取图片列表",
    description="获取图片列表，支持分页和项目过滤"
)
async def list_images(
    db: AsyncSession = Depends(get_async_db),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    project_id: Optional[int] = Query(None, description="项目ID过滤"),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取图片列表"""
    return await image_service.get_images(
        db=db,
        skip=skip,
        limit=limit,
        project_id=project_id
    )


@router.get(
    "/{image_id}",
    response_model=ImageDetail,
    summary="获取图片详情",
    description="根据图片ID获取图片详细信息及关联数据"
)
async def get_image(
    image_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user_id:  int = Depends(get_current_user_id)
):
    """获取图片详情"""
    return await image_service.get_image_detail(db=db, image_id=image_id)


@router.post(
    "/",
    response_model=Image,
    status_code=status.HTTP_201_CREATED,
    summary="创建图片",
    description="创建新图片记录"
)
async def create_image(
    image_in: ImageCreate,
    db:  AsyncSession = Depends(get_async_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """创建图片"""
    return await image_service.create_image(
        db=db,
        image_in=image_in,
        created_by=current_user_id
    )


@router.put(
    "/{image_id}",
    response_model=Image,
    summary="更新图片",
    description="更新图片信息"
)
async def update_image(
    image_id: int,
    image_in: ImageUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """更新图片"""
    return await image_service.update_image(
        db=db,
        image_id=image_id,
        image_in=image_in,
        updated_by=current_user_id
    )


@router.delete(
    "/{image_id}",
    status_code=status. HTTP_204_NO_CONTENT,
    summary="删除图片",
    description="删除图片及其所有关联数据"
)
async def delete_image(
    image_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """删除图片"""
    await image_service.delete_image(db=db, image_id=image_id)


@router.post(
    "/labels",
    response_model=ImageDetail,
    summary="为图片添加标签",
    description="为图片添加一个或多个标签"
)
async def add_labels_to_image(
    association: ImageLabelAssociation,
    db: AsyncSession = Depends(get_async_db),
    current_user_id:  int = Depends(get_current_user_id)
):
    """为图片添加标签"""
    return await image_service.add_labels_to_image(db=db, association=association)


@router.delete(
    "/{image_id}/labels",
    response_model=ImageDetail,
    summary="移除图片的标签",
    description="移除图片的一个或多个标签"
)
async def remove_labels_from_image(
    image_id: int,
    label_ids: List[int] = Body(..., description="要移除的标签ID列表"),
    db: AsyncSession = Depends(get_async_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """移除图片的标签"""
    return await image_service.remove_labels_from_image(
        db=db,
        image_id=image_id,
        label_ids=label_ids
    )


@router.get(
    "/by-label/{label_id}",
    response_model=ImageListResponse,
    summary="根据标签获取图片列表",
    description="获取包含指定标签的所有图片"
)
async def get_images_by_label(
    label_id: int,
    db: AsyncSession = Depends(get_async_db),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    current_user_id: int = Depends(get_current_user_id)
):
    """根据标签获取图片列表"""
    return await image_service.get_images_by_label(
        db=db,
        label_id=label_id,
        skip=skip,
        limit=limit
    )