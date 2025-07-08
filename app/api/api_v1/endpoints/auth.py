"""
认证相关API端点
支持移动端登录、注册、令牌刷新
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Any
import logging

from app.core.config import settings, MobileAPIResponse
from app.db.database import get_db
from app.schemas.requests.auth import LoginRequest, RegisterRequest
from app.schemas.responses.auth import TokenResponse, UserResponse
from app.services.auth.auth_service import AuthService

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=dict, tags=["认证"])
async def register(
    request: RegisterRequest,
    db = Depends(get_db)
) -> Any:
    """
    用户注册
    移动端友好的注册流程
    """
    try:
        auth_service = AuthService(db)
        result = await auth_service.register_user(request)
        
        return MobileAPIResponse.success(
            data=result,
            message="注册成功"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试"
        )

@router.post("/login", response_model=dict, tags=["认证"])
async def login(
    request: LoginRequest,
    db = Depends(get_db)
) -> Any:
    """
    用户登录
    支持移动端长期登录
    """
    try:
        auth_service = AuthService(db)
        result = await auth_service.login_user(request)
        
        return MobileAPIResponse.success(
            data=result,
            message="登录成功"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请稍后重试"
        )

@router.post("/refresh", response_model=dict, tags=["认证"])
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_db)
) -> Any:
    """
    刷新访问令牌
    移动端令牌自动续期
    """
    try:
        auth_service = AuthService(db)
        result = await auth_service.refresh_token(credentials.credentials)
        
        return MobileAPIResponse.success(
            data=result,
            message="令牌刷新成功"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="令牌刷新失败"
        )

@router.post("/logout", response_model=dict, tags=["认证"])
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_db)
) -> Any:
    """
    用户登出
    清理移动端推送令牌
    """
    try:
        auth_service = AuthService(db)
        await auth_service.logout_user(credentials.credentials)
        
        return MobileAPIResponse.success(
            message="登出成功"
        )
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return MobileAPIResponse.success(
            message="登出成功"  # 登出操作总是返回成功
        )

@router.get("/profile", response_model=dict, tags=["认证"])
async def get_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_db)
) -> Any:
    """
    获取用户资料
    移动端个人信息显示
    """
    try:
        auth_service = AuthService(db)
        result = await auth_service.get_current_user(credentials.credentials)
        
        return MobileAPIResponse.success(
            data=result,
            message="获取用户信息成功"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户信息失败"
        ) 