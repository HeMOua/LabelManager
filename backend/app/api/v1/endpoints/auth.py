from fastapi import APIRouter, Depends, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.core.database import get_async_db
from app.schemas.auth import LoginParams, LoginResult, RefreshTokenResult
from app.schemas.user import UserInfo
from app.schemas.base import MessageResponse
from app.services.auth import auth_service
from app.api.deps import get_current_user_id

router = APIRouter()


@router.post(
    "/login",
    response_model=LoginResult,
    summary="用户登录",
    description="用户登录接口，返回访问令牌"
)
async def login(
    login_params: LoginParams,
    response: Response,
    db: AsyncSession = Depends(get_async_db)
):
    """
    用户登录

    - **username**: 用户名
    - **password**: 密码
    - **captcha**: 是否需要验证码（可选）
    """
    result = await auth_service.login(db=db, login_params=login_params)

    # 可选：将refresh token设置到httpOnly cookie中
    # response.set_cookie(
    #     key="refresh_token",
    #     value=refresh_token,
    #     httponly=True,
    #     max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    #     samesite="lax"
    # )

    return result


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="用户登出",
    description="用户登出接口"
)
async def logout(
    response: Response,
    current_user_id: int = Depends(get_current_user_id)
):
    """
    用户登出

    前端需要清除本地存储的token
    """
    await auth_service.logout()

    # 清除cookie中的refresh token
    response.delete_cookie(key="refresh_token")

    return MessageResponse(message="登出成功")


@router.post(
    "/refresh",
    response_model=RefreshTokenResult,
    summary="刷新访问令牌",
    description="使用refresh token刷新访问令牌"
)
async def refresh_token(
    refresh_token: Optional[str] = Cookie(None, alias="refresh_token")
):
    """
    刷新访问令牌

    从cookie中读取refresh_token并返回新的access_token
    """
    if not refresh_token:
        from app.core.exceptions import UnauthorizedException
        raise UnauthorizedException("缺少刷新令牌")

    return await auth_service.refresh_token(refresh_token=refresh_token)


@router.get(
    "/codes",
    response_model=List[str],
    summary="获取用户权限码",
    description="获取当前用户的所有权限码"
)
async def get_access_codes(
    db: AsyncSession = Depends(get_async_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    获取用户权限码

    返回当前用户拥有的所有权限码列表
    """
    return await auth_service.get_access_codes(db=db, user_id=current_user_id)