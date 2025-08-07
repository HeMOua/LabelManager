from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="active", index=True)  # 状态字段
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    images = relationship("Image", back_populates="project", cascade="all, delete-orphan")
    project_tags = relationship("Tag", back_populates="project", cascade="all, delete-orphan")
