from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.crud.annotation_group import crud_annotation_group
from app.crud.project import crud_project
from app.schemas.annotation_group import (
    AnnotationGroupCreate,
    AnnotationGroupUpdate,
    AnnotationGroupListResponse,
    AnnotationGroupDetail
)
from app.core.exceptions import NotFoundException, AlreadyExistsException


class AnnotationGroupService:
    """标注组业务逻辑服务"""

    async def get_annotation_groups(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        project_id: Optional[int] = None
    ) -> AnnotationGroupListResponse:
        """
        获取标注组列表

        Args:
            db:  数据库会话
            skip: 跳过记录数
            limit: 返回记录数
            project_id: 项目ID过滤

        Returns:
            标注组列表响应
        """
        if project_id:
            groups = await crud_annotation_group.get_multi_by_project(
                db,
                project_id=project_id,
                skip=skip,
                limit=limit
            )
            total = await crud_annotation_group.get_count(
                db,
                filters={"project_id": project_id}
            )
        else:
            groups = await crud_annotation_group.get_multi(db, skip=skip, limit=limit)
            total = await crud_annotation_group.get_count(db)

        return AnnotationGroupListResponse(
            total=total,
            items=groups,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit
        )

    async def get_annotation_group_detail(
        self,
        db: AsyncSession,
        group_id: int
    ) -> AnnotationGroupDetail:
        """
        获取标注组详情

        Args:
            db: 数据库会话
            group_id: 标注组ID

        Returns:
            标注组详情

        Raises:
            NotFoundException: 标注组不存在
        """
        group = await crud_annotation_group.get(db, id=group_id)
        if not group:
            raise NotFoundException(f"AnnotationGroup with id {group_id} not found")

        # 统计标注文件数量
        file_count = await crud_annotation_group.get_annotation_file_count(
            db,
            group_id=group_id
        )

        return AnnotationGroupDetail(
            **group.__dict__,
            annotation_file_count=file_count
        )

    async def create_annotation_group(
        self,
        db: AsyncSession,
        group_in: AnnotationGroupCreate,
        created_by: int
    ) -> dict:
        """
        创建标注组

        Args:
            db: 数据库会话
            group_in: 创建标注组数据
            created_by: 创建人ID

        Returns:
            创建的标注组

        Raises:
            NotFoundException:  项目不存在
            AlreadyExistsException:  标注组名称已存在
        """
        # 检查项目是否存在
        project = await crud_project.get(db, id=group_in.project_id)
        if not project:
            raise NotFoundException(
                f"Project with id {group_in.project_id} not found"
            )

        # 检查标注组名称在项目中是否已存在
        existing_group = await crud_annotation_group.get_by_name_and_project(
            db,
            name=group_in.name,
            project_id=group_in.project_id
        )
        if existing_group:
            raise AlreadyExistsException(
                f"AnnotationGroup with name '{group_in.name}' already exists in project"
            )

        # 创建标注组
        group = await crud_annotation_group.create(
            db,
            obj_in=group_in,
            created_by=created_by
        )
        return group

    async def update_annotation_group(
        self,
        db: AsyncSession,
        group_id: int,
        group_in: AnnotationGroupUpdate,
        updated_by: int
    ) -> dict:
        """
        更新标注组

        Args:
            db: 数据库会话
            group_id: 标注组ID
            group_in: 更新数据
            updated_by: 更新人ID

        Returns:
            更新后的标注组

        Raises:
            NotFoundException: 标注组不存在
            AlreadyExistsException: 标注组名称已存在
        """
        # 获取标注组
        group = await crud_annotation_group.get(db, id=group_id)
        if not group:
            raise NotFoundException(f"AnnotationGroup with id {group_id} not found")

        # 如果更新名称，检查新名称在项目中是否已被使用
        if group_in.name and group_in.name != group.name:
            existing_group = await crud_annotation_group.get_by_name_and_project(
                db,
                name=group_in.name,
                project_id=group.project_id
            )
            if existing_group:
                raise AlreadyExistsException(
                    f"AnnotationGroup with name '{group_in.name}' already exists in project"
                )

        # 更新标注组
        group = await crud_annotation_group.update(
            db,
            db_obj=group,
            obj_in=group_in,
            updated_by=updated_by
        )
        return group

    async def delete_annotation_group(
        self,
        db: AsyncSession,
        group_id: int
    ) -> None:
        """
        删除标注组

        Args:
            db:  数据库会话
            group_id: 标注组ID

        Raises:
            NotFoundException: 标注组不存在
        """
        group = await crud_annotation_group.get(db, id=group_id)
        if not group:
            raise NotFoundException(f"AnnotationGroup with id {group_id} not found")

        await crud_annotation_group.delete(db, id=group_id)


# 创建服务实例
annotation_group_service = AnnotationGroupService()