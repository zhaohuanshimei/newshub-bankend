"""
认证服务层
处理用户注册、登录、令牌管理
"""
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from supabase import Client

from app.core.config import settings
from app.schemas.requests.auth import LoginRequest, RegisterRequest
from app.schemas.responses.auth import TokenResponse, UserResponse, LoginResponse, RegisterResponse

class AuthService:
    def __init__(self, db: Client):
        self.db = db
        
    async def register_user(self, request: RegisterRequest) -> RegisterResponse:
        """用户注册"""
        try:
            # 检查用户是否已存在
            existing_user = self.db.table('users').select('*').eq('email', request.email).execute()
            if existing_user.data:
                raise ValueError("邮箱已被注册")
                
            # 检查用户名是否已存在
            existing_username = self.db.table('users').select('*').eq('username', request.username).execute()
            if existing_username.data:
                raise ValueError("用户名已被使用")
            
            # 使用Supabase Auth注册
            auth_response = self.db.auth.sign_up({
                "email": request.email,
                "password": request.password
            })
            
            if not auth_response.user:
                raise ValueError("注册失败")
            
            # 创建用户资料
            user_data = {
                "auth_id": auth_response.user.id,
                "username": request.username,
                "full_name": request.full_name,
                "device_id": request.device_id,
                "push_token": request.push_token,
                "preferences": {
                    "categories": [],
                    "notification_enabled": True,
                    "theme": "light",
                    "language": "zh-CN"
                }
            }
            
            user_result = self.db.table('users').insert(user_data).execute()
            if not user_result.data:
                raise ValueError("创建用户资料失败")
            
            user_profile = user_result.data[0]
            
            return RegisterResponse(
                user=UserResponse(
                    id=user_profile['id'],
                    email=request.email,
                    username=user_profile['username'],
                    full_name=user_profile['full_name'],
                    avatar_url=user_profile.get('avatar_url'),
                    is_verified=False,
                    created_at=user_profile['created_at'],
                    preferences=user_profile['preferences']
                )
            )
            
        except Exception as e:
            raise ValueError(f"注册失败: {str(e)}")
    
    async def login_user(self, request: LoginRequest) -> LoginResponse:
        """用户登录"""
        try:
            # Supabase Auth登录
            auth_response = self.db.auth.sign_in_with_password({
                "email": request.email,
                "password": request.password
            })
            
            if not auth_response.user:
                raise ValueError("邮箱或密码错误")
            
            # 获取用户资料
            user_result = self.db.table('users').select('*').eq('auth_id', auth_response.user.id).execute()
            if not user_result.data:
                raise ValueError("用户资料不存在")
            
            user_profile = user_result.data[0]
            
            # 更新设备信息和最后登录时间
            update_data = {"last_login_at": datetime.utcnow().isoformat()}
            if request.device_id:
                update_data["device_id"] = request.device_id
            if request.push_token:
                update_data["push_token"] = request.push_token
                
            self.db.table('users').update(update_data).eq('id', user_profile['id']).execute()
            
            # 生成自定义JWT令牌
            access_token = self._generate_access_token(user_profile['id'])
            refresh_token = self._generate_refresh_token(user_profile['id'])
            
            return LoginResponse(
                token=TokenResponse(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                    user_id=user_profile['id']
                ),
                user=UserResponse(
                    id=user_profile['id'],
                    email=request.email,
                    username=user_profile['username'],
                    full_name=user_profile['full_name'],
                    avatar_url=user_profile.get('avatar_url'),
                    is_verified=auth_response.user.email_confirmed_at is not None,
                    created_at=user_profile['created_at'],
                    preferences=user_profile['preferences']
                )
            )
            
        except Exception as e:
            raise ValueError(f"登录失败: {str(e)}")
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """刷新访问令牌"""
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            
            if not user_id:
                raise ValueError("无效的刷新令牌")
            
            # 验证用户存在
            user_result = self.db.table('users').select('id').eq('id', user_id).execute()
            if not user_result.data:
                raise ValueError("用户不存在")
            
            # 生成新的访问令牌
            new_access_token = self._generate_access_token(user_id)
            
            return TokenResponse(
                access_token=new_access_token,
                refresh_token=refresh_token,  # 刷新令牌保持不变
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user_id=user_id
            )
            
        except ExpiredSignatureError:
            raise ValueError("刷新令牌已过期")
        except InvalidTokenError:
            raise ValueError("无效的刷新令牌")
    
    async def logout_user(self, access_token: str) -> None:
        """用户登出"""
        try:
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            
            if user_id:
                # 清理推送令牌
                self.db.table('users').update({"push_token": None}).eq('id', user_id).execute()
                
        except InvalidTokenError:
            pass  # 登出操作即使令牌无效也应该成功
    
    async def get_current_user(self, access_token: str) -> UserResponse:
        """获取当前用户信息"""
        try:
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            
            if not user_id:
                raise ValueError("无效的访问令牌")
            
            user_result = self.db.table('users').select('*').eq('id', user_id).execute()
            if not user_result.data:
                raise ValueError("用户不存在")
            
            user_profile = user_result.data[0]
            
            return UserResponse(
                id=user_profile['id'],
                email=user_profile.get('email', ''),
                username=user_profile['username'],
                full_name=user_profile['full_name'],
                avatar_url=user_profile.get('avatar_url'),
                is_verified=True,  # 假设已验证
                created_at=user_profile['created_at'],
                preferences=user_profile['preferences']
            )
            
        except ExpiredSignatureError:
            raise ValueError("访问令牌已过期")
        except InvalidTokenError:
            raise ValueError("无效的访问令牌")
    
    def _generate_access_token(self, user_id: str) -> str:
        """生成访问令牌"""
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": user_id,
            "exp": expire,
            "type": "access"
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    def _generate_refresh_token(self, user_id: str) -> str:
        """生成刷新令牌"""
        expire = datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": user_id,
            "exp": expire,
            "type": "refresh"
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM) 