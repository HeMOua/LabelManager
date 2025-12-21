from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from fastapi import HTTPException, status

from app.crud.user import crud_user
from app.schemas.user import UserCreate, UserUpdate, User, UserListResponse
from app.core.exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
    InsufficientPermissionsException
)


class UserService:
    """用户业务逻辑服务"""
    
    async def get_user(self, db: AsyncSession, user_id: int) -> User:
        """
        获取用户信息
        
        Args: 
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            用户信息
            
        Raises:
            UserNotFoundException: 用户不存在
        """
        user = await crud_user.async_get(db, id=user_id)
        if not user:
            raise UserNotFoundException(f"User with id {user_id} not found")
        return user
    
    async def get_users(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> UserListResponse:
        """
        获取用户列表
        
        Args:
            db:  数据库会话
            skip: 跳过记录数
            limit: 返回记录数
            is_active: 是否激活过滤
            
        Returns: 
            用户列表响应
        """
        users = await crud_user.async_get_multi(
            db, skip=skip, limit=limit, is_active=is_active
        )
        total = await crud_user.async_get_count(db, is_active=is_active)
        
        return UserListResponse(
            total=total,
            items=users,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit
        )
    
    async def create_user(
        self, db: AsyncSession, user_in: UserCreate
    ) -> User:
        """
        创建用户
        
        Args:
            db: 数据库会话
            user_in: 创建用户数据
            
        Returns: 
            创建的用户
            
        Raises:
            UserAlreadyExistsException:  用户已存在
        """
        # 检查邮箱是否已存在
        existing_user = await crud_user. async_get_by_email(db, email=user_in.email)
        if existing_user: 
            raise UserAlreadyExistsException(
                f"User with email {user_in. email} already exists"
            )
        
        # 检查用户名是否已存在
        existing_user = await crud_user.async_get_by_username(
            db, username=user_in.username
        )
        if existing_user:
            raise UserAlreadyExistsException(
                f"User with username {user_in.username} already exists"
            )
        
        # 创建用户
        user = await crud_user.async_create(db, obj_in=user_in)
        return user
    
    async def update_user(
        self,
        db: AsyncSession,
        user_id: int,
        user_in: UserUpdate,
        current_user_id: int,
        is_superuser: bool = False
    ) -> User:
        """
        更新用户
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            user_in: 更新数据
            current_user_id: 当前操作用户ID
            is_superuser: 是否超级用户
            
        Returns:
            更新后的用户
            
        Raises:
            UserNotFoundException: 用户不存在
            InsufficientPermissionsException: 权限不足
        """
        # 获取用户
        user = await crud_user.async_get(db, id=user_id)
        if not user:
            raise UserNotFoundException(f"User with id {user_id} not found")
        
        # 权限检查：只能修改自己或超级用户可以修改所有人
        if user_id != current_user_id and not is_superuser:
            raise InsufficientPermissionsException(
                "You don't have permission to update this user"
            )
        
        # 如果更新邮箱，检查新邮箱是否已被使用
        if user_in. email and user_in.email != user.email:
            existing_user = await crud_user.async_get_by_email(db, email=user_in.email)
            if existing_user: 
                raise UserAlreadyExistsException(
                    f"Email {user_in.email} is already in use"
                )
        
        # 如果更新用户名，检查新用户名是否已被使用
        if user_in.username and user_in. username != user.username:
            existing_user = await crud_user.async_get_by_username(
                db, username=user_in.username
            )
            if existing_user:
                raise UserAlreadyExistsException(
                    f"Username {user_in.username} is already in use"
                )
        
        # 更新用户
        user = await crud_user. async_update(db, db_obj=user, obj_in=user_in)
        return user
    
    async def delete_user(
        self,
        db: AsyncSession,
        user_id:  int,
        current_user_id: int,
        is_superuser: bool = False
    ) -> User:
        """
        删除用户
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            current_user_id: 当前操作用户ID
            is_superuser: 是否超级用户
            
        Returns:
            被删除的用户
            
        Raises:
            UserNotFoundException: 用户不存在
            InsufficientPermissionsException:  权限不足
        """
        # 获取用户
        user = await crud_user.async_get(db, id=user_id)
        if not user:
            raise UserNotFoundException(f"User with id {user_id} not found")
        
        # 权限检查：只有超级用户可以删除用户
        if not is_superuser: 
            raise InsufficientPermissionsException(
                "Only superusers can delete users"
            )
        
        # 删除用户
        user = await crud_user.async_delete(db, id=user_id)
        return user


# 创建服务实例
user_service = UserService()