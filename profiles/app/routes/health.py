from fastapi import APIRouter
from app.checks import ping_postgres

router = APIRouter()

@router.get('/health/live')
def live() -> dict:
    return {'status': 'ok'}

@router.get('/health/ready')
def ready() -> dict:
    ok = ping_postgres()
    return {'status': 'ready' if ok else 'degraded', 'postgres': ok}
