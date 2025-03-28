from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "transcoder"
    database_url: str
    redis_url: str
    api_key_header: str = "X-API-Key"
    timestamp_header: str = "X-Timestamp"
    signature_header: str = "X-Signature"
    timestamp_window: int = 300  # 5 minutes in seconds

    class Config:
        env_file = ".env"

settings = Settings()
