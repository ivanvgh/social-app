from fastapi import FastAPI
from app.routes.health import router as health_router

def create_app() -> FastAPI:
    app = FastAPI(title='Posts Service')
    app.include_router(health_router)
    return app

app = create_app()
