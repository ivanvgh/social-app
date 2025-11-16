# app/api/v1/forward.py
from fastapi import APIRouter, Request
from app.services.proxy_service import forward_request
from app.core.jwt import jwt_claims_unless_excluded
from app.core.settings import settings

router = APIRouter()

# Skip JWT validation for endpoints that don't require an access token.
EXCLUDED_AUTH_PATHS = {
    'login',
    'register',
    'forgot-password',
    'reset-password',
    'verify-email',
    'refresh',        # ← important for cookie-based refresh
}

get_auth_claims = jwt_claims_unless_excluded(EXCLUDED_AUTH_PATHS)


@router.api_route('/{api_version}/auth/{path:path}',
                  methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
async def proxy_auth(api_version: str, path: str, request: Request):
    # Validate JWT unless path is excluded (e.g., /auth/refresh)
    claims = await get_auth_claims(request)
    request.state.claims = claims
    upstream_response = await forward_request(request, settings.AUTH_SERVICE_URL)
    return upstream_response
