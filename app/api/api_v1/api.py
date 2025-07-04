"""
NewsHub API v1 路由配置
移动端友好的API路由结构
"""
from fastapi import APIRouter

# 创建主路由器
api_router = APIRouter()

# 临时的测试端点，后续会替换为实际的业务路由
@api_router.get("/status")
async def api_status():
    """API状态检查"""
    return {
        "success": True,
        "message": "NewsHub API v1 is running",
        "version": "1.0.0"
    }

# TODO: 后续将添加以下路由模块
# from app.api.api_v1.endpoints import news, auth, users, categories
# api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
# api_router.include_router(users.router, prefix="/users", tags=["用户"])
# api_router.include_router(news.router, prefix="/news", tags=["新闻"])
# api_router.include_router(categories.router, prefix="/categories", tags=["分类"]) 