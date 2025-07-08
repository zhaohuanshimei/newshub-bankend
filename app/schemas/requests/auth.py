"""
认证相关请求模式
移动端登录注册数据验证
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional

class LoginRequest(BaseModel):
    """登录请求"""
    email: EmailStr
    password: str
    device_id: Optional[str] = None  # 移动设备ID
    push_token: Optional[str] = None  # 推送令牌
    remember_me: bool = True  # 移动端默认长期登录

class RegisterRequest(BaseModel):
    """注册请求"""
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    device_id: Optional[str] = None
    push_token: Optional[str] = None
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线和连字符')
        if len(v) < 3 or len(v) > 20:
            raise ValueError('用户名长度必须在3-20个字符之间')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度至少6个字符')
        return v

class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str 