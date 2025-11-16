from fastapi import Request, Response
from fastapi.responses import JSONResponse
import httpx

# async def forward_request(request: Request, upstream: str) -> Response:
#     body = await request.body()
#     headers = dict(request.headers)
#     headers.pop('host', None)
#
#     async with httpx.AsyncClient(follow_redirects=True) as client:
#         r = await client.request(request.method, f'{upstream}{request.url.path}?{request.url.query}' if request.url.query else f'{upstream}{request.url.path}', headers=headers, content=body)
#
#     resp = Response(content=r.content, status_code=r.status_code, media_type=r.headers.get('content-type'))
#     for k, v in r.headers.items():
#         lk = k.lower()
#         if lk in {'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization', 'te', 'trailers', 'transfer-encoding', 'upgrade', 'content-encoding', 'content-length'}:
#             continue
#         if lk == 'set-cookie':
#             for sc in r.headers.get_list('set-cookie'):
#                 resp.headers.append('set-cookie', sc)
#         else:
#             resp.headers[k] = v
#     return resp

async def forward_request(
    request: Request,
    base_url: str,
) -> Response:
    url = f'{base_url}{request.url.path}'
    method = request.method
    headers = dict(request.headers)
    body = await request.body()

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body,
            )
        return Response(content=resp.content, status_code=resp.status_code, headers=resp.headers)
    except httpx.RequestError:
        return JSONResponse(status_code=502, content={'detail': 'Upstream service unavailable'})
