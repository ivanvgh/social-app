import httpx
from fastapi import Request, Response
from starlette.responses import JSONResponse


async def forward_request(
    service_name: str,
    api_version: str,
    base_url: str,
    path: str,
    request: Request,
) -> Response:
    url = f'{base_url}/{api_version}/{service_name}/{path}'
    method = request.method
    headers = dict(request.headers)
    body = await request.body()

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body
            )
        return Response(content=resp.content, status_code=resp.status_code, headers=resp.headers)
    except httpx.RequestError:
        return JSONResponse(status_code=502, content={'detail': 'Upstream service unavailable'})
