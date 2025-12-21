from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """用户 CRUD"""

    async def get_by_username(
        self, db: AsyncSession, username: str
    ) -> Optional[User]:
        """根据用户名获取用户"""
        result = await db.execute(
            select(self.model).filter(self.model.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_email(
        self, db: AsyncSession, email: str
    ) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await db.execute(
            select(self.model).filter(self.model.email == email)
        )
        return result.scalar_one_or_none()

    async def get_with_roles(
        self, db: AsyncSession, user_id: int
    ) -> Optional[User]:
        """获取用户及其角色"""
        result = await db.execute(
            select(self.model)
            .options(selectinload(self.model.roles))
            .filter(self.model.id == user_id)
        )
        return result.scalar_one_or_none()

    async def authenticate(
        self, db: AsyncSession, username: str, password: str
    ) -> Optional[User]:
        """
        用户认证

        Args:
            db: 数据库会话
            username: 用户名
            password: 密码

        Returns:
            认证成功返回用户对象，否则返回 None
        """
        user = await self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        if not user.is_active:
            return None
        return user

    async def create_with_password(
        self,
        db: AsyncSession,
        *,
        obj_in: UserCreate,
        created_by: Optional[int] = None
    ) -> User:
        """创建用户并加密密码"""
        # 加密密码
        hashed_password = get_password_hash(obj_in.password)

        # 创建用户对象
        db_obj = self.model(
            username=obj_in.username,
            password=hashed_password,
            real_name=obj_in.real_name,
            avatar=obj_in.avatar,
            email=obj_in.email,
            phone=obj_in.phone,
            home_path=obj_in.home_path or "/dashboard",
            desc=obj_in.desc,
            created_by=created_by
        )

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_user_permissions(
        self, db: AsyncSession, user_id: int
    ) -> List[str]:
        """
        获取用户的所有权限码

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            权限码列表
        """
        # 获取用户及其角色和权限
        result = await db.execute(
            select(self.model)
            .options(
                selectinload(self.model.roles).selectinload(Role.permissions)
            )
            .filter(self.model.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return []

        # 收集所有权限码
        permission_codes = set()
        for role in user.roles:
            for permission in role.permissions:
                permission_codes.add(permission.code)

        return list(permission_codes)


crud_user = CRUDUser(User)