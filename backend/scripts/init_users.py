"""
初始化用户脚本
创建默认管理员和测试用户
"""
import asyncio
from sqlalchemy import delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.database import AsyncSessionLocal
from app.crud.user import crud_user
from app.schemas.user import UserCreate
from app.models.role import Role, Permission, user_role_association, role_permission_association


async def clear_existing_data(db: AsyncSession):
    """初始化前清理已有数据"""
    print("⚠️ 检测到初始化前清理已有数据...")

    # 1. 清空中间表（非常重要）
    await db.execute(delete(user_role_association))
    await db.execute(delete(role_permission_association))

    # 2. 清空主表
    await db.execute(delete(User))
    await db.execute(delete(Role))
    await db.execute(delete(Permission))

    await db.commit()
    print("🧹 已清空 用户 / 角色 / 权限 相关数据")


async def init_permissions(db: AsyncSession):
    """初始化权限"""
    permissions_data = [
        {"name": "查看项目", "code": "project:read", "description": "查看项目列表和详情"},
        {"name": "创建项目", "code": "project:create", "description": "创建新项目"},
        {"name": "编辑项目", "code": "project:update", "description": "编辑项目信息"},
        {"name": "删除项目", "code": "project:delete", "description": "删除项目"},
        {"name": "查看图片", "code": "image:read", "description": "查看图片"},
        {"name": "上传图片", "code": "image:create", "description": "上传图片"},
        {"name": "编辑图片", "code": "image:update", "description": "编辑图片信息"},
        {"name": "删除图片", "code": "image:delete", "description": "删除图片"},
        {"name": "管理标签", "code": "label:manage", "description": "管理标签"},
        {"name": "管理标注", "code": "annotation:manage", "description": "管理标注"},
        {"name": "系统管理", "code": "system:admin", "description": "系统管理权限"},
    ]

    permissions = []
    for perm_data in permissions_data:
        permission = Permission(**perm_data, created_by=1)
        db.add(permission)
        permissions.append(permission)
    await db.commit()
    await db.flush()
    print(f"✅ 创建了 {len(permissions)} 个权限")
    return permissions


async def init_roles(db: AsyncSession, permissions: list):
    """初始化角色"""
    # 管理员角色 - 拥有所有权限
    admin_role = Role(
        name="管理员",
        code="admin",
        description="系统管理员，拥有所有权限",
        created_by=1
    )
    admin_role.permissions.extend(permissions)
    db.add(admin_role)

    # 普通用户角色 - 只有查看权限
    user_role = Role(
        name="普通用户",
        code="user",
        description="普通用户，只能查看",
        created_by=1
    )
    user_role.permissions.extend([p for p in permissions if ":read" in p.code])
    db.add(user_role)

    # 标注员角色 - 可以查看和标注
    annotator_role = Role(
        name="标注员",
        code="annotator",
        description="标注员，可以查看和标注",
        created_by=1
    )
    annotator_role.permissions.extend([
        p for p in permissions
        if ":read" in p.code or "annotation:manage" in p.code or "label:manage" in p.code
    ])
    db.add(annotator_role)

    await db.commit()
    await db.flush()
    print("✅ 创建了 3 个角色")
    return {"admin": admin_role, "user": user_role, "annotator": annotator_role}


async def init_users(db: AsyncSession, roles: dict):
    """初始化用户"""
    # 创建管理员用户
    admin_user = await crud_user.create_with_password(
        db,
        obj_in=UserCreate(
            username="admin",
            password="admin",
            real_name="系统管理员",
            email="admin@example.com",
            desc="系统管理员账号",
            home_path="/dashboard"
        ),
        created_by=1
    )
    admin_user.is_superuser = True

    # 创建普通用户
    test_user = await crud_user.create_with_password(
        db,
        obj_in=UserCreate(
            username="user",
            password="user123",
            real_name="测试用户",
            email="user@example.com",
            desc="普通测试用户",
            home_path="/dashboard"
        ),
        created_by=1
    )

    # 创建标注员用户
    annotator_user = await crud_user.create_with_password(
        db,
        obj_in=UserCreate(
            username="annotator",
            password="annotator123",
            real_name="标注员",
            email="annotator@example.com",
            desc="图片标注员",
            home_path="/dashboard"
        ),
        created_by=1
    )

    await db.execute(
        insert(user_role_association).values(
            user_id=admin_user.id,
            role_id=roles["admin"].id,
        )
    )

    await db.execute(
        insert(user_role_association).values(
            user_id=test_user.id,
            role_id=roles["user"].id,
        )
    )

    await db.execute(
        insert(user_role_association).values(
            user_id=annotator_user.id,
            role_id=roles["annotator"].id,
        )
    )

    await db.commit()

    print("\n✅ 创建了 3 个用户:")
    print(f"  - 管理员:  username=admin, password=admin")
    print(f"  - 普通用户: username=user, password=user123")
    print(f"  - 标注员: username=annotator, password=annotator123")


async def main():
    """主函数"""
    print("=" * 60)
    print("开始初始化用户数据")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        try:
            # 0. 初始化前清理
            await clear_existing_data(db)

            # 1. 初始化权限
            permissions = await init_permissions(db)

            # 2. 初始化角色
            roles = await init_roles(db, permissions)

            # 3. 初始化用户
            await init_users(db, roles)

            print("\n" + "=" * 60)
            print("✅ 用户数据初始化完成！")
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ 初始化失败: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())