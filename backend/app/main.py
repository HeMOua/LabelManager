from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import app.models
from app.core.database import init_db
from app.api import api_router
from app.services.storage.storage_service import get_storage_service


@asynccontextmanager
async def lifespan(application: FastAPI):
    """ 应用生命周期管理 """
    # 初始化数据库
    await init_db()

    # 初始化存储服务
    storage_service = get_storage_service()
    await storage_service.ensure_storage_ready()

    yield


app = FastAPI(
    title="Image Manager API",
    description="图片管理工具 API",
    version="1.0.0",
    lifespan=lifespan,
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