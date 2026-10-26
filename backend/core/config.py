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
    celery_broker_url: str
    celery_result_backend: str
    rabbitmq_default_user: str
    rabbitmq_default_pass: str

    internal_cookie: str | None = None
    openai_api_key: str | None = None
    openai_api_url: str = "https://api.openai.com"
    openai_default_model: str = "gpt-5.5"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()