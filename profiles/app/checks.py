from __future__ import annotations

import os
import psycopg
from psycopg.rows import tuple_row


def ping_postgres(url_env: str = 'DATABASE_URL', timeout: float = 2.0) -> bool:
    dsn = os.getenv(url_env)
    if not dsn:
        return False
    try:
        with psycopg.connect(dsn, connect_timeout=timeout) as conn:
            with conn.cursor(row_factory=tuple_row) as cur:
                cur.execute('SELECT 1')
                cur.fetchone()
        return True
    except Exception:
        return False
