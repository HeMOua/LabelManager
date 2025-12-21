from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.crud.label import crud_label
from app.crud.project import crud_project
from app.schemas.label import (
    LabelCreate,
    LabelUpdate,
    LabelListResponse,
    LabelDetail
)
from app.core.exceptions import NotFoundException, AlreadyExistsException


class LabelService:
    """标签业务逻辑服务"""

    async def get_labels(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        project_id: Optional[int] = None,
        category: Optional[str] = None
    ) -> LabelListResponse:
        """
        获取标签列表

        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 返回记录数
            project_id: 项目ID过滤
            category:  分类过滤

        Returns:
            标签列表响应
        """
        if project_id:
            labels = await crud_label.get_multi_by_project(
                db,
                project_id=project_id,
                skip=skip,
                limit=limit,
                category=category
            )
            filters = {"project_id": project_id}
            if category:
                filters["category"] = category
            total = await crud_label.get_count(db, filters=filters)
        else:
            filters = {}
            if category:
                filters["category"] = category
            labels = await crud_label.get_multi(db, skip=skip, limit=limit, filters=filters)
            total = await crud_label.get_count(db, filters=filters)

        return LabelListResponse(
            total=total,
            items=labels,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit
        )

    async def get_label_detail(
        self,
        db: AsyncSession,
        label_id: int
    ) -> LabelDetail:
        """
        获取标签详情

        Args:
            db:  数据库会话
            label_id: 标签ID

        Returns:
            标签详情

        Raises:
            NotFoundException: 标签不存在
        """
        label = await crud_label.get(db, id=label_id)
        if not label:
            raise NotFoundException(f"Label with id {label_id} not found")

        # 统计使用次数
        image_count = await crud_label.get_label_usage_count(db, label_id=label_id)

        return LabelDetail(
            **label.__dict__,
            image_count=image_count
        )

    async def create_label(
        self,
        db: AsyncSession,
        label_in: LabelCreate,
        created_by: int
    ) -> dict:
        """
        创建标签

        Args:
            db: 数据库会话
            label_in:  创建标签数据
            created_by: 创建人ID

        Returns:
            创建的标签

        Raises:
            NotFoundException: 项目不存在
            AlreadyExistsException: 标签名称已存在
        """
        # 检查项目是否存在
        project = await crud_project.get(db, id=label_in.project_id)
        if not project:
            raise NotFoundException(
                f"Project with id {label_in.project_id} not found"
            )

        # 检查标签名称在项目中是否已存在
        existing_label = await crud_label.get_by_name_and_project(
            db,
            name=label_in.name,
            project_id=label_in.project_id
        )
        if existing_label:
            raise AlreadyExistsException(
                f"Label with name '{label_in.name}' already exists in project {label_in.project_id}"
            )

        # 创建标签
        label = await crud_label.create(
            db,
            obj_in=label_in,
            created_by=created_by
        )
        return label

    async def update_label(
        self,
        db: AsyncSession,
        label_id: int,
        label_in: LabelUpdate,
        updated_by: int
    ) -> dict:
        """
        更新标签

        Args:
            db: 数据库会话
            label_id: 标签ID
            label_in: 更新数据
            updated_by: 更新人ID

        Returns:
            更新后的标签

        Raises:
            NotFoundException: 标签不存在
            AlreadyExistsException: 标签名称已存在
        """
        # 获取标签
        label = await crud_label.get(db, id=label_id)
        if not label:
            raise NotFoundException(f"Label with id {label_id} not found")

        # 如果更新名称，检查新名称在项目中是否已被使用
        if label_in.name and label_in.name != label.name:
            existing_label = await crud_label.get_by_name_and_project(
                db,
                name=label_in.name,
                project_id=label.project_id
            )
            if existing_label:
                raise AlreadyExistsException(
                    f"Label with name '{label_in.name}' already exists in project"
                )

        # 更新标签
        label = await crud_label.update(
            db,
            db_obj=label,
            obj_in=label_in,
            updated_by=updated_by
        )
        return label

    async def delete_label(
        self,
        db: AsyncSession,
        label_id: int
    ) -> None:
        """
        删除标签

        Args:
            db: 数据库会话
            label_id:  标签ID

        Raises:
            NotFoundException:  标签不存在
        """
        label = await crud_label.get(db, id=label_id)
        if not label:
            raise NotFoundException(f"Label with id {label_id} not found")

        await crud_label.delete(db, id=label_id)


# 创建服务实例
label_service = LabelService()