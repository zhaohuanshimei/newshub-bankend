"""
NewsHub Backend Configuration
针对移动端友好的配置设置
"""
from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    """应用程序配置"""
    
    # 应用基础配置
    APP_NAME: str = "NewsHub Backend API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API配置 - 移动端优化
    API_V1_PREFIX: str = "/api/v1"
    API_V2_PREFIX: str = "/api/v2"  # 为移动端版本迭代预留
    
    # 移动端特定配置
    MOBILE_API_TIMEOUT: int = 30  # 移动网络超时时间
    MAX_REQUEST_SIZE: int = 10 * 1024 * 1024  # 10MB 移动端文件上传限制
    PAGINATION_DEFAULT_SIZE: int = 20  # 移动端分页默认大小
    PAGINATION_MAX_SIZE: int = 100  # 移动端分页最大大小
    
    # CORS配置 - 支持移动端跨域
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # 本地开发
        "http://localhost:8080",  # 移动端开发
        "https://newshub.com",    # 生产域名
        "capacitor://localhost",  # Capacitor移动应用
        "ionic://localhost",      # Ionic移动应用
    ]
    
    # Supabase配置
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    
    # Redis配置 (Railway托管)
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # 缓存配置 - 移动端优化
    CACHE_TTL_SHORT: int = 300    # 5分钟 - 实时数据
    CACHE_TTL_MEDIUM: int = 1800  # 30分钟 - 新闻列表
    CACHE_TTL_LONG: int = 3600    # 1小时 - 用户数据
    
    # JWT认证配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天 (移动端长期登录)
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30天
    
    # 推送通知配置 (移动端)
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    FCM_SERVER_KEY: Optional[str] = None
    
    # 图片存储配置
    MAX_IMAGE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    
    # API限流配置 - 移动端友好
    RATE_LIMIT_PER_MINUTE: int = 100  # 每分钟100次请求
    RATE_LIMIT_BURST: int = 20        # 突发请求限制
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建全局配置实例
settings = Settings()

# 移动端API响应格式标准
class MobileAPIResponse:
    """移动端统一响应格式"""
    
    @staticmethod
    def success(data=None, message="success", code=200):
        return {
            "success": True,
            "code": code,
            "message": message,
            "data": data,
            "timestamp": int(__import__("time").time())
        }
    
    @staticmethod
    def error(message="error", code=400, errors=None):
        return {
            "success": False,
            "code": code,
            "message": message,
            "errors": errors,
            "timestamp": int(__import__("time").time())
        } 