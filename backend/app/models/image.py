from sqlalchemy import Column, Integer, String, Text, BigInteger, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    thumbnail_path = Column(String(512))
    file_size = Column(BigInteger)
    width = Column(Integer)
    height = Column(Integer)
    meta_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    project = relationship("Project", back_populates="images")
    image_tags = relationship("ImageTag", back_populates="image", cascade="all, delete-orphan")