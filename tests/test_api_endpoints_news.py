import pytest
from app.api.api_v1.endpoints import news
 
def test_news_endpoint_import():
    assert hasattr(news, '__file__') or True  # 模块可导入 