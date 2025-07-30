from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models import Tag, ImageTag, Image
from app.schemas import Tag as TagSchema, TagCreate, TagUpdate, TagWithCount

router = APIRouter()


@router.get("/", response_model=List[TagWithCount])
def get_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取标签列表"""
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

    return result


@router.post("/", response_model=TagSchema)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """创建标签"""
    # 检查同分类下是否已存在同名标签
    existing_tag = db.query(Tag).filter(
        Tag.name == tag.name,
        Tag.category == tag.category
    ).first()

    if existing_tag:
        raise HTTPException(
            status_code=400,
            detail=f"Tag '{tag.name}' already exists in category '{tag.category}'"
        )

    db_tag = Tag(**tag.dict())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.get("/{tag_id}", response_model=TagSchema)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """获取标签详情"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.put("/{tag_id}", response_model=TagSchema)
def update_tag(tag_id: int, tag: TagUpdate, db: Session = Depends(get_db)):
    """更新标签"""
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    update_data = tag.dict(exclude_unset=True)

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
            raise HTTPException(
                status_code=400,
                detail=f"Tag '{new_name}' already exists in category '{new_category}'"
            )

    for field, value in update_data.items():
        setattr(db_tag, field, value)

    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """删除标签"""
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    db.delete(db_tag)
    db.commit()


@router.get("/categories/", response_model=List[str])
def get_tag_categories(db: Session = Depends(get_db)):
    """获取所有标签分类"""
    categories = db.query(Tag.category).distinct().all()
    return [category[0] for category in categories]


@router.get("/category/{category}", response_model=List[TagSchema])
def get_tags_by_category(category: str, db: Session = Depends(get_db)):
    """根据分类获取标签"""
    tags = db.query(Tag).filter(Tag.category == category).all()
    return tags


@router.get("/project/{project_id}", response_model=List[TagWithCount])
def get_project_tags(project_id: int, db: Session = Depends(get_db)):
    """获取项目中使用的标签"""
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

    return result