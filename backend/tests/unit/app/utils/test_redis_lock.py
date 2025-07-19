# backend/tests/unit/app/utils/test_redis_lock.py

import pytest
from unittest.mock import patch, MagicMock
from app.utils.redis_lock import redis_lock, is_locked, RedisLockError
from redis.exceptions import RedisError

@patch("app.utils.redis_lock.get_redis_client")
def test_redis_lock_acquired(mock_get_client):
    mock_redis = MagicMock()
    mock_redis.set.return_value = True
    mock_get_client.return_value = mock_redis

    with redis_lock("test_lock", timeout=10) as (acquired, error):
        assert acquired is True
        assert error is None
    mock_redis.eval.assert_called_once()  # lock released

@patch("app.utils.redis_lock.get_redis_client")
def test_redis_lock_not_acquired(mock_get_client):
    mock_redis = MagicMock()
    mock_redis.set.return_value = False
    mock_get_client.return_value = mock_redis

    with redis_lock("test_lock", timeout=1, max_retries=1) as (acquired, error):
        assert acquired is False
        assert "Failed to acquire lock" in error

@patch("app.utils.redis_lock.get_redis_client", return_value=None)
def test_redis_lock_fallback_no_redis(mock_get_client):
    with redis_lock("test_lock") as (acquired, error):
        assert acquired is True
        assert error is None  # fallback mode


@patch("app.utils.redis_lock.get_redis_client")
def test_redis_lock_raises_on_redis_error(mock_get_client):
    from redis.exceptions import RedisError

    mock_redis = MagicMock()
    mock_redis.set.side_effect = RedisError("redis set failed")
    mock_get_client.return_value = mock_redis

    with pytest.raises(RedisLockError) as exc:
        with redis_lock("test_lock", max_retries=1):
            pass

    assert "Redis error during lock acquisition" in str(exc.value)

@patch("app.utils.redis_lock.get_redis_client")
def test_is_locked_true(mock_get_client):
    mock_redis = MagicMock()
    mock_redis.exists.return_value = 1
    mock_get_client.return_value = mock_redis

    result, error = is_locked("my_lock")
    assert result is True
    assert error is None

@patch("app.utils.redis_lock.get_redis_client")
def test_is_locked_false(mock_get_client):
    mock_redis = MagicMock()
    mock_redis.exists.return_value = 0
    mock_get_client.return_value = mock_redis

    result, error = is_locked("my_lock")
    assert result is False
    assert error is None

@patch("app.utils.redis_lock.get_redis_client", return_value=None)
def test_is_locked_no_redis(mock_get_client):
    result, error = is_locked("whatever")
    assert result is False
    assert "Redis client not available" in error
