import redis
import json
from config import REDIS_URL

r = redis.from_url(REDIS_URL)

def cache_session(user_id: int, data: dict):
    """
    Caches a user's session data in Redis.
    """
    r.set(f"session:{user_id}", json.dumps(data))

def get_session(user_id: int) -> dict:
    """
    Retrieves a user's session data from Redis.
    """
    session_data = r.get(f"session:{user_id}")
    if session_data:
        return json.loads(session_data)
    return {}
