from sqlalchemy import Column, Integer, String, Text, BigInteger, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import BaseModel

# 多对多关联表：Image 和 Label
image_label_association = Table(
    'image_label_association',
    Base.metadata,
    Column('image_id', Integer, ForeignKey('images.id', ondelete='CASCADE'), primary_key=True),
    Column('label_id', Integer, ForeignKey('labels.id', ondelete='CASCADE'), primary_key=True),
)


class Image(BaseModel):
    """图片模型"""

    __tablename__ = "images"

    filename = Column(String(255), nullable=False, comment="文件名")
    image_path = Column(String(500), nullable=False, comment="图片路径")
    thumbnail_path = Column(String(500), comment="缩略图路径")
    file_size = Column(BigInteger, comment="文件大小（字节）")
    width = Column(Integer, comment="图片宽度")
    height = Column(Integer, comment="图片高度")
    project_id = Column(
        Integer,
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="项目ID"
    )

    # 关系
    project = relationship("Project", back_populates="images")
    labels = relationship(
        "Label",
        secondary=image_label_association,
        back_populates="images"
    )
    annotation_files = relationship(
        "AnnotationFile",
        back_populates="image",
        cascade="all, delete-orphan"
    )