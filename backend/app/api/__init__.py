from fastapi import APIRouter
from .projects import router as projects_router
from .tags import router as tags_router
from .images import router as images_router
from .tree import router as tree_router
from .files import router as files_router

api_router = APIRouter()

api_router.include_router(projects_router, prefix="/projects", tags=["projects"])
api_router.include_router(tags_router, prefix="/tags", tags=["tags"])
api_router.include_router(images_router, prefix="/images", tags=["images"])
api_router.include_router(tree_router, prefix="/tree", tags=["tree"])
api_router.include_router(files_router, tags=["files"])