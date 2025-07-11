import pytest
import pytest_asyncio
from unittest.mock import MagicMock
from app.services.auth.auth_service import AuthService
from app.schemas.requests.auth import RegisterRequest, LoginRequest
from app.schemas.responses.auth import UserResponse

@pytest_asyncio.fixture
def mock_db():
    db = MagicMock()
    db.table.return_value = db
    db.select.return_value = db
    db.eq.return_value = db
    db.insert.return_value = db
    db.execute.return_value = MagicMock(data=[])
    db.auth = MagicMock()
    db.auth.sign_up.return_value = MagicMock(user=MagicMock(id='authid'))
    db.auth.sign_in_with_password.return_value = MagicMock(user=MagicMock(id='authid', email_confirmed_at='2024-01-01T00:00:00'))
    return db

@pytest.mark.asyncio
async def test_register_user_success(mock_db):
    service = AuthService(mock_db)
    req = RegisterRequest(email='a@b.com', username='user123', password='passwd123')
    mock_db.execute.side_effect = [MagicMock(data=[]), MagicMock(data=[]), MagicMock(data=[{'id': 'uid', 'username': 'user123', 'full_name': None, 'avatar_url': None, 'created_at': '2024-01-01T00:00:00', 'preferences': {}}])]
    resp = await service.register_user(req)
    assert resp.user.username == 'user123'

@pytest.mark.asyncio
async def test_register_user_email_exists(mock_db):
    service = AuthService(mock_db)
    req = RegisterRequest(email='a@b.com', username='user123', password='passwd123')
    mock_db.execute.side_effect = [MagicMock(data=[{'id': 'uid'}])]
    with pytest.raises(ValueError):
        await service.register_user(req)

@pytest.mark.asyncio
async def test_login_user_success(mock_db):
    service = AuthService(mock_db)
    req = LoginRequest(email='a@b.com', password='p')
    mock_db.execute.side_effect = [MagicMock(data=[{'id': 'uid', 'username': 'u', 'full_name': None, 'avatar_url': None, 'created_at': '2024-01-01T00:00:00', 'preferences': {}}])]
    resp = await service.login_user(req)
    assert resp.user.username == 'u'

@pytest.mark.asyncio
async def test_login_user_fail(mock_db):
    service = AuthService(mock_db)
    req = LoginRequest(email='a@b.com', password='p')
    mock_db.auth.sign_in_with_password.return_value = MagicMock(user=None)
    with pytest.raises(ValueError):
        await service.login_user(req) 