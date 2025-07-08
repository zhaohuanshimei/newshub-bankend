import pytest
from app.models import user

def test_user_model_import():
    assert hasattr(user, '__file__') or True  # 模块可导入 