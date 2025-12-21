from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models.base import BaseModel as DBBaseModel

ModelType = TypeVar("ModelType", bound=DBBaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """CRUD 基类"""

    def __init__(self, model: Type[ModelType]):
        """
        初始化 CRUD 对象

        Args:
            model: SQLAlchemy 模型类
        """
        self.model = model

    # ==================== 异步方法 ====================

    async def get(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """根据 ID 获取记录"""
        result = await db.execute(
            select(self.model).filter(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """获取记录列表"""
        query = select(self.model)

        # 应用过滤条件
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    query = query.filter(getattr(self.model, key) == value)

        query = query.offset(skip).limit(limit).order_by(self.model.id.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_count(
        self,
        db: AsyncSession,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """获取记录总数"""
        query = select(func.count(self.model.id))

        # 应用过滤条件
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    query = query.filter(getattr(self.model, key) == value)

        result = await db.execute(query)
        return result.scalar()

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: CreateSchemaType,
        created_by: Optional[int] = None
    ) -> ModelType:
        """创建记录"""
        obj_in_data = jsonable_encoder(obj_in)

        # 添加创建人信息
        if created_by is not None:
            obj_in_data["created_by"] = created_by

        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        updated_by: Optional[int] = None
    ) -> ModelType:
        """更新记录"""
        obj_data = jsonable_encoder(db_obj)

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # 添加更新人信息
        if updated_by is not None:
            update_data["updated_by"] = updated_by

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, id: int) -> ModelType:
        """删除记录"""
        obj = await self.get(db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    async def bulk_create(
        self,
        db: AsyncSession,
        *,
        objs_in: List[CreateSchemaType],
        created_by: Optional[int] = None
    ) -> List[ModelType]:
        """批量创建记录"""
        db_objs = []
        for obj_in in objs_in:
            obj_in_data = jsonable_encoder(obj_in)
            if created_by is not None:
                obj_in_data["created_by"] = created_by
            db_objs.append(self.model(**obj_in_data))

        db.add_all(db_objs)
        await db.commit()
        for db_obj in db_objs:
            await db.refresh(db_obj)
        return db_objs