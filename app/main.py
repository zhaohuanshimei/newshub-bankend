"""
NewsHub Backend Main Application
移动端友好的FastAPI应用配置
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import logging

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
            allowed_hosts=["newshub.com", "api.newshub.com", "*.railway.app", "localhost", "127.0.0.1", "0.0.0.0"]
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    ) 