from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_async_db
from app. schemas.label import (
    Label,
    LabelCreate,
    LabelUpdate,
    LabelDetail,
    LabelListResponse
)
from app.services.label import label_service
from app.api.deps import get_current_user_id

router = APIRouter()


@router.get(
    "/",
    response_model=LabelListResponse,
    summary="获取标签列表",
    description="获取标签列表，支持分页、项目和分类过滤"
)
async def list_labels(
    db: AsyncSession = Depends(get_async_db),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    project_id: Optional[int] = Query(None, description="项目ID过滤"),
    category: Optional[str] = Query(None, description="分类过滤"),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取标签列表"""
    return await label_service.get_labels(
        db=db,
        skip=skip,
        limit=limit,
        project_id=project_id,
        category=category
    )


@router.get(
    "/{label_id}",
    response_model=LabelDetail,
    summary="获取标签详情",
    description="根据标签ID获取标签详细信息及使用统计"
)
async def get_label(
    label_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取标签详情"""
    return await label_service.get_label_detail(db=db, label_id=label_id)


@router.post(
    "/",
    response_model=Label,
    status_code=status.HTTP_201_CREATED,
    summary="创建标签",
    description="创建新标签"
)
async def create_label(
    label_in: LabelCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """创建标签"""
    return await label_service.create_label(
        db=db,
        label_in=label_in,
        created_by=current_user_id
    )


@router.put(
    "/{label_id}",
    response_model=Label,
    summary="更新标签",
    description="更新标签信息"
)
async def update_label(
    label_id:  int,
    label_in:  LabelUpdate,
    db:  AsyncSession = Depends(get_async_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """更新标签"""
    return await label_service.update_label(
        db=db,
        label_id=label_id,
        label_in=label_in,
        updated_by=current_user_id
    )


@router.delete(
    "/{label_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除标签",
    description="删除标签及其所有关联"
)
async def delete_label(
    label_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """删除标签"""
    await label_service.delete_label(db=db, label_id=label_id)