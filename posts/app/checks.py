from __future__ import annotations

import os
from typing import Tuple

from pymongo import MongoClient
from redis import Redis


def ping_mongo(url_env: str = 'MONGO_URL', timeout_ms: int = 1500) -> bool:
    url = os.getenv(url_env)
    if not url:
        return False
    try:
        client = MongoClient(url, serverSelectionTimeoutMS=timeout_ms)
        client.admin.command('ping')
        client.close()
        return True
    except Exception:
        return False


def ping_redis(url_env: str = 'REDIS_URL', timeout: float = 1.5) -> bool:
    url = os.getenv(url_env)
    if not url:
        return False
    try:
        r = Redis.from_url(url, socket_connect_timeout=timeout, socket_timeout=timeout)
        return r.ping()
    except Exception:
        return False


def deps_ok() -> Tuple[bool, bool, bool]:
    m = ping_mongo()
    r = ping_redis()
    return (m and r), m, r
