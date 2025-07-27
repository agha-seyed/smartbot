# بخش: ابزارهای کمکی
# فایل: redis_utils.py

import redis
import json
import time
from typing import Any
from studentbot.config import REDIS_URL, logger

class RedisManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisManager, cls).__new__(cls)
            try:
                if REDIS_URL:
                    cls._instance.redis_client = redis.from_url(REDIS_URL, decode_responses=True)
                    cls._instance.redis_client.ping()
                    logger.info("✅ اتصال به Redis با موفقیت برقرار شد.")
                else:
                    logger.warning("⚠️ متغیر محیطی REDIS_URL تعریف نشده است. Redis غیرفعال خواهد بود.")
                    cls._instance.redis_client = None
            except redis.exceptions.ConnectionError as e:
                logger.error(f"❌ خطا در اتصال به Redis: {e}")
                cls._instance.redis_client = None
        return cls._instance

    def get_client(self):
        return self.redis_client

redis_manager = RedisManager()

def set_cache(key: str, value: Any, ttl: int) -> None:
    """
    ذخیره یک مقدار در Redis با استفاده از JSON serialization.

    Args:
        key (str): کلید برای ذخیره‌سازی.
        value (Any): مقداری که باید ذخیره شود.
        ttl (int): زمان انقضا به ثانیه.
    """
    redis_client = redis_manager.get_client()
    if not redis_client:
        return

    start_time = time.time()
    try:
        serialized_value = json.dumps(value)
        redis_client.setex(key, ttl, serialized_value)
        duration = (time.time() - start_time) * 1000
        logger.info(f"Cache SET: key='{key}', success=True, duration={duration:.2f}ms")
    except (TypeError, redis.exceptions.RedisError) as e:
        duration = (time.time() - start_time) * 1000
        logger.error(f"Cache SET: key='{key}', success=False, duration={duration:.2f}ms, error='{e}'")

def get_cache(key: str) -> Any:
    """
    بازیابی یک مقدار از Redis با استفاده از JSON deserialization.

    Args:
        key (str): کلیدی که باید بازیابی شود.

    Returns:
        Any: مقدار بازیابی‌شده یا None در صورت عدم وجود یا خطا.
    """
    redis_client = redis_manager.get_client()
    if not redis_client:
        return None

    start_time = time.time()
    try:
        cached_value = redis_client.get(key)
        duration = (time.time() - start_time) * 1000
        if cached_value:
            deserialized_value = json.loads(cached_value)
            logger.info(f"Cache GET: key='{key}', success=True, found=True, duration={duration:.2f}ms")
            return deserialized_value
        else:
            logger.info(f"Cache GET: key='{key}', success=True, found=False, duration={duration:.2f}ms")
            return None
    except (json.JSONDecodeError, redis.exceptions.RedisError) as e:
        duration = (time.time() - start_time) * 1000
        logger.error(f"Cache GET: key='{key}', success=False, duration={duration:.2f}ms, error='{e}'")
        return None

def delete_cache(key: str) -> None:
    """
    حذف یک کلید از Redis.

    Args:
        key (str): کلیدی که باید حذف شود.
    """
    redis_client = redis_manager.get_client()
    if not redis_client:
        return

    start_time = time.time()
    try:
        deleted_count = redis_client.delete(key)
        duration = (time.time() - start_time) * 1000
        logger.info(f"Cache DELETE: key='{key}', success=True, deleted_count={deleted_count}, duration={duration:.2f}ms")
    except redis.exceptions.RedisError as e:
        duration = (time.time() - start_time) * 1000
        logger.error(f"Cache DELETE: key='{key}', success=False, duration={duration:.2f}ms, error='{e}'")
