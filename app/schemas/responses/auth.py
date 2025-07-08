"""
认证相关响应模式
移动端友好的响应格式
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TokenResponse(BaseModel):
    """令牌响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # 秒
    user_id: str

class UserResponse(BaseModel):
    """用户信息响应"""
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_verified: bool = False
    created_at: datetime
    preferences: dict = {}

class LoginResponse(BaseModel):
    """登录响应"""
    token: TokenResponse
    user: UserResponse
    message: str = "登录成功"

class RegisterResponse(BaseModel):
    """注册响应"""
    user: UserResponse
    message: str = "注册成功，请查收验证邮件" 