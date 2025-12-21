from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.project import Project
from app.models.image import Image
from app.models.label import Label
from app.models.annotation_group import AnnotationGroup
from app.schemas.project import ProjectCreate, ProjectUpdate


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    """项目 CRUD"""

    async def get_with_stats(
        self, db: AsyncSession, id: int
    ) -> Optional[dict]:
        """获取项目及其统计信息"""
        project = await self.get(db, id=id)
        if not project:
            return None

        # 统计图片数量
        image_count_result = await db.execute(
            select(func.count(Image.id)).filter(Image.project_id == id)
        )
        image_count = image_count_result.scalar()

        # 统计标签数量
        label_count_result = await db.execute(
            select(func.count(Label.id)).filter(Label.project_id == id)
        )
        label_count = label_count_result.scalar()

        # 统计标注组数量
        group_count_result = await db.execute(
            select(func.count(AnnotationGroup.id)).filter(
                AnnotationGroup.project_id == id
            )
        )
        group_count = group_count_result.scalar()

        return {
            **project.__dict__,
            "image_count": image_count,
            "label_count": label_count,
            "annotation_group_count": group_count
        }

    async def get_by_name(
        self, db: AsyncSession, name: str
    ) -> Optional[Project]:
        """根据名称获取项目"""
        result = await db.execute(
            select(self.model).filter(self.model.name == name)
        )
        return result.scalar_one_or_none()


crud_project = CRUDProject(Project)