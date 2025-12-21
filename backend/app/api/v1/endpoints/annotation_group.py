from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_async_db
from app.schemas.annotation_group import (
    AnnotationGroup,
    AnnotationGroupCreate,
    AnnotationGroupUpdate,
    AnnotationGroupDetail,
    AnnotationGroupListResponse
)
from app.services.annotation_group import annotation_group_service
from app.api. deps import get_current_user_id

router = APIRouter()


@router.get(
    "/",
    response_model=AnnotationGroupListResponse,
    summary="获取标注组列表",
    description="获取标注组列表，支持分页和项目过滤"
)
async def list_annotation_groups(
    db: AsyncSession = Depends(get_async_db),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    project_id: Optional[int] = Query(None, description="项目ID过滤"),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取标注组列表"""
    return await annotation_group_service.get_annotation_groups(
        db=db,
        skip=skip,
        limit=limit,
        project_id=project_id
    )


@router.get(
    "/{group_id}",
    response_model=AnnotationGroupDetail,
    summary="获取标注组详情",
    description="根据标注组ID获取标注组详细信息及统计数据"
)
async def get_annotation_group(
    group_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取标注组详情"""
    return await annotation_group_service.get_annotation_group_detail(
        db=db,
        group_id=group_id
    )


@router.post(
    "/",
    response_model=AnnotationGroup,
    status_code=status. HTTP_201_CREATED,
    summary="创建标注组",
    description="创建新标注组"
)
async def create_annotation_group(
    group_in: AnnotationGroupCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """创建标注组"""
    return await annotation_group_service.create_annotation_group(
        db=db,
        group_in=group_in,
        created_by=current_user_id
    )


@router.put(
    "/{group_id}",
    response_model=AnnotationGroup,
    summary="更新标注组",
    description="更新标注组信息"
)
async def update_annotation_group(
    group_id: int,
    group_in: AnnotationGroupUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user_id:  int = Depends(get_current_user_id)
):
    """更新标注组"""
    return await annotation_group_service.update_annotation_group(
        db=db,
        group_id=group_id,
        group_in=group_in,
        updated_by=current_user_id
    )


@router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除标注组",
    description="删除标注组及其所有标注文件"
)
async def delete_annotation_group(
    group_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """删除标注组"""
    await annotation_group_service.delete_annotation_group(db=db, group_id=group_id)