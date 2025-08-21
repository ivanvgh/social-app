from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str = ''
    DATABASE_URL: str = ''
    REDIS_URL: str = ''
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = 'HS256'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()
