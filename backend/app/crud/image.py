from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.image import Image, image_label_association
from app.models.label import Label
from app.models.annotation_file import AnnotationFile
from app.schemas.image import ImageCreate, ImageUpdate


class CRUDImage(CRUDBase[Image, ImageCreate, ImageUpdate]):
    """图片 CRUD"""

    async def get_with_labels(
        self, db: AsyncSession, id: int
    ) -> Optional[Image]:
        """获取图片及其标签"""
        result = await db.execute(
            select(self.model)
            .options(selectinload(self.model.labels))
            .filter(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_multi_by_project(
        self,
        db: AsyncSession,
        *,
        project_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Image]:
        """根据项目获取图片列表"""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"project_id": project_id}
        )

    async def add_labels(
        self,
        db: AsyncSession,
        *,
        image_id: int,
        label_ids: List[int]
    ) -> Image:
        """为图片添加标签"""
        image = await self.get(db, id=image_id)
        if not image:
            return None

        # 获取标签对象
        result = await db.execute(
            select(Label).filter(Label.id.in_(label_ids))
        )
        labels = result.scalars().all()

        # 添加标签（自动去重）
        for label in labels:
            if label not in image.labels:
                image.labels.append(label)

        await db.commit()
        await db.refresh(image)
        return image

    async def remove_labels(
        self,
        db: AsyncSession,
        *,
        image_id: int,
        label_ids: List[int]
    ) -> Image:
        """移除图片的标签"""
        image = await self.get_with_labels(db, id=image_id)
        if not image:
            return None

        # 移除指定标签
        image.labels = [
            label for label in image.labels
            if label.id not in label_ids
        ]

        await db.commit()
        await db.refresh(image)
        return image

    async def get_images_by_label(
        self,
        db: AsyncSession,
        *,
        label_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Image]:
        """根据标签获取图片列表"""
        result = await db.execute(
            select(Image)
            .join(image_label_association)
            .filter(image_label_association.c.label_id == label_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


crud_image = CRUDImage(Image)