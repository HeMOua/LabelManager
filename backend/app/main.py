from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.core.config import settings
from app.core.database import init_db
from app.api import api_router
from app.services.minio_service import MinioService

app = FastAPI(
    title="Image Manager API",
    description="图片管理工具 API",
    version="1.0.0"
)

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    # 初始化数据库
    await init_db()
    
    # 初始化MinIO
    minio_service = MinioService()
    await minio_service.ensure_bucket_exists()

@app.get("/")
async def root():
    return {"message": "Image Manager API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8500,
        reload=True
    )