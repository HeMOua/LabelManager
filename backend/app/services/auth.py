from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import timedelta

from app.crud.user import crud_user
from app.schemas.auth import LoginParams, LoginResult, RefreshTokenResult
from app.schemas.user import UserInfo
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.core.config import settings
from app.core.exceptions import UnauthorizedException, NotFoundException


class AuthService:
    """认证服务"""

    async def login(
        self,
        db: AsyncSession,
        login_params: LoginParams
    ) -> LoginResult:
        """
        用户登录

        Args:
            db: 数据库会话
            login_params: 登录参数

        Returns:
            登录结果（包含访问令牌）

        Raises:
            UnauthorizedException: 认证失败
        """
        # 验证用户名和密码
        user = await crud_user.authenticate(
            db,
            username=login_params.username,
            password=login_params.password
        )

        if not user:
            raise UnauthorizedException("用户名或密码错误")

        if not user.is_active:
            raise UnauthorizedException("用户已被禁用")

        # 创建访问令牌
        access_token = create_access_token(
            subject=user.id,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        # 创建刷新令牌（可选，用于后续刷新）
        # refresh_token = create_refresh_token(
        #     subject=user.id,
        #     expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        # )

        return LoginResult(accessToken=access_token)

    async def get_user_info(
        self,
        db: AsyncSession,
        user_id: int,
        include_token: bool = False,
        token: Optional[str] = None
    ) -> UserInfo:
        """
        获取用户信息

        Args:
            db: 数据库会话
            user_id: 用户ID
            include_token: 是否包含token
            token: 访问令牌

        Returns:
            用户信息

        Raises:
            NotFoundException: 用户不存在
        """
        # 获取用户及其角色
        user = await crud_user.get_with_roles(db, user_id=user_id)

        if not user:
            raise NotFoundException(f"用户 {user_id} 不存在")

        # 提取角色代码
        roles = [role.code for role in user.roles] if user.roles else []

        # 如果没有角色，默认给普通用户角色
        if not roles:
            roles = ["user"]

        # 构建用户信息
        user_info = UserInfo(
            userId=str(user.id),
            username=user.username,
            realName=user.real_name or user.username,
            avatar=user.avatar or f"https://api.dicebear.com/7.x/avataaars/svg?seed={user.username}",
            desc=user.desc or "暂无描述",
            homePath=user.home_path or "/dashboard",
            roles=roles,
            token=token if include_token else None
        )

        return user_info

    async def get_access_codes(
        self,
        db: AsyncSession,
        user_id: int
    ) -> List[str]:
        """
        获取用户权限码

        Args:
            db: 数据库会话
            user_id:  用户ID

        Returns:
            权限码列表
        """
        permission_codes = await crud_user.get_user_permissions(db, user_id=user_id)

        # 如果没有权限，返回基础权限
        if not permission_codes:
            permission_codes = ["basic: read"]

        return permission_codes

    async def refresh_token(
        self,
        refresh_token: str
    ) -> RefreshTokenResult:
        """
        刷新访问令牌

        Args:
            refresh_token:  刷新令牌

        Returns:
            新的访问令牌

        Raises:
            UnauthorizedException: 刷新令牌无效
        """
        # 解码刷新令牌
        payload = decode_token(refresh_token)

        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedException("无效的刷新令牌")

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("无效的刷新令牌")

        # 创建新的访问令牌
        new_access_token = create_access_token(
            subject=int(user_id),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return RefreshTokenResult(
            data=new_access_token,
            status=0
        )

    async def logout(self):
        """
        登出（前端清除token即可）

        如果需要实现token黑名单，可以在这里添加逻辑
        """
        # 这里可以添加token黑名单逻辑
        # 例如：将token加入Redis黑名单
        pass


# 创建服务实例
auth_service = AuthService()