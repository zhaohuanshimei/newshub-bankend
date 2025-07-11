import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from app.services.news.news_service import NewsService
from app.models.news import NewsCategory

@pytest_asyncio.fixture
def mock_db():
    db = MagicMock()
    db.table.return_value = db
    db.select.return_value = db
    db.eq.return_value = db
    db.or_.return_value = db
    db.order.return_value = db
    db.range.return_value = db
    db.execute.return_value = MagicMock(data=[{
        'id': 'nid', 'slug': 'slug', 'title': 'title', 'category': 'technology',
        'created_at': '2024-01-01T00:00:00', 'view_count': 1, 'like_count': 2
    }], count=1)
    return db

@pytest.mark.asyncio
async def test_get_news_list_success(mock_db):
    service = NewsService(mock_db)
    resp = await service.get_news_list(page=1, size=1, category=NewsCategory.TECHNOLOGY)
    assert resp.total == 1
    assert len(resp.items) == 1
    assert resp.items[0].id == 'nid'

@pytest.mark.asyncio
async def test_get_news_list_exception(mock_db):
    mock_db.execute.side_effect = Exception("db error")
    service = NewsService(mock_db)
    with pytest.raises(Exception) as e:
        await service.get_news_list()
    assert "获取新闻列表失败" in str(e.value)

@pytest.mark.asyncio
async def test_get_news_detail_success(mock_db):
    service = NewsService(mock_db)
    mock_db.execute.side_effect = [MagicMock(data=[{
        'id': 'nid', 'slug': 'slug', 'title': 'title', 'category': 'technology',
        'view_count': 1, 'created_at': '2024-01-01T00:00:00'
    }]), MagicMock(), MagicMock(data=[])]
    detail = await service.get_news_detail('nid')
    assert detail['id'] == 'nid'
    assert detail['view_count'] == 2

@pytest.mark.asyncio
async def test_get_news_detail_not_found(mock_db):
    service = NewsService(mock_db)
    mock_db.execute.side_effect = [MagicMock(data=[])]
    with pytest.raises(ValueError):
        await service.get_news_detail('notfound') 