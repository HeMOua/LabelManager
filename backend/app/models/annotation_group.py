from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class AnnotationGroup(BaseModel):
    """标注组模型"""

    __tablename__ = "annotation_groups"

    project_id = Column(
        Integer,
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="项目ID"
    )
    name = Column(String(100), nullable=False, index=True, comment="标注组名称")
    description = Column(Text, comment="标注组描述")

    # 关系
    project = relationship("Project", back_populates="annotation_groups")
    annotation_files = relationship(
        "AnnotationFile",
        back_populates="annotation_group",
        cascade="all, delete-orphan"
    )
