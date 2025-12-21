from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.crud.user import crud_user
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException

# OAuth2 密码流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user_id(
    db: AsyncSession = Depends(get_async_db),
    token: str = Depends(oauth2_scheme)
) -> int:
    """
    获取当前用户ID（从JWT Token解析）

    Args:
        db: 数据库会话
        token: JWT 令牌

    Returns:
        当前用户ID

    Raises:
        UnauthorizedException: 无效凭证
    """
    # 解码token
    payload = decode_token(token)
    if not payload:
        raise UnauthorizedException("无效的访问令牌")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("无效的访问令牌")

    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise UnauthorizedException("无效的用户ID")

    # 验证用户是否存在且激活
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise UnauthorizedException("用户不存在")

    if not user.is_active:
        raise UnauthorizedException("用户已被禁用")

    return user_id


async def get_current_superuser_id(
    db: AsyncSession = Depends(get_async_db),
    current_user_id: int = Depends(get_current_user_id)
) -> int:
    """
    获取当前超级管理员用户ID

    Args:
        db: 数据库会话
        current_user_id: 当前用户ID

    Returns:
        当前超级管理员用户ID

    Raises:
        HTTPException: 权限不足
    """
    user = await crud_user.get(db, id=current_user_id)
    if not user or not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要超级管理员权限"
        )
    return current_user_id