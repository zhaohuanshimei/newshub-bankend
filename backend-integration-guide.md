# NewsHub 前后端对接指导文档

> **文档版本**: v2.0  
> **更新时间**: 2025-01-17  
> **适用项目**: NewsHub 新闻聚合平台  
> **后端技术栈**: Python + FastAPI + PostgreSQL  
> **前端技术栈**: React 18 + TypeScript + Vite + Zustand

## 📋 目录

- [1. 项目概述](#1-项目概述)
- [2. 前端架构分析](#2-前端架构分析)
- [3. 数据模型定义](#3-数据模型定义)
- [4. API设计规范](#4-api设计规范)
- [5. 核心接口清单](#5-核心接口清单)
- [6. 状态管理对接](#6-状态管理对接)
- [7. 认证与权限](#7-认证与权限)
- [8. 错误处理](#8-错误处理)
- [9. 开发环境配置](#9-开发环境配置)
- [10. 联调测试规范](#10-联调测试规范)

---

## 1. 项目概述

### 1.1 项目背景
NewsHub 是一个现代化的新闻聚合平台，前端基于 React 18 + TypeScript + Vite 架构，采用组件化设计和 Zustand 状态管理，具有完整的响应式设计和 Glassmorphism 视觉效果。

### 1.2 技术架构
```
前端 (React 18 + TypeScript + Zustand)
    ↕ HTTP/WebSocket (Axios)
后端 (FastAPI + Python + SQLAlchemy)
    ↕ SQL
数据库 (PostgreSQL + Redis)
```

### 1.3 核心功能模块
基于前端代码分析，确定以下核心模块：

- **新闻系统**: 新闻列表、详情、搜索、分类、收藏、点赞
- **用户系统**: 注册、登录、个人偏好、用户中心
- **社区功能**: 话题讨论、用户互动、专家认证
- **AI工具**: 情感分析、趋势预测、关键词提取、智能摘要
- **数据分析**: 排行榜、热门话题、统计分析

---

## 2. 前端架构分析

### 2.1 页面路由结构
```typescript
// 前端路由配置
{
  "/": HomePage,              // 首页 - 新闻列表和筛选
  "/ranking": RankingPage,    // 排行榜 - 多维度排行
  "/detail/:id": DetailPage,  // 详情页 - 新闻详情和评论
  "/community": CommunityPage,// 社区 - 话题讨论
  "/ai-tools": AIToolsPage,   // AI工具 - 分析工具集
  "/user": UserPage          // 用户中心 - 个人设置
}
```

### 2.2 组件化架构
```
src/
├── components/
│   ├── ui/                 # 基础UI组件
│   │   ├── Button/
│   │   ├── Card/
│   │   ├── Input/
│   │   └── OptimizedImage/
│   ├── business/           # 业务组件
│   │   ├── NewsCard/       # 新闻卡片
│   │   ├── CategoryFilter/ # 分类筛选
│   │   └── TrendingTopics/ # 热门话题
│   └── Layout/            # 布局组件
│       ├── Header/        # 顶部导航
│       ├── Sidebar/       # 侧边栏
│       └── Footer/        # 页脚
├── store/                 # Zustand状态管理
│   └── newsStore.ts       # 新闻状态管理
├── pages/                 # 页面组件
└── contexts/              # React Context
    └── ThemeContext.tsx   # 主题管理
```

### 2.3 状态管理架构 (Zustand)
```typescript
// newsStore.ts - 核心状态管理
interface NewsState {
  // 数据状态
  news: NewsItem[];
  selectedCategory: string;
  loading: boolean;
  error: string | null;
  
  // 异步操作
  fetchNews: (category?: string) => Promise<void>;
  searchNews: (query: string) => Promise<void>;
  
  // 用户交互
  bookmarkNews: (newsId: string) => void;
  likeNews: (newsId: string) => void;
}
```

---

## 3. 数据模型定义

### 3.1 前端 TypeScript 接口

#### 新闻数据模型 (基于 NewsCard 组件)
```typescript
interface NewsItem {
  id: string;
  title: string;
  summary: string;
  category: string;
  source: string;
  publishTime: string;        // 相对时间 "2小时前"
  readCount: number;          // 阅读量
  commentCount: number;       // 评论数
  imageUrl: string;          // 主图URL
  isVideo?: boolean;         // 是否视频内容
  isHot?: boolean;           // 是否热门
  tags: string[];            // 标签数组
}
```

#### 分类数据模型 (基于 CategoryFilter 组件)
```typescript
interface Category {
  id: string;
  name: string;
  count: number;             // 该分类下的新闻数量
}
```

#### 热门话题模型 (基于 TrendingTopics 组件)
```typescript
interface TrendingTopic {
  name: string;
  heat: number;              // 热度值 0-100
}
```

#### 社区话题模型 (基于 CommunityPage)
```typescript
interface Topic {
  id: string;
  title: string;
  content: string;
  author: string;
  authorAvatar: string;
  authorBadge?: 'expert' | 'vip' | 'moderator';
  category: string;
  publishTime: string;
  replyCount: number;
  likeCount: number;
  viewCount: number;
  isPinned?: boolean;
  isHot?: boolean;
  tags: string[];
  lastReply?: {
    author: string;
    time: string;
  };
}
```

#### AI工具模型 (基于 AIToolsPage)
```typescript
interface AITool {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType;
  category: string;
  usage: number;             // 使用量百分比
  accuracy: number;          // 准确率百分比
  status: 'active' | 'processing' | 'maintenance';
}

interface AnalysisResult {
  id: string;
  type: string;
  input: string;
  output: any;               // 根据工具类型变化
  timestamp: string;
  confidence: number;        // 置信度
}
```

### 3.2 后端数据库模型 (SQLAlchemy)

#### 新闻表 (news)
```sql
CREATE TABLE news (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    content TEXT,                    -- 完整内容（详情页使用）
    category_id UUID REFERENCES categories(id),
    source_name VARCHAR(200),
    source_url VARCHAR(1000),
    author VARCHAR(200),
    image_url VARCHAR(1000),
    is_video BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMP WITH TIME ZONE,
    view_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引优化
CREATE INDEX idx_news_category_published ON news(category_id, published_at DESC);
CREATE INDEX idx_news_published_featured ON news(published_at DESC, is_featured);
CREATE INDEX idx_news_view_count ON news(view_count DESC);
```

#### 分类表 (categories)
```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 初始分类数据
INSERT INTO categories (name, slug, sort_order) VALUES
('全部', 'all', 0),
('科技', 'tech', 1),
('财经', 'finance', 2),
('国际', 'international', 3),
('体育', 'sports', 4),
('娱乐', 'entertainment', 5);
```

#### 标签表 (tags)
```sql
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE news_tags (
    news_id UUID REFERENCES news(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (news_id, tag_id)
);
```

#### 用户表 (users)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(1000),
    display_name VARCHAR(200),
    bio TEXT,
    badge_type VARCHAR(50),              -- expert, vip, moderator
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE
);
```

#### 用户行为表
```sql
-- 收藏表
CREATE TABLE user_favorites (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    news_id UUID REFERENCES news(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (user_id, news_id)
);

-- 点赞表
CREATE TABLE user_likes (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    news_id UUID REFERENCES news(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (user_id, news_id)
);

-- 阅读记录表
CREATE TABLE user_reading_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    news_id UUID REFERENCES news(id) ON DELETE CASCADE,
    read_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_duration INTEGER,              -- 阅读时长（秒）
    read_progress FLOAT DEFAULT 0       -- 阅读进度 0-1
);
```

#### 社区表
```sql
CREATE TABLE community_topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    author_id UUID REFERENCES users(id),
    reply_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_hot BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE topic_tags (
    topic_id UUID REFERENCES community_topics(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (topic_id, tag_id)
);
```

---

## 4. API设计规范

### 4.1 基础规范

#### URL设计
```
基础URL: http://localhost:8000/api/v1
路径规范: /api/v1/{resource}/{id?}/{action?}

示例:
GET  /api/v1/news              # 获取新闻列表
GET  /api/v1/news/{id}         # 获取新闻详情
POST /api/v1/news/{id}/like    # 点赞新闻
POST /api/v1/news/{id}/favorite # 收藏新闻
```

#### HTTP方法约定
```
GET    - 查询数据 (幂等)
POST   - 创建数据 / 非幂等操作
PUT    - 完整更新数据 (幂等)
PATCH  - 部分更新数据
DELETE - 删除数据 (幂等)
```

### 4.2 响应格式标准

#### 成功响应
```json
{
  "success": true,
  "data": {
    // 实际数据内容
  },
  "message": "操作成功",
  "timestamp": "2025-01-17T10:30:00Z"
}
```

#### 分页响应格式 (适配前端期望)
```json
{
  "success": true,
  "data": [
    // 数据列表
  ],
  "pagination": {
    "total": 150,
    "page": 1,
    "page_size": 20,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  },
  "message": "获取成功",
  "timestamp": "2025-01-17T10:30:00Z"
}
```

#### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "参数验证失败",
    "details": {
      "page": ["页码必须大于0"]
    }
  },
  "timestamp": "2025-01-17T10:30:00Z"
}
```

---

## 5. 核心接口清单

### 5.1 新闻接口

#### 5.1.1 获取新闻列表 (适配首页 HomePage)
```http
GET /api/v1/news
```

**查询参数:**
```typescript
interface NewsListQuery {
  page?: number;              // 页码，默认1
  page_size?: number;         // 每页数量，默认20
  category?: string;          // 分类筛选，默认'all'
  sort?: 'latest' | 'popular' | 'trending'; // 排序方式
  featured?: boolean;         // 是否只显示精选
}
```

**响应示例:**
```json
{
  "success": true,
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "人工智能技术新突破：ChatGPT-5 即将发布",
      "summary": "OpenAI 宣布将在今年发布 ChatGPT-5，新版本将具备更强的推理能力...",
      "category": "科技",
      "source": "科技日报",
      "publishTime": "2小时前",
      "readCount": 15420,
      "commentCount": 89,
      "imageUrl": "https://example.com/images/chatgpt5.jpg",
      "isVideo": false,
      "isHot": true,
      "tags": ["AI", "ChatGPT", "OpenAI", "人工智能"]
    }
  ],
  "pagination": {
    "total": 1520,
    "page": 1,
    "page_size": 20,
    "total_pages": 76,
    "has_next": true,
    "has_prev": false
  }
}
```

#### 5.1.2 获取新闻详情 (适配 DetailPage)
```http
GET /api/v1/news/{news_id}
```

**响应增强字段:**
```json
{
  "success": true,
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "人工智能技术新突破：ChatGPT-5 即将发布",
    "summary": "OpenAI 宣布将在今年发布 ChatGPT-5...",
    "content": "完整的新闻内容HTML格式...",    // 详情页专用
    "category": "科技",
    "source": "科技日报",
    "author": "张记者",                      // 详情页显示
    "publishTime": "2小时前",
    "readCount": 15420,
    "commentCount": 89,
    "likeCount": 234,                        // 详情页显示
    "imageUrl": "https://example.com/images/chatgpt5.jpg",
    "isVideo": false,
    "isHot": true,
    "tags": ["AI", "ChatGPT", "OpenAI"],
    "relatedNews": [                         // 相关推荐
      {
        "id": "related-1",
        "title": "相关新闻标题",
        "imageUrl": "...",
        "publishTime": "1天前"
      }
    ]
  }
}
```

#### 5.1.3 搜索新闻 (适配 Header 搜索功能)
```http
GET /api/v1/news/search
```

**查询参数:**
```typescript
interface SearchQuery {
  q: string;                  // 搜索关键词 (必填)
  category?: string;          // 分类筛选
  page?: number;
  page_size?: number;
  sort?: 'relevance' | 'latest' | 'popular';
}
```

#### 5.1.4 新闻交互接口 (适配 Zustand store)
```http
# 点赞/取消点赞
POST /api/v1/news/{news_id}/like
DELETE /api/v1/news/{news_id}/like

# 收藏/取消收藏
POST /api/v1/news/{news_id}/favorite
DELETE /api/v1/news/{news_id}/favorite

# 增加阅读量
POST /api/v1/news/{news_id}/view
```

**响应格式:**
```json
{
  "success": true,
  "data": {
    "action": "like",           // like, unlike, favorite, unfavorite
    "count": 235               // 更新后的计数
  }
}
```

### 5.2 分类和标签接口

#### 5.2.1 获取分类列表 (适配 CategoryFilter 组件)
```http
GET /api/v1/categories
```

**响应:**
```json
{
  "success": true,
  "data": [
    {
      "id": "all",
      "name": "全部",
      "count": 1520            // 对应前端 Category 接口
    },
    {
      "id": "tech",
      "name": "科技",
      "count": 456
    },
    {
      "id": "finance",
      "name": "财经",
      "count": 234
    }
  ]
}
```

#### 5.2.2 获取热门话题 (适配 TrendingTopics 组件)
```http
GET /api/v1/trending-topics
```

**响应:**
```json
{
  "success": true,
  "data": [
    {
      "name": "ChatGPT",
      "heat": 98               // 热度值 0-100
    },
    {
      "name": "新能源汽车",
      "heat": 87
    }
  ]
}
```

### 5.3 排行榜接口 (适配 RankingPage)

#### 5.3.1 获取排行榜数据
```http
GET /api/v1/rankings
```

**查询参数:**
```typescript
interface RankingQuery {
  type: 'hot' | 'trending' | 'latest';    // 排行类型
  period: 'hour' | 'day' | 'week' | 'month'; // 时间范围
  category?: string;                        // 分类筛选
  limit?: number;                          // 数量限制，默认50
}
```

### 5.4 社区接口 (适配 CommunityPage)

#### 5.4.1 获取社区话题列表
```http
GET /api/v1/community/topics
```

**查询参数:**
```typescript
interface CommunityQuery {
  page?: number;
  page_size?: number;
  category?: string;
  sort?: 'latest' | 'hot' | 'popular';
  pinned?: boolean;                        // 是否包含置顶
}
```

**响应格式 (适配前端 Topic 接口):**
```json
{
  "success": true,
  "data": [
    {
      "id": "topic-1",
      "title": "如何看待最新的AI技术发展？",
      "content": "话题内容摘要...",
      "author": "专家用户",
      "authorAvatar": "https://example.com/avatar.jpg",
      "authorBadge": "expert",
      "category": "科技讨论",
      "publishTime": "2小时前",
      "replyCount": 45,
      "likeCount": 123,
      "viewCount": 1580,
      "isPinned": false,
      "isHot": true,
      "tags": ["AI", "技术", "讨论"],
      "lastReply": {
        "author": "回复用户",
        "time": "10分钟前"
      }
    }
  ]
}
```

### 5.5 AI工具接口 (适配 AIToolsPage)

#### 5.5.1 获取AI工具列表
```http
GET /api/v1/ai-tools
```

**响应格式 (适配前端 AITool 接口):**
```json
{
  "success": true,
  "data": [
    {
      "id": "sentiment",
      "name": "情感分析",
      "description": "分析文本内容的情感倾向，识别积极、消极或中性情绪",
      "category": "文本分析",
      "usage": 89,             // 使用量百分比
      "accuracy": 94,          // 准确率百分比
      "status": "active"       // active, processing, maintenance
    }
  ]
}
```

#### 5.5.2 执行AI分析
```http
POST /api/v1/ai-tools/{tool_id}/analyze
```

**请求体:**
```json
{
  "input": "要分析的文本内容",
  "options": {
    "language": "zh-CN",
    "detailed": true
  }
}
```

**响应格式 (适配前端 AnalysisResult 接口):**
```json
{
  "success": true,
  "data": {
    "id": "analysis-1",
    "type": "sentiment",
    "input": "要分析的文本内容",
    "output": {
      "sentiment": "positive",
      "confidence": 0.92,
      "details": {
        "positive": 0.92,
        "negative": 0.05,
        "neutral": 0.03
      }
    },
    "timestamp": "2025-01-17T10:30:00Z",
    "confidence": 92
  }
}
```

### 5.6 用户系统接口

#### 5.6.1 用户注册/登录
```http
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/logout
GET  /api/v1/auth/profile
```

#### 5.6.2 用户偏好设置 (适配 UserPage)
```http
GET  /api/v1/user/preferences
PUT  /api/v1/user/preferences
GET  /api/v1/user/favorites      # 收藏列表
GET  /api/v1/user/history        # 阅读历史
```

---

## 6. 状态管理对接

### 6.1 Zustand Store 与 API 对接

基于前端 `newsStore.ts` 的需求，后端需要支持以下操作：

```typescript
// 前端状态管理需求分析
interface NewsState {
  // 数据状态 - 对应后端API响应
  news: NewsItem[];           // GET /api/v1/news
  selectedCategory: string;   // 前端本地状态
  loading: boolean;          // 前端本地状态
  error: string | null;      // 前端本地状态
  
  // 异步操作 - 需要后端API支持
  fetchNews: (category?: string) => Promise<void>;    // GET /api/v1/news?category=
  searchNews: (query: string) => Promise<void>;       // GET /api/v1/news/search?q=
  
  // 用户交互 - 需要后端API支持
  bookmarkNews: (newsId: string) => void;             // POST /api/v1/news/{id}/favorite
  likeNews: (newsId: string) => void;                 // POST /api/v1/news/{id}/like
}
```

### 6.2 API 调用规范

```typescript
// 建议的前端API调用模式
class NewsAPI {
  static async getNews(params: NewsListQuery) {
    const response = await fetch(`/api/v1/news?${new URLSearchParams(params)}`);
    return response.json();
  }
  
  static async likeNews(newsId: string) {
    const response = await fetch(`/api/v1/news/${newsId}/like`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    return response.json();
  }
}
```

---

## 7. 认证与权限

### 7.1 JWT认证方案

#### Token 格式
```
Authorization: Bearer <access_token>
```

#### 用户权限等级
- **游客**: 浏览新闻、搜索 (无需认证)
- **普通用户**: 评论、收藏、点赞
- **VIP用户**: 高级功能访问
- **专家用户**: 社区特殊标识
- **管理员**: 内容管理

### 7.2 权限控制

```python
# FastAPI 权限装饰器示例
@app.post("/api/v1/news/{news_id}/like")
async def like_news(
    news_id: str,
    current_user: User = Depends(get_current_user)  # 需要登录
):
    pass

@app.get("/api/v1/news")
async def get_news(
    current_user: Optional[User] = Depends(get_current_user_optional)  # 可选登录
):
    pass
```

---

## 8. 错误处理

### 8.1 标准错误码

```python
# 错误码定义
ERROR_CODES = {
    "VALIDATION_ERROR": "参数验证失败",
    "NOT_FOUND": "资源不存在", 
    "UNAUTHORIZED": "未授权访问",
    "FORBIDDEN": "权限不足",
    "RATE_LIMITED": "请求过于频繁",
    "SERVER_ERROR": "服务器内部错误"
}
```

### 8.2 前端错误处理

```typescript
// 建议的前端错误处理模式
try {
  const response = await NewsAPI.getNews(params);
  if (!response.success) {
    throw new Error(response.error.message);
  }
  return response.data;
} catch (error) {
  // 统一错误处理
  console.error('API调用失败:', error);
  throw error;
}
```

---

## 9. 开发环境配置

### 9.1 后端开发环境

#### 依赖包 (requirements.txt)
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
redis==5.0.1
requests==2.31.0
```

#### 环境变量 (.env)
```bash
# 数据库配置
DATABASE_URL=postgresql://username:password@localhost:5432/newshub
REDIS_URL=redis://localhost:6379/0

# JWT配置
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API配置
API_V1_STR=/api/v1
PROJECT_NAME=NewsHub API

# CORS配置
BACKEND_CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

### 9.2 数据库初始化

```python
# database/init.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 创建所有表
def create_tables():
    Base.metadata.create_all(bind=engine)
```

### 9.3 CORS配置

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 10. 联调测试规范

### 10.1 API测试清单

#### 基础功能测试
- [ ] 新闻列表获取 (分页、筛选、排序)
- [ ] 新闻详情获取
- [ ] 搜索功能
- [ ] 分类列表获取
- [ ] 热门话题获取

#### 用户交互测试
- [ ] 用户注册/登录
- [ ] 新闻点赞/取消
- [ ] 新闻收藏/取消
- [ ] 阅读记录统计

#### 社区功能测试
- [ ] 话题列表获取
- [ ] 话题详情获取
- [ ] 话题创建/回复

#### AI工具测试
- [ ] 工具列表获取
- [ ] 情感分析接口
- [ ] 趋势预测接口
- [ ] 关键词提取接口

### 10.2 性能测试

#### 响应时间要求
- 新闻列表: < 500ms
- 新闻详情: < 300ms
- 搜索接口: < 1s
- AI分析: < 3s

#### 并发测试
- 支持100+并发用户
- 数据库连接池优化
- Redis缓存策略

### 10.3 联调流程

1. **后端API开发完成**
   - 所有接口通过单元测试
   - API文档生成 (Swagger)
   - 数据库迁移完成

2. **前端适配**
   - 更新API接口地址
   - 适配响应数据格式
   - 错误处理完善

3. **集成测试**
   - 完整功能流程测试
   - 跨浏览器兼容性测试
   - 移动端适配测试

4. **性能优化**
   - API响应时间优化
   - 数据库查询优化
   - 缓存策略实施

---

## 📋 开发检查清单

### 后端开发
- [ ] 数据库表结构设计
- [ ] SQLAlchemy模型定义
- [ ] Pydantic响应模型
- [ ] FastAPI路由实现
- [ ] JWT认证中间件
- [ ] 错误处理机制
- [ ] API文档生成
- [ ] 单元测试编写

### 前端对接
- [ ] API基础URL配置
- [ ] 响应数据类型适配
- [ ] Zustand store更新
- [ ] 错误状态处理
- [ ] 加载状态管理
- [ ] 分页组件对接
- [ ] 搜索功能对接
- [ ] 用户认证流程

### 部署配置
- [ ] Docker配置文件
- [ ] 环境变量配置
- [ ] 数据库迁移脚本
- [ ] Nginx反向代理
- [ ] SSL证书配置
- [ ] 监控日志配置

---

**文档维护**: 本文档将随着开发进度持续更新，确保前后端开发的一致性和高效协作。