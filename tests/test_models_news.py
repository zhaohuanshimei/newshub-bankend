import pytest
from app.models.news import (
    NewsCategory, NewsStatus, NewsBase, NewsCreate, NewsUpdate, NewsInDB, NewsPublic, NewsListResponse
)
from datetime import datetime

def test_news_category_enum():
    assert NewsCategory.TECHNOLOGY == "technology"
    assert NewsCategory.BUSINESS == "business"
    assert NewsCategory.SPORTS == "sports"
    assert NewsCategory.ENTERTAINMENT == "entertainment"
    assert NewsCategory.HEALTH == "health"
    assert NewsCategory.SCIENCE == "science"
    assert NewsCategory.POLITICS == "politics"
    assert NewsCategory.WORLD == "world"
    assert NewsCategory.LOCAL == "local"

def test_news_status_enum():
    assert NewsStatus.DRAFT == "draft"
    assert NewsStatus.PUBLISHED == "published"
    assert NewsStatus.ARCHIVED == "archived"

def test_news_base_required_fields():
    model = NewsBase(
        title="Test News",
        category=NewsCategory.TECHNOLOGY
    )
    assert model.title == "Test News"
    assert model.category == NewsCategory.TECHNOLOGY
    assert model.tags == []

def test_news_create_optional_fields():
    model = NewsCreate(
        title="Test News",
        category=NewsCategory.BUSINESS,
        source_url="https://example.com"
    )
    assert str(model.source_url) == "https://example.com/"

def test_news_update_partial():
    model = NewsUpdate(title="Updated", tags=["a", "b"])
    assert model.title == "Updated"
    assert model.tags == ["a", "b"]

def test_news_in_db_all_fields():
    now = datetime.utcnow()
    model = NewsInDB(
        id="uuid",
        slug="slug",
        title="Title",
        category=NewsCategory.HEALTH,
        created_at=now,
        updated_at=now
    )
    assert model.id == "uuid"
    assert model.slug == "slug"
    assert model.status == NewsStatus.PUBLISHED
    assert model.view_count == 0

def test_news_public_fields():
    now = datetime.utcnow()
    model = NewsPublic(
        id="uuid",
        slug="slug",
        title="Title",
        category=NewsCategory.HEALTH,
        created_at=now
    )
    assert model.id == "uuid"
    assert model.slug == "slug"
    assert model.title == "Title"
    assert model.category == NewsCategory.HEALTH
    assert model.created_at == now

def test_news_list_response():
    now = datetime.utcnow()
    item = NewsPublic(
        id="uuid",
        slug="slug",
        title="Title",
        category=NewsCategory.HEALTH,
        created_at=now
    )
    resp = NewsListResponse(items=[item], total=1, page=1, size=10, has_next=False)
    assert resp.total == 1
    assert resp.items[0].id == "uuid"
    assert resp.has_next is False 