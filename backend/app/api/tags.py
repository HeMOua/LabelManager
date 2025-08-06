from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models import Tag, ImageTag, Image
from app.schemas import Tag as TagSchema, TagCreate, TagUpdate, TagWithCount, ApiResponse

router = APIRouter()


@router.get("/", response_model=ApiResponse[List[TagWithCount]])
def get_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取标签列表"""
    try:
        tags = (
            db.query(
                Tag,
                func.count(ImageTag.image_id).label("image_count")
            )
            .outerjoin(ImageTag)
            .group_by(Tag.id)
            .offset(skip)
            .limit(limit)
            .all()
        )

        result = []
        for tag, image_count in tags:
            tag_dict = {
                "id": tag.id,
                "name": tag.name,
                "category": tag.category,
                "created_at": tag.created_at,
                "image_count": image_count or 0
            }
            result.append(TagWithCount(**tag_dict))

        return ApiResponse.success(data=result, message="获取标签列表成功")
    except Exception as e:
        return ApiResponse.error(message=f"获取标签列表失败: {str(e)}")


@router.post("/", response_model=ApiResponse[TagSchema])
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """创建标签"""
    try:
        # 检查同分类下是否已存在同名标签
        existing_tag = db.query(Tag).filter(
            Tag.name == tag.name,
            Tag.category == tag.category
        ).first()

        if existing_tag:
            return ApiResponse.bad_request(
                message=f"标签 '{tag.name}' 在分类 '{tag.category}' 中已存在"
            )

        db_tag = Tag(**tag.model_dump())
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
        return ApiResponse.success(data=db_tag, message="标签创建成功")
    except Exception as e:
        db.rollback()
        return ApiResponse.error(message=f"标签创建失败: {str(e)}")


@router.get("/{tag_id}", response_model=ApiResponse[TagSchema])
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """获取标签详情"""
    try:
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if tag is None:
            return ApiResponse.not_found(message="标签不存在")
        return ApiResponse.success(data=tag, message="获取标签详情成功")
    except Exception as e:
        return ApiResponse.error(message=f"获取标签详情失败: {str(e)}")


@router.put("/{tag_id}", response_model=ApiResponse[TagSchema])
def update_tag(tag_id: int, tag: TagUpdate, db: Session = Depends(get_db)):
    """更新标签"""
    try:
        db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if db_tag is None:
            return ApiResponse.not_found(message="标签不存在")

        update_data = tag.model_dump(exclude_unset=True)

        # 如果更新名称或分类，检查是否冲突
        if "name" in update_data or "category" in update_data:
            new_name = update_data.get("name", db_tag.name)
            new_category = update_data.get("category", db_tag.category)

            existing_tag = db.query(Tag).filter(
                Tag.name == new_name,
                Tag.category == new_category,
                Tag.id != tag_id
            ).first()

            if existing_tag:
                return ApiResponse.bad_request(
                    message=f"标签 '{new_name}' 在分类 '{new_category}' 中已存在"
                )

        for field, value in update_data.items():
            setattr(db_tag, field, value)

        db.commit()
        db.refresh(db_tag)
        return ApiResponse.success(data=db_tag, message="标签更新成功")
    except Exception as e:
        db.rollback()
        return ApiResponse.error(message=f"标签更新失败: {str(e)}")


@router.delete("/{tag_id}", response_model=ApiResponse[None])
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """删除标签"""
    try:
        db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if db_tag is None:
            return ApiResponse.not_found(message="标签不存在")

        db.delete(db_tag)
        db.commit()
        return ApiResponse.success(message="标签删除成功")
    except Exception as e:
        db.rollback()
        return ApiResponse.error(message=f"标签删除失败: {str(e)}")


@router.get("/categories/", response_model=ApiResponse[List[str]])
def get_tag_categories(db: Session = Depends(get_db)):
    """获取所有标签分类"""
    try:
        categories = db.query(Tag.category).distinct().all()
        result = [category[0] for category in categories]
        return ApiResponse.success(data=result, message="获取标签分类成功")
    except Exception as e:
        return ApiResponse.error(message=f"获取标签分类失败: {str(e)}")


@router.get("/category/{category}", response_model=ApiResponse[List[TagSchema]])
def get_tags_by_category(category: str, db: Session = Depends(get_db)):
    """根据分类获取标签"""
    try:
        tags = db.query(Tag).filter(Tag.category == category).all()
        return ApiResponse.success(data=tags, message=f"获取分类 '{category}' 下的标签成功")
    except Exception as e:
        return ApiResponse.error(message=f"获取分类标签失败: {str(e)}")


@router.get("/project/{project_id}", response_model=ApiResponse[List[TagWithCount]])
def get_project_tags(project_id: int, db: Session = Depends(get_db)):
    """获取项目中使用的标签"""
    try:
        tags = (
            db.query(
                Tag,
                func.count(ImageTag.image_id).label("image_count")
            )
            .join(ImageTag)
            .join(Image)
            .filter(Image.project_id == project_id)
            .group_by(Tag.id)
            .all()
        )

        result = []
        for tag, image_count in tags:
            tag_dict = {
                "id": tag.id,
                "name": tag.name,
                "category": tag.category,
                "created_at": tag.created_at,
                "image_count": image_count or 0
            }
            result.append(TagWithCount(**tag_dict))

        return ApiResponse.success(data=result, message="获取项目标签成功")
    except Exception as e:
        return ApiResponse.error(message=f"获取项目标签失败: {str(e)}")
