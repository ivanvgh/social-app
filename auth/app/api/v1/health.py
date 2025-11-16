from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import text

from app.api.dependencies.db import get_session

router = APIRouter()

@router.get('/live')
def live() -> dict:
    return {'status': 'ok'}

@router.get('/ready')
def ready(db: Session = Depends(get_session)) -> dict:
    try:
        db.execute(text('select 1'))
        return {'status': 'ready', 'postgres': True}
    except Exception:
        return {'status': 'degraded', 'postgres': False}
    finally:
        try:
            db.rollback()
        except Exception:
            pass


