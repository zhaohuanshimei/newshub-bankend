"""
新闻相关API端点
支持移动端新闻浏览、搜索、互动
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List, Any
import logging

from app.core.config import settings, MobileAPIResponse
from app.db.database import get_db
from app.models.news import NewsCategory, NewsPublic, NewsListResponse
from app.services.news.news_service import NewsService
from app.services.auth.auth_service import AuthService

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

@router.get("/", response_model=dict, tags=["新闻"])
async def get_news_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    category: Optional[NewsCategory] = Query(None, description="新闻分类"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    sort: str = Query("published_at", regex="^(published_at|view_count|like_count)$", description="排序字段"),
    order: str = Query("desc", regex="^(asc|desc)$", description="排序方向"),
    db = Depends(get_db)
) -> Any:
    """
    获取新闻列表
    移动端分页和筛选
    """
    try:
        news_service = NewsService(db)
        result = await news_service.get_news_list(
            page=page,
            size=size,
            category=category,
            keyword=keyword,
            sort=sort,
            order=order
        )
        
        return MobileAPIResponse.success(
            data=result,
            message="获取新闻列表成功"
        )
    except Exception as e:
        logger.error(f"Get news list error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取新闻列表失败"
        )

@router.get("/{news_id}", response_model=dict, tags=["新闻"])
async def get_news_detail(
    news_id: str,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db = Depends(get_db)
) -> Any:
    """
    获取新闻详情
    记录用户浏览行为
    """
    try:
        news_service = NewsService(db)
        
        # 获取当前用户ID（如果已登录）
        user_id = None
        if credentials:
            try:
                auth_service = AuthService(db)
                user = await auth_service.get_current_user(credentials.credentials)
                user_id = user.id
            except:
                pass  # 未登录用户也可以浏览
        
        result = await news_service.get_news_detail(news_id, user_id)
        
        return MobileAPIResponse.success(
            data=result,
            message="获取新闻详情成功"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Get news detail error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取新闻详情失败"
        )

@router.post("/{news_id}/like", response_model=dict, tags=["新闻"])
async def like_news(
    news_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_db)
) -> Any:
    """
    点赞/取消点赞新闻
    移动端一键互动
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.get_current_user(credentials.credentials)
        
        news_service = NewsService(db)
        result = await news_service.toggle_news_like(news_id, user.id)
        
        return MobileAPIResponse.success(
            data=result,
            message="操作成功"
        )
    except ValueError as e:
        if "无效" in str(e) or "过期" in str(e):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Like news error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="操作失败"
        )

@router.post("/{news_id}/favorite", response_model=dict, tags=["新闻"])
async def favorite_news(
    news_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_db)
) -> Any:
    """
    收藏/取消收藏新闻
    移动端个人收藏管理
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.get_current_user(credentials.credentials)
        
        news_service = NewsService(db)
        result = await news_service.toggle_news_favorite(news_id, user.id)
        
        return MobileAPIResponse.success(
            data=result,
            message="操作成功"
        )
    except ValueError as e:
        if "无效" in str(e) or "过期" in str(e):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Favorite news error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="操作失败"
        )

@router.post("/{news_id}/share", response_model=dict, tags=["新闻"])
async def share_news(
    news_id: str,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db = Depends(get_db)
) -> Any:
    """
    分享新闻
    记录分享统计
    """
    try:
        # 获取当前用户ID（如果已登录）
        user_id = None
        if credentials:
            try:
                auth_service = AuthService(db)
                user = await auth_service.get_current_user(credentials.credentials)
                user_id = user.id
            except:
                pass  # 未登录用户也可以分享
        
        news_service = NewsService(db)
        result = await news_service.share_news(news_id, user_id)
        
        return MobileAPIResponse.success(
            data=result,
            message="分享成功"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Share news error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="分享失败"
        )

@router.get("/categories/list", response_model=dict, tags=["新闻"])
async def get_categories(
    db = Depends(get_db)
) -> Any:
    """
    获取新闻分类列表
    移动端分类筛选
    """
    try:
        news_service = NewsService(db)
        result = await news_service.get_categories()
        
        return MobileAPIResponse.success(
            data=result,
            message="获取分类列表成功"
        )
    except Exception as e:
        logger.error(f"Get categories error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取分类列表失败"
        )

@router.get("/trending/hot", response_model=dict, tags=["新闻"])
async def get_trending_news(
    limit: int = Query(10, ge=1, le=50, description="数量限制"),
    db = Depends(get_db)
) -> Any:
    """
    获取热门新闻
    移动端首页推荐
    """
    try:
        news_service = NewsService(db)
        result = await news_service.get_trending_news(limit)
        
        return MobileAPIResponse.success(
            data=result,
            message="获取热门新闻成功"
        )
    except Exception as e:
        logger.error(f"Get trending news error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取热门新闻失败"
        ) 