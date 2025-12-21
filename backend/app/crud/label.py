from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.label import Label
from app.models.image import image_label_association
from app.schemas.label import LabelCreate, LabelUpdate


class CRUDLabel(CRUDBase[Label, LabelCreate, LabelUpdate]):
    """标签 CRUD"""

    async def get_multi_by_project(
        self,
        db: AsyncSession,
        *,
        project_id: int,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None
    ) -> List[Label]:
        """根据项目获取标签列表"""
        filters = {"project_id": project_id}
        if category:
            filters["category"] = category

        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters
        )

    async def get_by_name_and_project(
        self,
        db: AsyncSession,
        *,
        name: str,
        project_id: int
    ) -> Optional[Label]:
        """根据名称和项目获取标签"""
        result = await db.execute(
            select(self.model).filter(
                self.model.name == name,
                self.model.project_id == project_id
            )
        )
        return result.scalar_one_or_none()

    async def get_label_usage_count(
        self, db: AsyncSession, label_id: int
    ) -> int:
        """获取标签的使用次数"""
        result = await db.execute(
            select(func.count(image_label_association.c.image_id)).filter(
                image_label_association.c.label_id == label_id
            )
        )
        return result.scalar()


crud_label = CRUDLabel(Label)