"""
新闻数据模型
针对移动端新闻展示和缓存优化
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, HttpUrl
from enum import Enum

class NewsCategory(str, Enum):
    """新闻分类枚举"""
    TECHNOLOGY = "technology"
    BUSINESS = "business"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    SCIENCE = "science"
    POLITICS = "politics"
    WORLD = "world"
    LOCAL = "local"

class NewsStatus(str, Enum):
    """新闻状态"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class NewsBase(BaseModel):
    """新闻基础模型"""
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    category: NewsCategory
    tags: List[str] = []
    
class NewsCreate(NewsBase):
    """新闻创建模型"""
    source_url: Optional[HttpUrl] = None
    author: Optional[str] = None
    
class NewsUpdate(BaseModel):
    """新闻更新模型"""
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    category: Optional[NewsCategory] = None
    tags: Optional[List[str]] = None
    
class NewsInDB(NewsBase):
    """数据库中的新闻模型"""
    id: str
    slug: str  # URL友好的标识符
    author: Optional[str] = None
    source_url: Optional[HttpUrl] = None
    
    # 移动端优化字段
    featured_image: Optional[str] = None
    thumbnail_image: Optional[str] = None  # 移动端缩略图
    reading_time: int = 0  # 预估阅读时间(分钟)
    
    # 统计数据
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    
    # 状态和时间
    status: NewsStatus = NewsStatus.PUBLISHED
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    
    # 移动端响应式元数据
    metadata: Dict[str, Any] = {
        "mobile_optimized": True,
        "image_sizes": {},  # 不同尺寸的图片URL
        "external_links": [],
        "related_news": []
    }

class NewsPublic(BaseModel):
    """移动端公开的新闻信息"""
    id: str
    slug: str
    title: str
    summary: Optional[str] = None
    category: NewsCategory
    tags: List[str] = []
    author: Optional[str] = None
    
    # 移动端展示字段
    featured_image: Optional[str] = None
    thumbnail_image: Optional[str] = None
    reading_time: int = 0
    
    # 统计信息
    view_count: int = 0
    like_count: int = 0
    
    # 时间信息
    created_at: datetime
    published_at: Optional[datetime] = None

class NewsListResponse(BaseModel):
    """移动端新闻列表响应"""
    items: List[NewsPublic]
    total: int
    page: int
    size: int
    has_next: bool

# Supabase数据表结构SQL
NEWS_TABLES_SQL = """
-- 新闻分类表
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    icon_url TEXT,
    color VARCHAR(7), -- 十六进制颜色
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 新闻文章表
CREATE TABLE IF NOT EXISTS news (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(255) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    content TEXT,
    category VARCHAR(50) REFERENCES categories(name),
    tags TEXT[] DEFAULT '{}',
    author VARCHAR(100),
    source_url TEXT,
    
    -- 移动端优化字段
    featured_image TEXT,
    thumbnail_image TEXT,
    reading_time INTEGER DEFAULT 0,
    
    -- 统计数据
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    
    -- 状态和时间
    status VARCHAR(20) DEFAULT 'published',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    published_at TIMESTAMP WITH TIME ZONE,
    
    -- 移动端元数据
    metadata JSONB DEFAULT '{"mobile_optimized": true, "image_sizes": {}, "external_links": [], "related_news": []}'
);

-- 用户新闻互动表 (点赞、收藏、分享)
CREATE TABLE IF NOT EXISTS user_news_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    news_id UUID REFERENCES news(id) ON DELETE CASCADE,
    interaction_type VARCHAR(20) NOT NULL, -- 'like', 'favorite', 'share', 'view'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, news_id, interaction_type)
);

-- 新闻评论表
CREATE TABLE IF NOT EXISTS news_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    news_id UUID REFERENCES news(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES news_comments(id) ON DELETE CASCADE, -- 支持回复
    content TEXT NOT NULL,
    like_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引 (移动端查询优化)
CREATE INDEX IF NOT EXISTS idx_news_category ON news(category);
CREATE INDEX IF NOT EXISTS idx_news_status ON news(status);
CREATE INDEX IF NOT EXISTS idx_news_published_at ON news(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_news_view_count ON news(view_count DESC);
CREATE INDEX IF NOT EXISTS idx_news_like_count ON news(like_count DESC);
CREATE INDEX IF NOT EXISTS idx_news_tags ON news USING GIN(tags);

CREATE INDEX IF NOT EXISTS idx_user_interactions_user_id ON user_news_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_interactions_news_id ON user_news_interactions(news_id);
CREATE INDEX IF NOT EXISTS idx_user_interactions_type ON user_news_interactions(interaction_type);

CREATE INDEX IF NOT EXISTS idx_comments_news_id ON news_comments(news_id);
CREATE INDEX IF NOT EXISTS idx_comments_user_id ON news_comments(user_id);
CREATE INDEX IF NOT EXISTS idx_comments_created_at ON news_comments(created_at DESC);

-- 更新触发器
CREATE TRIGGER update_news_updated_at BEFORE UPDATE ON news
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_comments_updated_at BEFORE UPDATE ON news_comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
""" 