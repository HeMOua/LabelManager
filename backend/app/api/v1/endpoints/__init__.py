from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    user,
    project,
    image,
    label,
    annotation_group,
    annotation_file
)

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(user.router, prefix="/users", tags=["users"])
router.include_router(project.router, prefix="/projects", tags=["projects"])
router.include_router(image.router, prefix="/images", tags=["Images"])
router.include_router(label.router, prefix="/labels", tags=["Labels"])
router.include_router(annotation_group.router, prefix="/annotation-groups", tags=["Annotation Groups"])
router.include_router(annotation_file.router, prefix="/annotation-files", tags=["Annotation Files"])
