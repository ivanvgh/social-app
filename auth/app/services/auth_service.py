from datetime import datetime, timedelta
from uuid import UUID, uuid4

from fastapi import HTTPException, status, Request
from sqlalchemy.orm.session import Session

from app.core.settings import settings
from app.models import User
from app.schemas import TokenPair, RegisterRequest, LoginRequest
from app.security import verify_password
from app.services.session_service import create_session
from app.services.token_service import create_access_token, create_refresh_token
from app.services.user_service import get_user_by_email, create_user


def authenticate_user(email: str, password: str, db) -> TokenPair:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')

    return TokenPair(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


def register_user(payload: RegisterRequest, db: Session):
    if db.query(User).filter_by(email=payload.email).first():
        raise HTTPException(status_code=400, detail='Email already registered')
    if db.query(User).filter_by(username=payload.username).first():
        raise HTTPException(status_code=400, detail='Username already taken')

    user = create_user(db, payload)

    return user


def login_user(payload: LoginRequest, request: Request, db: Session) -> TokenPair:
    user = db.query(User).filter_by(email=payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials'
        )

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    create_session(
        db=db,
        user_id=str(user.id),
        refresh_token_hash=refresh_token,
        device_id=get_device_id(request),
        user_agent=request.headers.get('user-agent', '')[:255],
        ip=request.client.host if request.client else '',
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    return TokenPair(access_token=access_token, refresh_token=refresh_token)


def get_device_id(request: Request) -> UUID:
    raw = request.headers.get('X-Device-ID')
    try:
        return UUID(raw)
    except (ValueError, TypeError):
        return uuid4()