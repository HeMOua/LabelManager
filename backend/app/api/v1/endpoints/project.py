from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_async_db
from app.schemas.project import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectDetail,
    ProjectListResponse
)
from app.services.project import project_service
from app.api.deps import get_current_user_id

router = APIRouter()


@router.get(
    "/",
    response_model=ProjectListResponse,
    summary="获取项目列表",
    description="获取项目列表，支持分页"
)
async def list_projects(
    db: AsyncSession = Depends(get_async_db),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取项目列表"""
    return await project_service.get_projects(db=db, skip=skip, limit=limit)


@router.get(
    "/{project_id}",
    response_model=ProjectDetail,
    summary="获取项目详情",
    description="根据项目ID获取项目详细信息及统计数据"
)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user_id:  int = Depends(get_current_user_id)
):
    """获取项目详情"""
    return await project_service.get_project_detail(db=db, project_id=project_id)


@router.post(
    "/",
    response_model=Project,
    status_code=status.HTTP_201_CREATED,
    summary="创建项目",
    description="创建新项目"
)
async def create_project(
    project_in: ProjectCreate,
    db:  AsyncSession = Depends(get_async_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """创建项目"""
    return await project_service.create_project(
        db=db,
        project_in=project_in,
        created_by=current_user_id
    )


@router.put(
    "/{project_id}",
    response_model=Project,
    summary="更新项目",
    description="更新项目信息"
)
async def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user_id:  int = Depends(get_current_user_id)
):
    """更新项目"""
    return await project_service.update_project(
        db=db,
        project_id=project_id,
        project_in=project_in,
        updated_by=current_user_id
    )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除项目",
    description="删除项目及其所有关联数据"
)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """删除项目"""
    await project_service.delete_project(db=db, project_id=project_id)