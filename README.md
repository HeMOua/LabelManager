# 图片管理工具

一个支持多维度标签和树形结构展示的图片管理系统。

## 功能特性

- 📁 **项目管理**：支持多项目组织图片
- 🏷️ **标签系统**：多维度标签分类（颜色、材质、用途等）
- 🌲 **树形展示**：根据标签维度生成树形结构
- 📤 **批量上传**：支持拖拽批量上传图片
- 🖼️ **缩略图**：自动生成缩略图提升浏览体验
- ⚡ **高性能**：Redis缓存 + PostgreSQL + MinIO存储

## 技术栈

### 后端
- **框架**：FastAPI
- **数据库**：PostgreSQL
- **缓存**：Redis
- **存储**：MinIO
- **图片处理**：Pillow

### 前端
- **框架**：Vue 3
- **UI库**：Element Plus
- **状态管理**：Pinia
- **构建工具**：Vite

## 快速开始

### 环境要求
- Docker & Docker Compose
- Python 3.9+
- Node.js 16+

### 启动开发环境

1. **克隆项目**
```bash
git clone https://github.com/HeMOua/image-manager.git
cd image-manager
```

2. **启动所有服务**
```bash
docker-compose up -d
```

3. **访问应用**
- 前端：http://localhost:3000
- 后端API文档：http://localhost:8000/docs
- MinIO控制台：http://localhost:9001

### 手动开发模式

#### 后端开发
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端开发
```bash
cd frontend
npm install
npm run dev
```

## 项目结构

```
image-manager/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   ├── utils/          # 工具函数
│   │   └── main.py         # 应用入口
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # Vue3 前端
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   ├── stores/         # 状态管理
│   │   ├── utils/          # 工具函数
│   │   └── main.js         # 应用入口
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml      # 容器编排
└── README.md              # 项目说明
```

## API 文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整的API文档。

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目基于 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。