from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base

class ImageTag(Base):
    __tablename__ = "image_tags"
    
    image_id = Column(Integer, ForeignKey("images.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)
    
    # 关系
    image = relationship("Image", back_populates="image_tags")
    tag = relationship("Tag", back_populates="image_tags")