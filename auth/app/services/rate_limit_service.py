from fastapi import Request, HTTPException, status
import time

from app.core.redis import redis_client



def is_rate_limited(key: str, limit: int, seconds: int) -> bool:
    current_time = int(time.time())

    # Use a Redis sorted set for sliding window
    redis_client.zremrangebyscore(key, 0, current_time - seconds)
    count = redis_client.zcard(key)

    if count >= limit:
        return True

    pipeline = redis_client.pipeline()
    pipeline.zadd(key, {str(current_time): current_time})
    pipeline.expire(key, seconds)
    pipeline.execute()

    return False


def check_rate_limits(
    request: Request,
    *,
    user_identifier: str | None = None,
    ip_limit: int = 5,
    user_limit: int = 10,
    seconds: int = 60,
    key_prefix: str = 'login'
) -> None:
    ip = request.client.host
    ip_key = f'rl:{key_prefix}:ip:{ip}'

    if is_rate_limited(ip_key, limit=ip_limit, seconds=seconds):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail='Too many requests from this IP'
        )

    if user_identifier:
        user_key = f'rl:{key_prefix}:user:{user_identifier}'
        if is_rate_limited(user_key, limit=user_limit, seconds=seconds):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail='Too many requests for this user'
            )
