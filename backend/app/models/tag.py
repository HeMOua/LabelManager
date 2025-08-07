from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    color = Column(String(50), nullable=False, index=True)
    category = Column(String(255), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)  # 为空表示全局标签
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    image_tags = relationship("ImageTag", back_populates="tag")
    project = relationship("Project", back_populates="project_tags")

    @property
    def is_global(self):
        """判断是否为全局标签"""
        return self.project_id is None

    @property
    def tag_type(self):
        """返回标签类型"""
        return "global" if self.is_global else "project"