from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = ''
    REDIS_URL: str = ''
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_SECRET_KEY: str = ''
    JWT_ALGORITHM: str = 'HS256'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()
