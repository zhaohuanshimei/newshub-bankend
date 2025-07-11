import pytest
from app.models.user import (
    UserBase, UserCreate, UserUpdate, UserInDB, UserPublic
)
from datetime import datetime

def test_user_base_required_fields():
    model = UserBase(email="test@example.com", username="testuser")
    assert model.email == "test@example.com"
    assert model.username == "testuser"
    assert model.full_name is None
    assert model.avatar_url is None

def test_user_create_all_fields():
    model = UserCreate(
        email="test@example.com",
        username="testuser",
        password="123456",
        device_id="dev123",
        push_token="token123"
    )
    assert model.password == "123456"
    assert model.device_id == "dev123"
    assert model.push_token == "token123"

def test_user_update_partial():
    model = UserUpdate(full_name="New Name", preferences={"theme": "dark"})
    assert model.full_name == "New Name"
    assert model.preferences["theme"] == "dark"

def test_user_in_db_all_fields():
    now = datetime.utcnow()
    model = UserInDB(
        id="uuid",
        email="test@example.com",
        username="testuser",
        created_at=now,
        updated_at=now
    )
    assert model.id == "uuid"
    assert model.is_active is True
    assert model.is_verified is False
    assert model.preferences["theme"] == "light"
    assert model.read_count == 0
    assert model.favorite_count == 0

def test_user_public_fields():
    now = datetime.utcnow()
    model = UserPublic(
        id="uuid",
        username="testuser",
        created_at=now
    )
    assert model.id == "uuid"
    assert model.username == "testuser"
    assert model.created_at == now 