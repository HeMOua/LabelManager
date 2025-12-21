from sqlalchemy import Column, String, Table, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, Base

# 用户-角色关联表
user_role_association = Table(
    'user_role_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
)

# 角色-权限关联表
role_permission_association = Table(
    'role_permission_association',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True),
)


class Role(BaseModel):
    """角色模型"""

    __tablename__ = "roles"

    name = Column(String(50), unique=True, nullable=False, comment="角色名称")
    code = Column(String(50), unique=True, nullable=False, comment="角色编码")
    description = Column(String(255), comment="角色描述")

    # 关系
    users = relationship("User", secondary=user_role_association, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permission_association, back_populates="roles")

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name}, code={self.code})>"


class Permission(BaseModel):
    """权限模型"""

    __tablename__ = "permissions"

    name = Column(String(100), nullable=False, comment="权限名称")
    code = Column(String(100), unique=True, nullable=False, comment="权限编码")
    description = Column(String(255), comment="权限描述")

    roles = relationship("Role", secondary=role_permission_association, back_populates="permissions")

    def __repr__(self):
        return f"<Permission(id={self.id}, name={self.name}, code={self.code})>"