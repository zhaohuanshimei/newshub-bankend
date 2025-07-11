import pytest
from app.models.news import NewsCreate, NewsUpdate, NewsListResponse, NewsCategory, NewsPublic
from datetime import datetime
import pydantic

def test_news_create_missing_required():
    with pytest.raises(pydantic.ValidationError):
        NewsCreate()

def test_news_create_invalid_url():
    with pytest.raises(ValueError):
        NewsCreate(title='t', category=NewsCategory.TECHNOLOGY, source_url='not-a-url')

def test_news_update_empty():
    model = NewsUpdate()
    assert model.title is None
    assert model.tags is None

def test_news_list_response_empty():
    resp = NewsListResponse(items=[], total=0, page=1, size=10, has_next=False)
    assert resp.total == 0
    assert resp.items == []

def test_news_list_response_with_items():
    now = datetime.utcnow()
    item = NewsPublic(id='nid', slug='slug', title='t', category=NewsCategory.TECHNOLOGY, created_at=now)
    resp = NewsListResponse(items=[item], total=1, page=1, size=10, has_next=False)
    assert resp.items[0].id == 'nid' 