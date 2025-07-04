# NewsHub Backend API

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

NewsHub移动端友好的新闻聚合后端API，基于FastAPI构建，专为移动应用优化设计。

## 🚀 功能特性

- **移动端优化**: 专为移动应用设计的API响应格式和性能优化
- **现代技术栈**: FastAPI + Supabase + Redis + Railway部署
- **完整认证系统**: 基于JWT的用户认证和授权
- **新闻聚合**: 支持多源新闻聚合和智能分类
- **实时功能**: 支持WebSocket实时推送
- **高性能缓存**: Redis缓存层优化响应速度
- **API文档**: 自动生成的OpenAPI文档

## 🏗️ 技术架构

```
Frontend (Mobile)     Backend (FastAPI)     Database (Supabase)
     ↓                       ↓                       ↓
Ionic/React Native ← → FastAPI Server ← → PostgreSQL
     ↓                       ↓                       ↓
Capacitor/Expo           Redis Cache            Supabase Auth
                              ↓                       ↓
                        Railway Deploy          File Storage
```

## 📋 项目结构

```
newshub-backend/
├── app/
│   ├── api/v1/          # API路由 v1
│   ├── core/            # 核心配置
│   ├── db/              # 数据库连接
│   ├── models/          # 数据模型
│   ├── schemas/         # Pydantic模式
│   ├── services/        # 业务逻辑
│   └── utils/           # 工具函数
├── scripts/             # 数据库脚本
├── migrations/          # 数据库迁移
├── tests/               # 测试文件
├── requirements.txt     # Python依赖
└── start.py            # 快速启动脚本
```

## 🛠️ 安装和运行

### 环境要求

- Python 3.9+
- Redis (可选，用于缓存)
- Git

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/newshub-backend.git
cd newshub-backend
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### 3. 安装依赖

```bash
# 使用国内源安装（推荐）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 4. 环境配置

创建 `.env` 文件：

```env
# 基础配置
DEBUG=True
APP_NAME="NewsHub Backend API"
VERSION="1.0.0"

# Supabase配置
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Redis配置 (可选)
REDIS_URL=redis://localhost:6379
```

### 5. 初始化数据库

```bash
python scripts/init_database.py
```

### 6. 启动服务

```bash
# 方式1: 使用启动脚本
python start.py

# 方式2: 直接使用uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后访问：
- API服务: http://localhost:8000
- API文档: http://localhost:8000/docs (仅开发环境)
- 健康检查: http://localhost:8000/health

## 📱 移动端集成

### API响应格式

所有API响应都遵循统一格式：

```json
{
  "success": true,
  "code": 200,
  "message": "success",
  "data": { /* 具体数据 */ },
  "timestamp": 1234567890
}
```

### 错误响应格式

```json
{
  "success": false,
  "code": 400,
  "message": "error message",
  "errors": { /* 详细错误信息 */ },
  "timestamp": 1234567890
}
```

## 🔌 API端点

### 基础端点

- `GET /` - API信息
- `GET /health` - 健康检查
- `GET /api/v1/status` - API状态

### 认证相关 (计划中)

- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/refresh` - 刷新令牌

### 新闻相关 (计划中)

- `GET /api/v1/news` - 获取新闻列表
- `GET /api/v1/news/{id}` - 获取新闻详情
- `GET /api/v1/categories` - 获取新闻分类

## 🚀 部署

### Railway部署

1. 连接GitHub仓库到Railway
2. 设置环境变量
3. 自动部署

### Docker部署

```bash
# 构建镜像
docker build -t newshub-backend .

# 运行容器
docker run -p 8000:8000 --env-file .env newshub-backend
```

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行覆盖率测试
pytest --cov=app tests/
```

## 📝 开发日志

### v1.0.0 (2025-01-04)

- ✅ 完成基础项目架构
- ✅ 实现移动端友好的API设计
- ✅ 配置FastAPI应用和中间件
- ✅ 设计完整的数据库模型
- ✅ 创建数据库初始化脚本
- ✅ 基础功能测试通过

### 下一步计划

- 🔄 配置Supabase数据库连接
- 🔄 实现用户认证系统
- 🔄 实现新闻API功能
- 🔄 添加Redis缓存层
- 🔄 部署到Railway平台

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

本项目采用 [MIT](LICENSE) 许可证。

## 🔗 相关链接

- [FastAPI文档](https://fastapi.tiangolo.com/)
- [Supabase文档](https://supabase.com/docs)
- [Railway部署指南](https://railway.app/docs)

---

**开发团队**: NewsHub Development Team  
**最后更新**: 2025-01-04 