from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    image_tags = relationship("ImageTag", back_populates="tag", cascade="all, delete-orphan")