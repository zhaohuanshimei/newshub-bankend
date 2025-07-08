"""
NewsHub API v1 路由配置
移动端友好的API路由结构
"""
from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, news
from app.core.config import MobileAPIResponse

# 创建主路由器
api_router = APIRouter()

# API状态检查端点
@api_router.get("/status")
async def api_status():
    """API状态检查"""
    return MobileAPIResponse.success({
        "service": "NewsHub API v1",
        "version": "1.0.0",
        "status": "running"
    })

# 包含业务路由模块
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(news.router, prefix="/news", tags=["新闻"]) 