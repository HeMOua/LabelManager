from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Project(BaseModel):
    """项目模型"""

    __tablename__ = "projects"

    name = Column(String(100), nullable=False, index=True, comment="项目名称")
    description = Column(Text, comment="项目描述")

    # 关系
    images = relationship("Image", back_populates="project", cascade="all, delete-orphan")
    labels = relationship("Label", back_populates="project", cascade="all, delete-orphan")
    annotation_groups = relationship(
        "AnnotationGroup",
        back_populates="project",
        cascade="all, delete-orphan"
    )