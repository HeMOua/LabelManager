from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.schemas.user import UserInfo
from app.services.auth import auth_service
from app.api.deps import get_current_user_id

router = APIRouter()


@router.get(
    "/info",
    response_model=UserInfo,
    summary="获取用户信息",
    description="获取当前登录用户的详细信息"
)
async def get_user_info(
    db: AsyncSession = Depends(get_async_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    获取用户信息

    返回当前登录用户的详细信息，包括：
    - 用户ID、用户名、真实姓名
    - 头像、描述
    - 首页路径
    - 角色列表
    """
    return await auth_service.get_user_info(
        db=db,
        user_id=current_user_id,
        include_token=False
    )