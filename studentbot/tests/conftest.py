import pytest
from unittest.mock import MagicMock

@pytest.fixture(scope="function")
def mock_redis_client():
    """
    Pytest fixture to provide a mock Redis client for testing.
    This avoids the need for a live Redis server during tests.
    """
    mock_client = MagicMock()
    # You can configure the mock's behavior here if needed
    # For example: mock_client.get.return_value = '{"key": "value"}'
    return mock_client

@pytest.fixture(autouse=True)
def patch_redis_manager(monkeypatch, mock_redis_client):
    """
    Autouse fixture to patch the redis_manager's get_client method.
    This ensures that any code calling get_client() will receive the
    mock_redis_client instead of a real Redis client.
    """
    from studentbot.utils import redis_utils
    monkeypatch.setattr(redis_utils.redis_manager, 'get_client', lambda: mock_redis_client)
