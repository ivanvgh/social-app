from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = 'Gateway'
    AUTH_SERVICE_URL: str = 'http://auth:8001'
    JWT_SECRET_KEY: str = ''
    JWT_ALGORITHM: str = 'HS256'

    class Config:
        env_file = '.env'

settings = Settings()
