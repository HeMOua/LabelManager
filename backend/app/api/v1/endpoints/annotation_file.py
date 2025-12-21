from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_async_db
from app.schemas.annotation_file import (
    AnnotationFile,
    AnnotationFileCreate,
    AnnotationFileUpdate,
    AnnotationFileDetail,
    AnnotationFileListResponse
)
from app.services.annotation_file import annotation_file_service
from app.api. deps import get_current_user_id

router = APIRouter()


@router.get(
    "/",
    response_model=AnnotationFileListResponse,
    summary="获取标注文件列表",
    description="获取标注文件列表，支持分页、标注组和图片过滤"
)
async def list_annotation_files(
    db:  AsyncSession = Depends(get_async_db),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    annotation_group_id: Optional[int] = Query(None, description="标注组ID过滤"),
    image_id: Optional[int] = Query(None, description="图片ID过滤"),
    current_user_id:  int = Depends(get_current_user_id)
):
    """获取标注文件列表"""
    return await annotation_file_service.get_annotation_files(
        db=db,
        skip=skip,
        limit=limit,
        annotation_group_id=annotation_group_id,
        image_id=image_id
    )


@router.get(
    "/{file_id}",
    response_model=AnnotationFileDetail,
    summary="获取标注文件详情",
    description="根据标注文件ID获取标注文件详细信息"
)
async def get_annotation_file(
    file_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user_id:  int = Depends(get_current_user_id)
):
    """获取标注文件详情"""
    return await annotation_file_service.get_annotation_file_detail(
        db=db,
        file_id=file_id
    )


@router.post(
    "/",
    response_model=AnnotationFile,
    status_code=status.HTTP_201_CREATED,
    summary="创建标注文件",
    description="创建新标注文件，支持自动版本管理"
)
async def create_annotation_file(
    file_in: AnnotationFileCreate,
    auto_version: bool = Query(True, description="是否自动生成版本号"),
    db: AsyncSession = Depends(get_async_db),
    current_user_id:  int = Depends(get_current_user_id)
):
    """创建标注文件"""
    return await annotation_file_service.create_annotation_file(
        db=db,
        file_in=file_in,
        created_by=current_user_id,
        auto_version=auto_version
    )


@router.put(
    "/{file_id}",
    response_model=AnnotationFile,
    summary="更新标注文件",
    description="更新标注文件信息"
)
async def update_annotation_file(
    file_id: int,
    file_in: AnnotationFileUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """更新标注文件"""
    return await annotation_file_service.update_annotation_file(
        db=db,
        file_id=file_id,
        file_in=file_in,
        updated_by=current_user_id
    )


@router.delete(
    "/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除标注文件",
    description="删除标注文件"
)
async def delete_annotation_file(
    file_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """删除标注文件"""
    await annotation_file_service.delete_annotation_file(db=db, file_id=file_id)


@router.get(
    "/latest",
    response_model=AnnotationFile,
    summary="获取最新标注",
    description="获取特定图片在标注组中的最新版本标注"
)
async def get_latest_annotation(
    annotation_group_id: int = Query(... , description="标注组ID"),
    image_id: int = Query(..., description="图片ID"),
    db: AsyncSession = Depends(get_async_db),
    current_user_id:  int = Depends(get_current_user_id)
):
    """获取最新标注"""
    file = await annotation_file_service. get_latest_annotation(
        db=db,
        annotation_group_id=annotation_group_id,
        image_id=image_id
    )
    if not file:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("No annotation found for this image in the group")
    return file