from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.database import init_db, close_db_connections
from app.api.v1 import api_router as api_v1


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动时的初始化"""
    # 初始化数据库
    await init_db()

    yield

    # 关闭数据
    await close_db_connections()


app = FastAPI(
    title="Image Manager API",
    description="图片管理工具 API",
    version="1.0.0",
    lifespan=lifespan
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
app.include_router(api_v1, prefix="/api")

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
        port=8500
    )