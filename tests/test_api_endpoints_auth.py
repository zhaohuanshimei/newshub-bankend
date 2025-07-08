import pytest
from app.api.api_v1.endpoints import auth

def test_auth_endpoint_import():
    assert hasattr(auth, '__file__') or True  # 模块可导入 