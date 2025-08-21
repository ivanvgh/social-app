from fastapi import APIRouter
from app.routes.checks import deps_ok

router = APIRouter()

@router.get('/health/live')
def live() -> dict:
    return {'status': 'ok'}

@router.get('/health/ready')
def ready() -> dict:
    all_ok, mongo_ok, redis_ok = deps_ok()
    return {
        'status': 'ready' if all_ok else 'degraded',
        'mongo': mongo_ok,
        'redis': redis_ok,
    }
