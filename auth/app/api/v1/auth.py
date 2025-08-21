from fastapi import APIRouter, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session

from app import models
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_session
from fastapi import Depends
from passlib.context import CryptContext

from app.schemas import (
    TokenPair, RegisterResponse, RegisterRequest, UserOut, LoginRequest, RefreshRequest
)
from app.services import auth_service, token_service, session_service

router = APIRouter()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.get('/me', response_model=UserOut, tags=['Auth'])
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.post('/register', response_model=RegisterResponse)
def register_user(payload: RegisterRequest, db: Session = Depends(get_session)):
    return auth_service.register_user(payload, db)


@router.post('/login', response_model=TokenPair)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: Session = Depends(get_session)
):
    return auth_service.login_user(form_data, request, db)


@router.post('/refresh', response_model=TokenPair)
def refresh_token(payload: RefreshRequest):
    return token_service.refresh_token(payload)


@router.post('/logout', status_code=204)
def logout_user(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_session)):
    session_service.revoke_session(db, current_user.id)
    return


@router.post('/logout-all', status_code=204)
def logout_all_user_sessions(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_session)):
    session_service.revoke_all_sessions_for_user(db, str(current_user.id))
    return