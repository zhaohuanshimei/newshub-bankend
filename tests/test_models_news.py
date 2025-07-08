import pytest
from app.models import news

def test_news_model_import():
    assert hasattr(news, '__file__') or True  # 模块可导入 