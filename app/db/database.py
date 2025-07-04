"""
NewsHub Database Configuration
Supabase PostgreSQL 连接配置
"""
from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Supabase客户端实例
supabase: Client = None

def get_supabase_client() -> Client:
    """获取Supabase客户端实例"""
    global supabase
    
    if supabase is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
            logger.warning("Supabase credentials not configured")
            return None
            
        try:
            supabase = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_ANON_KEY
            )
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            return None
    
    return supabase

def get_supabase_admin_client() -> Client:
    """获取Supabase管理员客户端实例（用于后台操作）"""
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        logger.warning("Supabase admin credentials not configured")
        return None
        
    try:
        admin_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
        logger.info("Supabase admin client initialized successfully")
        return admin_client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase admin client: {e}")
        return None

# 依赖注入函数
async def get_db() -> Client:
    """FastAPI依赖注入：获取数据库客户端"""
    client = get_supabase_client()
    if client is None:
        raise Exception("Database connection not available")
    return client 