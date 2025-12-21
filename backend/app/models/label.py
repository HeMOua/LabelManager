from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.image import image_label_association


class Label(BaseModel):
    """标签模型"""

    __tablename__ = "labels"

    name = Column(String(100), nullable=False, index=True, comment="标签名称")
    category = Column(String(100), index=True, comment="标签分类")
    project_id = Column(
        Integer,
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="项目ID"
    )

    # 关系
    project = relationship("Project", back_populates="labels")
    images = relationship(
        "Image",
        secondary=image_label_association,
        back_populates="labels"
    )