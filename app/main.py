"""
NewsHub Backend Main Application
移动端友好的FastAPI应用配置
"""
from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from datetime import datetime

from app.core.config import settings, MobileAPIResponse
from app.api.api_v1.api import api_router

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    """创建并配置FastAPI应用"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="NewsHub移动端友好的新闻聚合API",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
    )
    
    # 添加CORS中间件 - 支持移动端
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count", "X-Page-Count"],  # 移动端分页信息
    )
    
    # 添加信任主机中间件
    if not settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["newshub.com", "api.newshub.com", "*.railway.app", "localhost", "127.0.0.1", "0.0.0.0", "testserver"]
        )
    
    # 请求响应时间中间件 - 移动端性能监控
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # 移动端超时警告
        if process_time > settings.MOBILE_API_TIMEOUT:
            logger.warning(f"Slow API response: {request.url} took {process_time:.2f}s")
        
        return response
    
    # 全局异常处理 - 移动端友好的错误响应
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=MobileAPIResponse.error(
                message=exc.detail,
                code=exc.status_code
            )
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content=MobileAPIResponse.error(
                message="Internal server error",
                code=500
            )
        )
    
    # 包含API路由
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    
    return app

# 创建应用实例
app = create_application()

# 健康检查端点 - 移动端监控
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return MobileAPIResponse.success({
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": int(time.time())
    })

# 移动端API信息端点
@app.get("/")
async def root():
    """API根路径信息"""
    return MobileAPIResponse.success({
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "description": "NewsHub移动端友好的新闻聚合API",
        "docs_url": "/docs" if settings.DEBUG else None,
        "health_check": "/health"
    })

@app.get("/api/v1/news")
async def mock_news_list(
    page: int = 1,
    size: int = 20,
    category: str = None,
    keyword: str = None,
    sort: str = "published_at",
    order: str = "desc"
):
    items = [
        {
            "id": str(i),
            "slug": f"test-news-{i}",
            "title": f"测试新闻 {i}",
            "category": category or ("technology" if i % 2 == 0 else "business"),
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        for i in range(1, 11)
    ]
    return {
        "success": True,
        "code": 200,
        "message": "获取新闻列表成功",
        "data": {
            "items": items,
            "total": 100,
            "page": page,
            "size": size,
            "has_next": page * size < 100
        },
        "errors": None,
        "timestamp": int(datetime.utcnow().timestamp())
    }

@app.get("/api/v1/news/{news_id}")
async def mock_news_detail(news_id: str):
    return {
        "success": True,
        "code": 200,
        "message": "获取新闻详情成功",
        "data": {
            "id": news_id,
            "slug": f"test-news-{news_id}",
            "title": f"测试新闻 {news_id}",
            "content": f"这是测试新闻 {news_id} 的内容。",
            "category": "technology" if int(news_id) % 2 == 0 else "business",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "view_count": 100 + int(news_id),
            "like_count": 10 + int(news_id),
            "comment_count": 5,
            "share_count": 2
        },
        "errors": None,
        "timestamp": int(datetime.utcnow().timestamp())
    }

@app.post("/api/v1/news/{news_id}/like")
async def mock_news_like(news_id: str):
    return {"success": True, "code": 200, "message": "点赞成功", "data": {"action": "liked", "like_count": 11}, "errors": None, "timestamp": int(datetime.utcnow().timestamp())}

@app.post("/api/v1/news/{news_id}/favorite")
async def mock_news_favorite(news_id: str):
    return {"success": True, "code": 200, "message": "收藏成功", "data": {"action": "favorited"}, "errors": None, "timestamp": int(datetime.utcnow().timestamp())}

@app.post("/api/v1/news/{news_id}/share")
async def mock_news_share(news_id: str):
    return {"success": True, "code": 200, "message": "分享成功", "data": {"action": "shared"}, "errors": None, "timestamp": int(datetime.utcnow().timestamp())}

@app.get("/api/v1/news/categories/list")
async def mock_news_categories():
    return {"success": True, "code": 200, "message": "获取分类成功", "data": {"categories": [
        {"id": "1", "name": "technology", "display_name": "科技"},
        {"id": "2", "name": "business", "display_name": "商业"},
        {"id": "3", "name": "sports", "display_name": "体育"}
    ]}, "errors": None, "timestamp": int(datetime.utcnow().timestamp())}

@app.get("/api/v1/news/trending/hot")
async def mock_news_trending():
    return {"success": True, "code": 200, "message": "获取热榜成功", "data": {"items": [
        {"id": str(i), "title": f"热榜新闻 {i}", "view_count": 1000 + i} for i in range(1, 6)
    ]}, "errors": None, "timestamp": int(datetime.utcnow().timestamp())}

@app.post("/api/v1/auth/login")
async def mock_login(data: dict = Body(...)):
    return {
        "success": True,
        "code": 200,
        "message": "登录成功",
        "data": {
            "token": "mocked-jwt-token",
            "user": {
                "id": "u1",
                "username": data.get("username", "testuser"),
                "email": data.get("email", "test@example.com"),
                "full_name": "测试用户",
                "avatar_url": None,
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
        },
        "errors": None,
        "timestamp": int(datetime.utcnow().timestamp())
    }

@app.get("/api/v1/users/me")
async def mock_user_me():
    return {
        "success": True,
        "code": 200,
        "message": "获取用户信息成功",
        "data": {
            "id": "u1",
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "测试用户",
            "avatar_url": None,
            "created_at": datetime.utcnow().isoformat() + "Z"
        },
        "errors": None,
        "timestamp": int(datetime.utcnow().timestamp())
    }

@app.get("/api/v1/news/{news_id}/comments")
async def mock_news_comments(news_id: str, page: int = 1, size: int = 10):
    comments = [
        {
            "id": str(i),
            "news_id": news_id,
            "user_id": "u1",
            "username": "testuser",
            "content": f"这是评论 {i}",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "like_count": i
        }
        for i in range(1, 6)
    ]
    return {
        "success": True,
        "code": 200,
        "message": "获取评论成功",
        "data": {
            "items": comments,
            "total": 5,
            "page": page,
            "size": size,
            "has_next": False
        },
        "errors": None,
        "timestamp": int(datetime.utcnow().timestamp())
    }

@app.post("/api/v1/news/{news_id}/comments")
async def mock_add_comment(news_id: str, data: dict = Body(...)):
    return {
        "success": True,
        "code": 200,
        "message": "评论成功",
        "data": {
            "id": "c1",
            "news_id": news_id,
            "user_id": "u1",
            "username": "testuser",
            "content": data.get("content", "mock 评论内容"),
            "created_at": datetime.utcnow().isoformat() + "Z",
            "like_count": 0
        },
        "errors": None,
        "timestamp": int(datetime.utcnow().timestamp())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    ) 