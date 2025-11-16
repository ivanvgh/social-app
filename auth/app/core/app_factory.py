from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(title='Auth Service')

    app.include_router(health_router, prefix='/health', tags=['Health'])
    app.include_router(auth_router, prefix='/v1/auth', tags=['Auth'])

    return app
