from fastapi import APIRouter, Request
from app.services.proxy_service import forward_request

from app.core.jwt import verify_jwt
from app.core.settings import settings

router = APIRouter()


@router.api_route('/{api_version}/auth/{path:path}', methods=['GET', 'POST'])
async def proxy_auth(api_version: str, path: str, request: Request):
    return await forward_request('auth',api_version, settings.AUTH_SERVICE_URL, path, request)


# @router.api_route('/profiles/{path:path}', methods=['GET', 'POST', 'PUT', 'DELETE'])
# async def proxy_profiles(path: str, request: Request):
#     user = verify_jwt(request)
#     return await forward_request(request, settings.PROFILES_SERVICE_URL, path)
#
#
# @router.api_route('/posts/{path:path}', methods=['GET', 'POST', 'PUT', 'DELETE'])
# async def proxy_posts(path: str, request: Request):
#     user = verify_jwt(request)
#     return await forward_request(request, settings.POSTS_SERVICE_URL, path)
