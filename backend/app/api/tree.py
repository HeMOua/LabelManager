from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.services.tree_service import TreeService
from app.schemas import TreeNode
from app.models import Project

router = APIRouter()


class TreeBuildRequest(BaseModel):
    selected_tags: List[int] = []
    tag_order: List[str] = []


@router.post("/build/{project_id}", response_model=List[TreeNode])
def build_tree(
        project_id: int,
        request: TreeBuildRequest,
        db: Session = Depends(get_db)
):
    """构建树形结构"""
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    tree_service = TreeService(db)

    try:
        tree_nodes = tree_service.build_tree(
            project_id=project_id,
            selected_tags=request.selected_tags,
            tag_order=request.tag_order
        )
        return tree_nodes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build tree: {str(e)}")


@router.get("/categories/{project_id}", response_model=List[str])
def get_available_categories(project_id: int, db: Session = Depends(get_db)):
    """获取项目中可用的标签分类"""
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    tree_service = TreeService(db)

    try:
        categories = tree_service.get_available_tag_categories(project_id)
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")


@router.get("/stats/{project_id}")
def get_tree_stats(project_id: int, db: Session = Depends(get_db)):
    """获取树形结构统计信息"""
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    tree_service = TreeService(db)

    try:
        categories = tree_service.get_available_tag_categories(project_id)

        # 获取每个分类下的标签数量
        from app.models import Tag, ImageTag, Image
        from sqlalchemy import func, distinct

        category_stats = {}
        for category in categories:
            tag_count = (
                db.query(func.count(distinct(Tag.id)))
                .join(ImageTag)
                .join(Image)
                .filter(
                    Image.project_id == project_id,
                    Tag.category == category
                )
                .scalar()
            )
            category_stats[category] = tag_count

        # 获取项目图片总数
        total_images = (
            db.query(func.count(Image.id))
            .filter(Image.project_id == project_id)
            .scalar()
        )

        return {
            "project_id": project_id,
            "total_images": total_images,
            "total_categories": len(categories),
            "categories": categories,
            "category_stats": category_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")