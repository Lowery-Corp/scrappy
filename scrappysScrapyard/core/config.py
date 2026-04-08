from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    auth_api_url: str
    minio_api_url: str
    minio_root_user: str
    minio_root_password: str
    minio_secure: bool

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()