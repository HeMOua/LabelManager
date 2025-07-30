from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from collections import defaultdict

from app.models import Image, Tag, ImageTag
from app.schemas import TreeNode

class TreeService:
    def __init__(self, db: Session):
        self.db = db
    
    def build_tree(self, project_id: int, selected_tags: List[int], tag_order: List[str]) -> List[TreeNode]:
        """
        根据选择的标签构建树形结构
        
        Args:
            project_id: 项目ID
            selected_tags: 选择的标签ID列表
            tag_order: 标签分类的排序顺序，如 ["颜色", "材质", "用途"]
        
        Returns:
            树形节点列表
        """
        # 获取匹配的图片和它们的标签
        images_with_tags = self._get_images_with_tags(project_id, selected_tags)
        
        if not images_with_tags:
            return []
        
        # 按照tag_order构建树形结构
        return self._build_tree_recursive(images_with_tags, tag_order, 0)
    
    def _get_images_with_tags(self, project_id: int, selected_tags: List[int]) -> List[Dict[str, Any]]:
        """获取包含指定标签的图片及其所有标签"""
        if not selected_tags:
            # 如果没有选择标签，返回项目下所有图片
            query = self.db.query(Image).filter(Image.project_id == project_id)
        else:
            # 获取包含所有选择标签的图片
            subquery = (
                self.db.query(ImageTag.image_id)
                .filter(ImageTag.tag_id.in_(selected_tags))
                .group_by(ImageTag.image_id)
                .having(self.db.func.count(ImageTag.tag_id) == len(selected_tags))
                .subquery()
            )
            
            query = (
                self.db.query(Image)
                .filter(and_(
                    Image.project_id == project_id,
                    Image.id.in_(subquery)
                ))
            )
        
        images = query.all()
        result = []
        
        for image in images:
            # 获取图片的所有标签
            tags = (
                self.db.query(Tag)
                .join(ImageTag)
                .filter(ImageTag.image_id == image.id)
                .all()
            )
            
            result.append({
                "image": image,
                "tags": {tag.category: tag for tag in tags}
            })
        
        return result
    
    def _build_tree_recursive(
        self, 
        images_with_tags: List[Dict[str, Any]], 
        tag_order: List[str], 
        level: int
    ) -> List[TreeNode]:
        """递归构建树形结构"""
        if level >= len(tag_order):
            # 到达叶子层，返回图片节点
            nodes = []
            for item in images_with_tags:
                image = item["image"]
                nodes.append(TreeNode(
                    name=image.filename,
                    type="image",
                    image_data={
                        "id": image.id,
                        "filename": image.filename,
                        "file_path": image.file_path,
                        "thumbnail_path": image.thumbnail_path,
                        "width": image.width,
                        "height": image.height
                    }
                ))
            return nodes
        
        current_category = tag_order[level]
        grouped_images = defaultdict(list)
        
        # 按当前层级的标签分类分组
        for item in images_with_tags:
            tags = item["tags"]
            if current_category in tags:
                tag_name = tags[current_category].name
                grouped_images[tag_name].append(item)
        
        nodes = []
        for tag_name, group_images in grouped_images.items():
            children = self._build_tree_recursive(group_images, tag_order, level + 1)
            nodes.append(TreeNode(
                name=tag_name,
                category=current_category,
                type="tag",
                children=children
            ))
        
        return nodes
    
    def get_available_tag_categories(self, project_id: int) -> List[str]:
        """获取项目中可用的标签分类"""
        categories = (
            self.db.query(Tag.category)
            .join(ImageTag)
            .join(Image)
            .filter(Image.project_id == project_id)
            .distinct()
            .all()
        )
        return [category[0] for category in categories]