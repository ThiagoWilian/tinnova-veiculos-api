from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    cotacao_ttl_seconds: int = 600
    admin_email: str
    admin_password: str
    user_email: str
    user_password: str

    model_config = SettingsConfigDict( 
        env_file=".env", 
        env_file_encoding="utf-8"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
