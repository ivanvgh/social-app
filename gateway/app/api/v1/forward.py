from fastapi import APIRouter, Request, Depends
from app.services.proxy_service import forward_request

from app.core.jwt import jwt_claims_unless_excluded
from app.core.settings import settings

router = APIRouter()

# Only these will skip JWT validation
EXCLUDED_AUTH_PATHS = {
    'login',
    'register',
    'forgot-password',
    'reset-password',
    'verify-email'
}

get_auth_claims = jwt_claims_unless_excluded(EXCLUDED_AUTH_PATHS)


@router.api_route('/{api_version}/auth/{path:path}', methods=['GET', 'POST'])
async def proxy_auth(api_version:str, path: str, request: Request):
    # Evaluate the dependency dynamically
    claims = await get_auth_claims(request)
    request.state.claims = claims
    return await forward_request(request, settings.AUTH_SERVICE_URL)




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
