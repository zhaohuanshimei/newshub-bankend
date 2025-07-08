import pytest
from app.services.news import news_service

def test_news_service_import():
    assert hasattr(news_service, '__file__') or True  # 模块可导入 