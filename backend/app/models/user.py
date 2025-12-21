from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    """用户模型"""

    __tablename__ = "users"

    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码")
    real_name = Column(String(100), comment="真实姓名")
    avatar = Column(String(500), comment="头像URL")
    email = Column(String(255), unique=True, index=True, comment="邮箱")
    phone = Column(String(20), comment="手机号")
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_superuser = Column(Boolean, default=False, comment="是否超级管理员")
    home_path = Column(String(255), default="/dashboard", comment="首页路径")
    desc = Column(String(500), comment="用户描述")

    roles = relationship(
        "Role",
        secondary="user_role_association",
        back_populates="users"
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, real_name={self.real_name})>"