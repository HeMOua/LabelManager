from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models import Project, Image
from app.schemas import Project as ProjectSchema, ProjectCreate, ProjectUpdate, ProjectWithImageCount

router = APIRouter()

@router.get("/", response_model=List[ProjectWithImageCount])
def get_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取项目列表"""
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
            "description": project.description,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "image_count": image_count or 0
        }
        result.append(ProjectWithImageCount(**project_dict))
    
    return result

@router.post("/", response_model=ProjectSchema)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """创建项目"""
    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/{project_id}", response_model=ProjectSchema)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """获取项目详情"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=ProjectSchema)
def update_project(project_id: int, project: ProjectUpdate, db: Session = Depends(get_db)):
    """更新项目"""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """删除项目"""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_project)
    db.commit()