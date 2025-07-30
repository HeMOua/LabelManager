from PIL import Image as PILImage
import io
import uuid
import os
from typing import Tuple, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import Image, Tag, ImageTag
from app.schemas import ImageCreate, ImageWithTags
from app.services.minio_service import MinioService
from app.core.config import settings

class ImageService:
    def __init__(self, db: Session):
        self.db = db
        self.minio_service = MinioService()
    
    def create_thumbnail(self, image_data: bytes) -> bytes:
        """创建缩略图"""
        try:
            image = PILImage.open(io.BytesIO(image_data))
            image.thumbnail(settings.THUMBNAIL_SIZE, PILImage.Resampling.LANCZOS)
            
            # 转换为RGB（如果是RGBA）
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            
            # 保存缩略图
            thumbnail_io = io.BytesIO()
            image.save(thumbnail_io, format="JPEG", quality=settings.THUMBNAIL_QUALITY)
            return thumbnail_io.getvalue()
        except Exception as e:
            raise ValueError(f"Failed to create thumbnail: {str(e)}")
    
    def get_image_info(self, image_data: bytes) -> Tuple[int, int]:
        """获取图片尺寸信息"""
        try:
            image = PILImage.open(io.BytesIO(image_data))
            return image.size
        except Exception:
            return (0, 0)
    
    async def upload_image(
        self, 
        project_id: int, 
        file_data: bytes, 
        filename: str,
        content_type: str = "image/jpeg"
    ) -> Image:
        """上传图片"""
        # 生成唯一文件名
        file_ext = os.path.splitext(filename)[1].lower()
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        thumbnail_filename = f"thumb_{unique_filename}"
        
        # 获取图片信息
        width, height = self.get_image_info(file_data)
        file_size = len(file_data)
        
        # 创建缩略图
        thumbnail_data = self.create_thumbnail(file_data)
        
        # 上传原图和缩略图到MinIO
        file_path = f"images/{unique_filename}"
        thumbnail_path = f"thumbnails/{thumbnail_filename}"
        
        if not self.minio_service.upload_file(file_data, file_path, content_type):
            raise RuntimeError("Failed to upload image")
        
        if not self.minio_service.upload_file(thumbnail_data, thumbnail_path, "image/jpeg"):
            # 如果缩略图上传失败，删除已上传的原图
            self.minio_service.delete_file(file_path)
            raise RuntimeError("Failed to upload thumbnail")
        
        # 保存到数据库
        db_image = Image(
            project_id=project_id,
            filename=filename,
            file_path=file_path,
            thumbnail_path=thumbnail_path,
            file_size=file_size,
            width=width,
            height=height,
            meta_data={"original_filename": filename}
        )
        self.db.add(db_image)
        self.db.commit()
        self.db.refresh(db_image)
        
        return db_image
    
    def get_image_with_tags(self, image_id: int) -> Optional[ImageWithTags]:
        """获取带标签的图片信息"""
        image = self.db.query(Image).filter(Image.id == image_id).first()
        if not image:
            return None
        
        # 获取图片的标签
        tags = self.db.query(Tag).join(ImageTag).filter(ImageTag.image_id == image_id).all()
        
        return ImageWithTags(
            id=image.id,
            project_id=image.project_id,
            filename=image.filename,
            file_path=image.file_path,
            thumbnail_path=image.thumbnail_path,
            file_size=image.file_size,
            width=image.width,
            height=image.height,
            meta_data=image.meta_data,
            created_at=image.created_at,
            updated_at=image.updated_at,
            tags=tags
        )
    
    def add_tags_to_image(self, image_id: int, tag_ids: List[int]) -> bool:
        """为图片添加标签"""
        try:
            # 删除现有标签关联
            self.db.query(ImageTag).filter(ImageTag.image_id == image_id).delete()
            
            # 添加新的标签关联
            for tag_id in tag_ids:
                image_tag = ImageTag(image_id=image_id, tag_id=tag_id)
                self.db.add(image_tag)
            
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False
    
    def delete_image(self, image_id: int) -> bool:
        """删除图片"""
        image = self.db.query(Image).filter(Image.id == image_id).first()
        if not image:
            return False
        
        try:
            # 删除MinIO中的文件
            self.minio_service.delete_file(image.file_path)
            if image.thumbnail_path:
                self.minio_service.delete_file(image.thumbnail_path)
            
            # 删除数据库记录
            self.db.delete(image)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False