from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.crud.project import crud_project
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectListResponse,
    ProjectDetail
)
from app.core.exceptions import NotFoundException, AlreadyExistsException


class ProjectService:
    """项目业务逻辑服务"""

    async def get_projects(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20
    ) -> ProjectListResponse:
        """
        获取项目列表

        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 返回记录数

        Returns:
            项目列表响应
        """
        projects = await crud_project.get_multi(db, skip=skip, limit=limit)
        total = await crud_project.get_count(db)

        return ProjectListResponse(
            total=total,
            items=projects,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit
        )

    async def get_project_detail(
        self,
        db: AsyncSession,
        project_id: int
    ) -> ProjectDetail:
        """
        获取项目详情

        Args:
            db: 数据库会话
            project_id: 项目ID

        Returns:
            项目详情

        Raises:
            NotFoundException: 项目不存在
        """
        project_data = await crud_project.get_with_stats(db, id=project_id)
        if not project_data:
            raise NotFoundException(f"Project with id {project_id} not found")

        return ProjectDetail(**project_data)

    async def create_project(
        self,
        db: AsyncSession,
        project_in: ProjectCreate,
        created_by: int
    ) -> dict:
        """
        创建项目

        Args:
            db: 数据库会话
            project_in:  创建项目数据
            created_by: 创建人ID

        Returns:
            创建的项目

        Raises:
            AlreadyExistsException: 项目名称已存在
        """
        # 检查项目名称是否已存在
        existing_project = await crud_project.get_by_name(db, name=project_in.name)
        if existing_project:
            raise AlreadyExistsException(
                f"Project with name '{project_in.name}' already exists"
            )

        # 创建项目
        project = await crud_project.create(
            db,
            obj_in=project_in,
            created_by=created_by
        )
        return project

    async def update_project(
        self,
        db: AsyncSession,
        project_id: int,
        project_in: ProjectUpdate,
        updated_by: int
    ) -> dict:
        """
        更新项目

        Args:
            db: 数据库会话
            project_id: 项目ID
            project_in: 更新数据
            updated_by: 更新人ID

        Returns:
            更新后的项目

        Raises:
            NotFoundException: 项目不存在
            AlreadyExistsException: 项目名称已存在
        """
        # 获取项目
        project = await crud_project.get(db, id=project_id)
        if not project:
            raise NotFoundException(f"Project with id {project_id} not found")

        # 如果更新名称，检查新名称是否已被使用
        if project_in.name and project_in.name != project.name:
            existing_project = await crud_project.get_by_name(db, name=project_in.name)
            if existing_project:
                raise AlreadyExistsException(
                    f"Project with name '{project_in.name}' already exists"
                )

        # 更新项目
        project = await crud_project.update(
            db,
            db_obj=project,
            obj_in=project_in,
            updated_by=updated_by
        )
        return project

    async def delete_project(
        self,
        db: AsyncSession,
        project_id: int
    ) -> None:
        """
        删除项目

        Args:
            db: 数据库会话
            project_id:  项目ID

        Raises:
            NotFoundException:  项目不存在
        """
        project = await crud_project.get(db, id=project_id)
        if not project:
            raise NotFoundException(f"Project with id {project_id} not found")

        await crud_project.delete(db, id=project_id)


# 创建服务实例
project_service = ProjectService()