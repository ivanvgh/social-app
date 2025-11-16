import logging

from fastapi import HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.core.settings import settings

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def jwt_claims_unless_excluded(excluded: set[str]):
    async def _get_claims(request: Request) -> dict:
        path = request.path_params.get('path')

        if path in excluded:
            logger.info('Skipping JWT validation for path: %s', path)
            return {}

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=401, detail='Missing or invalid token')

        token = auth_header.removeprefix('Bearer ').strip()
        try:
            claims = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            logger.info('Successfully decoded JWT for path: %s, claims: %s', path, claims)
            return claims
        except JWTError as e:
            logger.error('JWT decode failed on path: %s, error: %s', path, str(e))
            raise HTTPException(status_code=401, detail='Invalid or expired token')

    return _get_claims