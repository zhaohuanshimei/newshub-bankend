"""
用户数据模型
支持移动端认证和个性化功能
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    """用户基础模型"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    
class UserCreate(UserBase):
    """用户创建模型"""
    password: str
    device_id: Optional[str] = None  # 移动设备标识
    push_token: Optional[str] = None  # 推送令牌

class UserUpdate(BaseModel):
    """用户更新模型"""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    push_token: Optional[str] = None
    preferences: Optional[dict] = None

class UserInDB(UserBase):
    """数据库中的用户模型"""
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    is_verified: bool = False
    
    # 移动端相关字段
    last_login_at: Optional[datetime] = None
    device_id: Optional[str] = None
    push_token: Optional[str] = None
    
    # 用户偏好设置
    preferences: dict = {
        "categories": [],  # 关注的新闻分类
        "notification_enabled": True,
        "theme": "light",  # light/dark
        "language": "zh-CN"
    }
    
    # 统计数据
    read_count: int = 0
    favorite_count: int = 0
    
class UserPublic(BaseModel):
    """公开的用户信息"""
    id: str
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime

# Supabase数据表结构SQL
USER_TABLE_SQL = """
-- 用户表 (利用Supabase Auth)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    avatar_url TEXT,
    device_id VARCHAR(255),
    push_token TEXT,
    preferences JSONB DEFAULT '{"categories": [], "notification_enabled": true, "theme": "light", "language": "zh-CN"}',
    read_count INTEGER DEFAULT 0,
    favorite_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_auth_id ON users(auth_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_device_id ON users(device_id);

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
""" 