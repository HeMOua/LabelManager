from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.annotation_group import AnnotationGroup
from app.models.annotation_file import AnnotationFile
from app.schemas.annotation_group import AnnotationGroupCreate, AnnotationGroupUpdate


class CRUDAnnotationGroup(CRUDBase[AnnotationGroup, AnnotationGroupCreate, AnnotationGroupUpdate]):
    """标注组 CRUD"""

    async def get_multi_by_project(
        self,
        db: AsyncSession,
        *,
        project_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[AnnotationGroup]:
        """根据项目获取标注组列表"""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"project_id": project_id}
        )

    async def get_by_name_and_project(
        self,
        db: AsyncSession,
        *,
        name: str,
        project_id: int
    ) -> Optional[AnnotationGroup]:
        """根据名称和项目获取标注组"""
        result = await db.execute(
            select(self.model).filter(
                self.model.name == name,
                self.model.project_id == project_id
            )
        )
        return result.scalar_one_or_none()

    async def get_annotation_file_count(
        self, db: AsyncSession, group_id: int
    ) -> int:
        """获取标注组中的文件数量"""
        result = await db.execute(
            select(func.count(AnnotationFile.id)).filter(
                AnnotationFile.annotation_group_id == group_id
            )
        )
        return result.scalar()


crud_annotation_group = CRUDAnnotationGroup(AnnotationGroup)