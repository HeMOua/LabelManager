from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models import Project, Image
from app.schemas import (
    Project as ProjectSchema,
    ProjectCreate,
    ProjectUpdate,
    ProjectWithImageCount,
    ApiResponse
)

router = APIRouter()


@router.get("/", response_model=ApiResponse[List[ProjectWithImageCount]])
def get_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取项目列表"""
    try:
        projects = (
            db.query(
                Project,
                func.count(Image.id).label("image_count")
            )
            .outerjoin(Image)
            .group_by(Project.id)
            .offset(skip)
            .limit(limit)
            .all()
        )

        result = []
        for project, image_count in projects:
            project_dict = {
                "id": project.id,
                "name": project.name,
                "status": project.status,
                "description": project.description,
                "created_at": project.created_at,
                "updated_at": project.updated_at,
                "image_count": image_count or 0
            }
            result.append(ProjectWithImageCount(**project_dict))

        return ApiResponse.success(data=result, message="获取项目列表成功")
    except Exception as e:
        return ApiResponse.error(message=f"获取项目列表失败: {str(e)}")


@router.post("/", response_model=ApiResponse[ProjectSchema])
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """创建项目"""
    try:
        db_project = Project(**project.model_dump())
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return ApiResponse.success(data=db_project, message="项目创建成功")
    except Exception as e:
        db.rollback()
        return ApiResponse.error(message=f"项目创建失败: {str(e)}")


@router.get("/{project_id}", response_model=ApiResponse[ProjectSchema])
def get_project(project_id: int, db: Session = Depends(get_db)):
    """获取项目详情"""
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project is None:
            return ApiResponse.not_found(message="项目不存在")
        return ApiResponse.success(data=project, message="获取项目详情成功")
    except Exception as e:
        return ApiResponse.error(message=f"获取项目详情失败: {str(e)}")


@router.put("/{project_id}", response_model=ApiResponse[ProjectSchema])
def update_project(project_id: int, project: ProjectUpdate, db: Session = Depends(get_db)):
    """更新项目"""
    try:
        db_project = db.query(Project).filter(Project.id == project_id).first()
        if db_project is None:
            return ApiResponse.not_found(message="项目不存在")

        update_data = project.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_project, field, value)

        db.commit()
        db.refresh(db_project)
        return ApiResponse.success(data=db_project, message="项目更新成功")
    except Exception as e:
        db.rollback()
        return ApiResponse.error(message=f"项目更新失败: {str(e)}")


@router.delete("/{project_id}", response_model=ApiResponse[None])
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """删除项目"""
    try:
        db_project = db.query(Project).filter(Project.id == project_id).first()
        if db_project is None:
            return ApiResponse.not_found(message="项目不存在")

        db.delete(db_project)
        db.commit()
        return ApiResponse.success(message="项目删除成功")
    except Exception as e:
        db.rollback()
        return ApiResponse.error(message=f"项目删除失败: {str(e)}")
