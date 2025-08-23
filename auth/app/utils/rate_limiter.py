from redis.exceptions import RedisError
from app.core.redis import redis_client

def is_rate_limited(key: str, limit: int, seconds: int) -> bool:
    try:
        current = redis_client.incr(key)
        if current == 1:
            redis_client.expire(key, seconds)
        return current > limit
    except RedisError:
        # Fail open if Redis is unavailable
        return False
