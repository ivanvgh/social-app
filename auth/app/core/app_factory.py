from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(title='Auth Service')

    # CORS config
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],  # change in prod
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    app.include_router(health_router, tags=['Health'])
    app.include_router(auth_router, prefix='/v1/auth', tags=['Auth'])

    return app
