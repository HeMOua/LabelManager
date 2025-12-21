from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class AnnotationFile(BaseModel):
    """标注文件模型"""

    __tablename__ = "annotation_files"

    annotation_group_id = Column(
        Integer,
        ForeignKey('annotation_groups.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="标注组ID"
    )
    image_id = Column(
        Integer,
        ForeignKey('images.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="图片ID"
    )
    content = Column(Text, nullable=False, comment="标注内容")
    format = Column(String(16), nullable=False, comment="标注格式（如：json, xml, coco等）")
    version = Column(Integer, default=1, nullable=False, comment="版本号")

    # 关系
    annotation_group = relationship("AnnotationGroup", back_populates="annotation_files")
    image = relationship("Image", back_populates="annotation_files")
