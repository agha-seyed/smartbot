import redis
import json
from config import REDIS_URL, logger

# Initialize Redis connection
try:
    r = redis.from_url(REDIS_URL, decode_responses=True)
except redis.ConnectionError as e:
    logger.error(f"Failed to connect to Redis: {e}")
    raise

def cache_session(user_id: int, data: dict, ttl: int = 86400) -> None:
    """
    Cache a user's session data in Redis with an optional TTL (time-to-live).

    Args:
        user_id (int): The Telegram user ID.
        data (dict): The session data to cache.
        ttl (int): Time-to-live in seconds (default: 24 hours).
    """
    try:
        r.setex(f"session:{user_id}", ttl, json.dumps(data))
        logger.info(f"Session data cached for user {user_id}")
    except redis.RedisError as e:
        logger.error(f"Error caching session for user {user_id}: {e}")
        raise
    except json.JSONEncodeError as e:
        logger.error(f"Invalid JSON data for user {user_id}: {e}")
        raise

def get_session(user_id: int) -> dict:
    """
    Retrieve a user's session data from Redis.

    Args:
        user_id (int): The Telegram user ID.

    Returns:
        dict: The session data if found, else an empty dict.
    """
    try:
        session_data = r.get(f"session:{user_id}")
        if session_data:
            logger.info(f"Session data retrieved for user {user_id}")
            return json.loads(session_data)
        logger.debug(f"No session data found for user {user_id}")
        return {}
    except redis.RedisError as e:
        logger.error(f"Error retrieving session for user {user_id}: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON data retrieved for user {user_id}: {e}")
        return {}
