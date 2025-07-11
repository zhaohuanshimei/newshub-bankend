import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app

client = TestClient(app)

@patch('app.api.api_v1.endpoints.auth.AuthService')
def test_register_success(mock_auth_service):
    mock_instance = mock_auth_service.return_value
    mock_instance.register_user = AsyncMock(return_value=MagicMock(user=MagicMock(username='user123')))
    resp = client.post(
        '/api/v1/auth/register',
        json={'email': 'a@b.com', 'username': 'user123', 'password': 'passwd123'},
        headers={'host': 'testserver'}
    )
    print(resp.status_code, resp.text)
    assert resp.status_code == 200 or resp.status_code == 201
    # 可选：断言 resp.json() 中 username 字段为 'user123'（视接口实现）

@patch('app.api.api_v1.endpoints.auth.AuthService')
def test_register_fail(mock_auth_service):
    mock_instance = mock_auth_service.return_value
    mock_instance.register_user.side_effect = Exception('注册失败')
    resp = client.post('/api/v1/auth/register', json={
        'email': 'a@b.com', 'username': 'u', 'password': 'p'
    })
    assert resp.status_code >= 400 