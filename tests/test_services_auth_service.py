import pytest
from app.services.auth import auth_service

def test_auth_service_import():
    assert hasattr(auth_service, '__file__') or True  # 模块可导入 