from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.core.database import get_db
from app.models import Tag, ImageTag, Image, Project
from app.schemas import (
    Tag as TagSchema,
    TagCreate,
    TagUpdate,
    TagWithCount,
    TagWithProject,
    ApiResponse
)

router = APIRouter()


@router.get("/", response_model=ApiResponse[List[TagWithCount]])
def get_tags(
        skip: int = 0,
        limit: int = 100,
        tag_type: Optional[str] = Query(None, alias="tagType", description="标签类型: global, project, all"),
        project_id: Optional[int] = Query(None, alias="projectId", description="项目ID，仅当tag_type为project时有效"),
        category: Optional[str] = Query(None, description="标签分类筛选"),
        db: Session = Depends(get_db)
):
    """获取标签列表"""
    try:
        query = db.query(
            Tag,
            func.count(ImageTag.image_id).label("image_count")
        ).outerjoin(ImageTag)

        # 根据标签类型筛选
        if tag_type == "global":
            query = query.filter(Tag.project_id.is_(None))
        elif tag_type == "project":
            if project_id:
                query = query.filter(Tag.project_id == project_id)
            else:
                query = query.filter(Tag.project_id.isnot(None))
        # tag_type == "all" 或 None 时不添加筛选条件

        # 按分类筛选
        if category:
            query = query.filter(Tag.category == category)

        tags = query.group_by(Tag.id).offset(skip).limit(limit).all()

        result = []
        for tag, image_count in tags:
            tag_dict = {
                "id": tag.id,
                "name": tag.name,
                "category": tag.category,
                "color": tag.color,
                "project_id": tag.project_id,
                "created_at": tag.created_at,
                "tag_type": tag.tag_type,
                "is_global": tag.is_global,
                "image_count": image_count or 0
            }
            result.append(TagWithCount(**tag_dict))

        return ApiResponse.success(data=result, message="获取标签列表成功")
    except Exception as e:
        return ApiResponse.error(message=f"获取标签列表失败: {str(e)}")


@router.get("/global", response_model=ApiResponse[List[TagWithCount]])
def get_global_tags(
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = Query(None, description="标签分类筛选"),
        db: Session = Depends(get_db)
):
    """获取全局标签列表"""
    try:
        query = db.query(
            Tag,
            func.count(ImageTag.image_id).label("image_count")
        ).outerjoin(ImageTag).filter(Tag.project_id.is_(None))

        if category:
            query = query.filter(Tag.category == category)

        tags = query.group_by(Tag.id).offset(skip).limit(limit).all()

        result = []
        for tag, image_count in tags:
            tag_dict = {
                "id": tag.id,
                "name": tag.name,
                "category": tag.category,
                "color": tag.color,
                "project_id": tag.project_id,
                "created_at": tag.created_at,
                "tag_type": tag.tag_type,
                "is_global": tag.is_global,
                "image_count": image_count or 0
            }
            result.append(TagWithCount(**tag_dict))

        return ApiResponse.success(data=result, message="获取全局标签列表成功")
    except Exception as e:
        return ApiResponse.error(message=f"获取全局标签列表失败: {str(e)}")


@router.get("/project/{project_id}/tags", response_model=ApiResponse[List[TagWithCount]])
def get_project_specific_tags(
        project_id: int,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = Query(None, description="标签分类筛选"),
        db: Session = Depends(get_db)
):
    """获取项目特定标签列表"""
    try:
        # 验证项目是否存在
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return ApiResponse.not_found(message="项目不存在")

        query = db.query(
            Tag,
            func.count(ImageTag.image_id).label("image_count")
        ).outerjoin(ImageTag).filter(Tag.project_id == project_id)

        if category:
            query = query.filter(Tag.category == category)

        tags = query.group_by(Tag.id).offset(skip).limit(limit).all()

        result = []
        for tag, image_count in tags:
            tag_dict = {
                "id": tag.id,
                "name": tag.name,
                "category": tag.category,
                "color": tag.color,
                "project_id": tag.project_id,
                "created_at": tag.created_at,
                "tag_type": tag.tag_type,
                "is_global": tag.is_global,
                "image_count": image_count or 0
            }
            result.append(TagWithCount(**tag_dict))

        return ApiResponse.success(data=result, message="获取项目标签列表成功")
    except Exception as e:
        return ApiResponse.error(message=f"获取项目标签列表失败: {str(e)}")


@router.get("/project/{project_id}/available", response_model=ApiResponse[List[TagWithCount]])
def get_available_tags_for_project(
        project_id: int,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = Query(None, description="标签分类筛选"),
        db: Session = Depends(get_db)
):
    """获取项目可用的所有标签（包括全局标签和项目特定标签）"""
    try:
        # 验证项目是否存在
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return ApiResponse.not_found(message="项目不存在")

        # 查询全局标签和该项目的特定标签
        query = db.query(
            Tag,
            func.count(ImageTag.image_id).label("image_count")
        ).outerjoin(ImageTag).filter(
            or_(
                Tag.project_id.is_(None),  # 全局标签
                Tag.project_id == project_id  # 项目特定标签
            )
        )

        if category:
            query = query.filter(Tag.category == category)

        tags = query.group_by(Tag.id).offset(skip).limit(limit).all()

        result = []
        for tag, image_count in tags:
            tag_dict = {
                "id": tag.id,
                "name": tag.name,
                "category": tag.category,
                "color": tag.color,
                "project_id": tag.project_id,
                "created_at": tag.created_at,
                "tag_type": tag.tag_type,
                "is_global": tag.is_global,
                "image_count": image_count or 0
            }
            result.append(TagWithCount(**tag_dict))

        return ApiResponse.success(data=result, message="获取项目可用标签成功")
    except Exception as e:
        return ApiResponse.error(message=f"获取项目可用标签失败: {str(e)}")


@router.post("/", response_model=ApiResponse[TagSchema])
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """创建标签（全局或项目特定）"""
    try:
        # 如果指定了项目ID，验证项目是否存在
        if tag.project_id:
            project = db.query(Project).filter(Project.id == tag.project_id).first()
            if not project:
                return ApiResponse.not_found(message="指定的项目不存在")

        # 检查同分类下是否已存在同名标签（在相同范围内）
        existing_tag = db.query(Tag).filter(
            Tag.name == tag.name,
            Tag.category == tag.category,
            Tag.project_id == tag.project_id
        ).first()

        if existing_tag:
            scope = "全局" if tag.project_id is None else f"项目 {tag.project_id}"
            return ApiResponse.bad_request(
                message=f"标签 '{tag.name}' 在分类 '{tag.category}' 的{scope}范围内已存在"
            )

        db_tag = Tag(**tag.model_dump())
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
        return ApiResponse.success(data=db_tag, message="标签创建成功")
    except Exception as e:
        db.rollback()
        return ApiResponse.error(message=f"标签创建失败: {str(e)}")


@router.get("/{tag_id}", response_model=ApiResponse[TagWithProject])
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """获取标签详情"""
    try:
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if tag is None:
            return ApiResponse.not_found(message="标签不存在")

        # 如果是项目标签，获取项目名称
        project_name = None
        if tag.project_id:
            project = db.query(Project).filter(Project.id == tag.project_id).first()
            project_name = project.name if project else None

        tag_dict = {
            "id": tag.id,
            "name": tag.name,
            "category": tag.category,
            "color": tag.color,
            "project_id": tag.project_id,
            "created_at": tag.created_at,
            "tag_type": tag.tag_type,
            "is_global": tag.is_global,
            "project_name": project_name
        }

        return ApiResponse.success(data=TagWithProject(**tag_dict), message="获取标签详情成功")
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
                Tag.project_id == db_tag.project_id,  # 在相同范围内检查
                Tag.id != tag_id
            ).first()

            if existing_tag:
                scope = "全局" if db_tag.project_id is None else f"项目 {db_tag.project_id}"
                return ApiResponse.bad_request(
                    message=f"标签 '{new_name}' 在分类 '{new_category}' 的{scope}范围内已存在"
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

        # 检查是否有关联的图片
        image_tags_count = db.query(ImageTag).filter(ImageTag.tag_id == tag_id).count()
        if image_tags_count > 0:
            return ApiResponse.bad_request(
                message=f"无法删除标签，该标签已被 {image_tags_count} 张图片使用"
            )

        db.delete(db_tag)
        db.commit()
        return ApiResponse.success(message="标签删除成功")
    except Exception as e:
        db.rollback()
        return ApiResponse.error(message=f"标签删除失败: {str(e)}")


@router.get("/categories/", response_model=ApiResponse[List[str]])
def get_tag_categories(
        tag_type: Optional[str] = Query(None, description="标签类型: global, project, all"),
        project_id: Optional[int] = Query(None, description="项目ID，仅当tag_type为project时有效"),
        db: Session = Depends(get_db)
):
    """获取标签分类"""
    try:
        query = db.query(Tag.category).distinct()

        # 根据标签类型筛选
        if tag_type == "global":
            query = query.filter(Tag.project_id.is_(None))
        elif tag_type == "project":
            if project_id:
                query = query.filter(Tag.project_id == project_id)
            else:
                query = query.filter(Tag.project_id.isnot(None))

        categories = query.all()
        result = [category[0] for category in categories]
        return ApiResponse.success(data=result, message="获取标签分类成功")
    except Exception as e:
        return ApiResponse.error(message=f"获取标签分类失败: {str(e)}")


@router.get("/category/{category}", response_model=ApiResponse[List[TagSchema]])
def get_tags_by_category(
        category: str,
        tag_type: Optional[str] = Query(None, description="标签类型: global, project, all"),
        project_id: Optional[int] = Query(None, description="项目ID，仅当tag_type为project时有效"),
        db: Session = Depends(get_db)
):
    """根据分类获取标签"""
    try:
        query = db.query(Tag).filter(Tag.category == category)

        # 根据标签类型筛选
        if tag_type == "global":
            query = query.filter(Tag.project_id.is_(None))
        elif tag_type == "project":
            if project_id:
                query = query.filter(Tag.project_id == project_id)
            else:
                query = query.filter(Tag.project_id.isnot(None))

        tags = query.all()
        return ApiResponse.success(data=tags, message=f"获取分类 '{category}' 下的标签成功")
    except Exception as e:
        return ApiResponse.error(message=f"获取分类标签失败: {str(e)}")


@router.get("/project/{project_id}/used", response_model=ApiResponse[List[TagWithCount]])
def get_project_used_tags(project_id: int, db: Session = Depends(get_db)):
    """获取项目中实际使用的标签（包括全局和项目特定标签）"""
    try:
        # 验证项目是否存在
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return ApiResponse.not_found(message="项目不存在")

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
                "color": tag.color,
                "project_id": tag.project_id,
                "created_at": tag.created_at,
                "tag_type": tag.tag_type,
                "is_global": tag.is_global,
                "image_count": image_count or 0
            }
            result.append(TagWithCount(**tag_dict))

        return ApiResponse.success(data=result, message="获取项目使用标签成功")
    except Exception as e:
        return ApiResponse.error(message=f"获取项目使用标签失败: {str(e)}")


@router.post("/project/{project_id}/copy-global", response_model=ApiResponse[List[TagSchema]])
def copy_global_tags_to_project(
        project_id: int,
        tag_ids: List[int],
        db: Session = Depends(get_db)
):
    """将全局标签复制为项目特定标签"""
    try:
        # 验证项目是否存在
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return ApiResponse.not_found(message="项目不存在")

        # 获取要复制的全局标签
        global_tags = db.query(Tag).filter(
            Tag.id.in_(tag_ids),
            Tag.project_id.is_(None)
        ).all()

        if len(global_tags) != len(tag_ids):
            return ApiResponse.bad_request(message="部分标签不存在或不是全局标签")

        copied_tags = []
        for global_tag in global_tags:
            # 检查项目中是否已存在同名同分类的标签
            existing_tag = db.query(Tag).filter(
                Tag.name == global_tag.name,
                Tag.category == global_tag.category,
                Tag.project_id == project_id
            ).first()

            if existing_tag:
                continue  # 跳过已存在的标签

            # 创建项目特定标签
            new_tag = Tag(
                name=global_tag.name,
                category=global_tag.category,
                color=global_tag.color,
                project_id=project_id
            )
            db.add(new_tag)
            copied_tags.append(new_tag)

        db.commit()
        for tag in copied_tags:
            db.refresh(tag)

        return ApiResponse.success(
            data=copied_tags,
            message=f"成功复制 {len(copied_tags)} 个标签到项目"
        )
    except Exception as e:
        db.rollback()
        return ApiResponse.error(message=f"复制标签失败: {str(e)}")
