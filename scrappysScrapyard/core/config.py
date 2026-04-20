from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    auth_api_url: str
    offload_api_url: str
    minio_api_url: str
    minio_root_user: str
    minio_root_password: str
    minio_secure: bool
    internal_api_username: str
    internal_api_password: str


    internal_cookie: str | None = None

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()