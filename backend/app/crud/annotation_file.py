from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.crud.base import CRUDBase
from app.models.annotation_file import AnnotationFile
from app.schemas.annotation_file import AnnotationFileCreate, AnnotationFileUpdate


class CRUDAnnotationFile(CRUDBase[AnnotationFile, AnnotationFileCreate, AnnotationFileUpdate]):
    """标注文件 CRUD"""

    async def get_multi_by_group(
        self,
        db: AsyncSession,
        *,
        annotation_group_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[AnnotationFile]:
        """根据标注组获取标注文件列表"""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"annotation_group_id": annotation_group_id}
        )

    async def get_multi_by_image(
        self,
        db: AsyncSession,
        *,
        image_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[AnnotationFile]:
        """根据图片获取标注文件列表"""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"image_id": image_id}
        )

    async def get_by_group_and_image(
        self,
        db: AsyncSession,
        *,
        annotation_group_id: int,
        image_id: int
    ) -> Optional[AnnotationFile]:
        """根据标注组和图片获取最新版本的标注文件"""
        result = await db.execute(
            select(self.model)
            .filter(
                and_(
                    self.model.annotation_group_id == annotation_group_id,
                    self.model.image_id == image_id
                )
            )
            .order_by(self.model.version.desc())
        )
        return result.scalars().first()

    async def get_latest_version(
        self,
        db: AsyncSession,
        *,
        annotation_group_id: int,
        image_id: int
    ) -> int:
        """获取特定图片在标注组中的最新版本号"""
        annotation = await self.get_by_group_and_image(
            db,
            annotation_group_id=annotation_group_id,
            image_id=image_id
        )
        return annotation.version if annotation else 0

    async def create_new_version(
        self,
        db: AsyncSession,
        *,
        obj_in: AnnotationFileCreate,
        created_by: Optional[int] = None
    ) -> AnnotationFile:
        """创建新版本的标注文件"""
        # 获取最新版本号
        latest_version = await self.get_latest_version(
            db,
            annotation_group_id=obj_in.annotation_group_id,
            image_id=obj_in.image_id
        )

        # 创建新版本
        obj_in.version = latest_version + 1
        return await self.create(db, obj_in=obj_in, created_by=created_by)


crud_annotation_file = CRUDAnnotationFile(AnnotationFile)