from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.crud.image import crud_image
from app.crud.project import crud_project
from app.crud.label import crud_label
from app.schemas.image import (
    ImageCreate,
    ImageUpdate,
    ImageListResponse,
    ImageDetail,
    ImageLabelAssociation
)
from app.core.exceptions import NotFoundException, ValidationException


class ImageService:
    """图片业务逻辑服务"""

    async def get_images(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        project_id: Optional[int] = None
    ) -> ImageListResponse:
        """
        获取图片列表

        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 返回记录数
            project_id: 项目ID过滤

        Returns:
            图片列表响应
        """
        if project_id:
            images = await crud_image.get_multi_by_project(
                db,
                project_id=project_id,
                skip=skip,
                limit=limit
            )
            total = await crud_image.get_count(db, filters={"project_id": project_id})
        else:
            images = await crud_image.get_multi(db, skip=skip, limit=limit)
            total = await crud_image.get_count(db)

        return ImageListResponse(
            total=total,
            items=images,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit
        )

    async def get_image_detail(
        self,
        db: AsyncSession,
        image_id: int
    ) -> ImageDetail:
        """
        获取图片详情

        Args:
            db: 数据库会话
            image_id: 图片ID

        Returns:
            图片详情

        Raises:
            NotFoundException: 图片不存在
        """
        image = await crud_image.get_with_labels(db, id=image_id)
        if not image:
            raise NotFoundException(f"Image with id {image_id} not found")

        # 统计标注数量
        from app.crud.annotation_file import crud_annotation_file
        annotation_count = await crud_annotation_file.get_count(
            db,
            filters={"image_id": image_id}
        )

        return ImageDetail(
            **image.__dict__,
            labels=image.labels,
            annotation_count=annotation_count
        )

    async def create_image(
        self,
        db: AsyncSession,
        image_in: ImageCreate,
        created_by: int
    ) -> dict:
        """
        创建图片

        Args:
            db: 数据库会话
            image_in:  创建图片数据
            created_by: 创建人ID

        Returns:
            创建的图片

        Raises:
            NotFoundException: 项目不存在
        """
        # 检查项目是否存在
        project = await crud_project.get(db, id=image_in.project_id)
        if not project:
            raise NotFoundException(
                f"Project with id {image_in.project_id} not found"
            )

        # 创建图片
        image = await crud_image.create(
            db,
            obj_in=image_in,
            created_by=created_by
        )
        return image

    async def update_image(
        self,
        db: AsyncSession,
        image_id: int,
        image_in: ImageUpdate,
        updated_by: int
    ) -> dict:
        """
        更新图片

        Args:
            db: 数据库会话
            image_id: 图片ID
            image_in:  更新数据
            updated_by: 更新人ID

        Returns:
            更新后的图片

        Raises:
            NotFoundException: 图片不存在
        """
        # 获取图片
        image = await crud_image.get(db, id=image_id)
        if not image:
            raise NotFoundException(f"Image with id {image_id} not found")

        # 如果更新项目ID，检查新项目是否存在
        if image_in.project_id and image_in.project_id != image.project_id:
            project = await crud_project.get(db, id=image_in.project_id)
            if not project:
                raise NotFoundException(
                    f"Project with id {image_in.project_id} not found"
                )

        # 更新图片
        image = await crud_image.update(
            db,
            db_obj=image,
            obj_in=image_in,
            updated_by=updated_by
        )
        return image

    async def delete_image(
        self,
        db: AsyncSession,
        image_id: int
    ) -> None:
        """
        删除图片

        Args:
            db: 数据库会话
            image_id:  图片ID

        Raises:
            NotFoundException:  图片不存在
        """
        image = await crud_image.get(db, id=image_id)
        if not image:
            raise NotFoundException(f"Image with id {image_id} not found")

        await crud_image.delete(db, id=image_id)

    async def add_labels_to_image(
        self,
        db: AsyncSession,
        association: ImageLabelAssociation
    ) -> ImageDetail:
        """
        为图片添加标签

        Args:
            db:  数据库会话
            association: 图片标签关联数据

        Returns:
            更新后的图片详情

        Raises:
            NotFoundException: 图片或标签不存在
        """
        # 检查图片是否存在
        image = await crud_image.get(db, id=association.image_id)
        if not image:
            raise NotFoundException(
                f"Image with id {association.image_id} not found"
            )

        # 检查所有标签是否存在且属于同一项目
        for label_id in association.label_ids:
            label = await crud_label.get(db, id=label_id)
            if not label:
                raise NotFoundException(f"Label with id {label_id} not found")
            if label.project_id != image.project_id:
                raise ValidationException(
                    f"Label {label_id} does not belong to the same project as image"
                )

        # 添加标签
        updated_image = await crud_image.add_labels(
            db,
            image_id=association.image_id,
            label_ids=association.label_ids
        )

        return await self.get_image_detail(db, image_id=updated_image.id)

    async def remove_labels_from_image(
        self,
        db: AsyncSession,
        image_id: int,
        label_ids: List[int]
    ) -> ImageDetail:
        """
        移除图片的标签

        Args:
            db: 数据库会话
            image_id:  图片ID
            label_ids: 要移除的标签ID列表

        Returns:
            更新后的图片详情

        Raises:
            NotFoundException:  图片不存在
        """
        # 检查图片是否存在
        image = await crud_image.get(db, id=image_id)
        if not image:
            raise NotFoundException(f"Image with id {image_id} not found")

        # 移除标签
        updated_image = await crud_image.remove_labels(
            db,
            image_id=image_id,
            label_ids=label_ids
        )

        return await self.get_image_detail(db, image_id=updated_image.id)

    async def get_images_by_label(
        self,
        db: AsyncSession,
        label_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> ImageListResponse:
        """
        根据标签获取图片列表

        Args:
            db: 数据库会话
            label_id: 标签ID
            skip: 跳过记录数
            limit: 返回记录数

        Returns:
            图片列表响应

        Raises:
            NotFoundException: 标签不存在
        """
        # 检查标签是否存在
        label = await crud_label.get(db, id=label_id)
        if not label:
            raise NotFoundException(f"Label with id {label_id} not found")

        # 获取图片列表
        images = await crud_image.get_images_by_label(
            db,
            label_id=label_id,
            skip=skip,
            limit=limit
        )

        # 统计总数
        total = await crud_label.get_label_usage_count(db, label_id=label_id)

        return ImageListResponse(
            total=total,
            items=images,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit
        )


# 创建服务实例
image_service = ImageService()