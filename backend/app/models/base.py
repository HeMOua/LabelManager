from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class BaseModel(Base):
    """
    基础模型类
    所有模型都应继承此类
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    created_by = Column(Integer, comment="创建人ID")
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    updated_by = Column(Integer, comment="更新人ID")
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        comment="更新时间"
    )
    remark = Column(Text, comment="备注")
