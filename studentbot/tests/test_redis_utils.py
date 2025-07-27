import unittest
from unittest.mock import patch, MagicMock
import json
from studentbot.utils.redis_utils import set_cache, get_cache, delete_cache, redis_manager

class TestRedisUtils(unittest.TestCase):

    def setUp(self):
        """
        Set up a mock Redis client before each test.
        """
        self.mock_redis_client = MagicMock()
        redis_manager.redis_client = self.mock_redis_client

    def test_set_cache_success(self):
        """
        Test that set_cache successfully calls the redis client's setex method.
        """
        key = "test_key"
        value = {"data": "test_value"}
        ttl = 3600

        set_cache(key, value, ttl)

        serialized_value = json.dumps(value)
        self.mock_redis_client.setex.assert_called_once_with(key, ttl, serialized_value)

    def test_get_cache_found(self):
        """
        Test that get_cache successfully retrieves and deserializes a cached value.
        """
        key = "test_key"
        value = {"data": "test_value"}
        serialized_value = json.dumps(value)

        self.mock_redis_client.get.return_value = serialized_value

        result = get_cache(key)

        self.mock_redis_client.get.assert_called_once_with(key)
        self.assertEqual(result, value)

    def test_get_cache_not_found(self):
        """
        Test that get_cache returns None when a key is not found.
        """
        key = "not_found_key"
        self.mock_redis_client.get.return_value = None

        result = get_cache(key)

        self.mock_redis_client.get.assert_called_once_with(key)
        self.assertIsNone(result)

    def test_delete_cache(self):
        """
        Test that delete_cache successfully calls the redis client's delete method.
        """
        key = "test_key"

        delete_cache(key)

        self.mock_redis_client.delete.assert_called_once_with(key)

    def test_set_cache_redis_error(self):
        """
        Test that set_cache handles Redis errors gracefully.
        """
        key = "test_key"
        value = {"data": "test_value"}
        ttl = 3600

        self.mock_redis_client.setex.side_effect = Exception("Redis connection error")

        # The function should not raise an exception, but log the error.
        # We can't easily test the log output here, but we can ensure it doesn't crash.
        try:
            set_cache(key, value, ttl)
        except Exception as e:
            self.fail(f"set_cache raised an unexpected exception: {e}")

    def test_get_cache_redis_error(self):
        """
        Test that get_cache handles Redis errors gracefully and returns None.
        """
        key = "test_key"
        self.mock_redis_client.get.side_effect = Exception("Redis connection error")

        result = get_cache(key)

        self.assertIsNone(result)

    def test_get_cache_json_decode_error(self):
        """
        Test that get_cache handles JSON decoding errors gracefully and returns None.
        """
        key = "test_key"
        self.mock_redis_client.get.return_value = "invalid json"

        result = get_cache(key)

        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
