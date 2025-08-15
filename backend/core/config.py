# backend/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # --- infra / IO ---
    DATABASE_URL: str
    UPLOAD_DIR: str = "backend/static/uploads"

    # --- app behavior ---
    APP_ENV: str = "production"          # "production" / "development"
    MONDAY_JOIN_ONLY: bool = True        # 本番は True 推奨
    APP_TIMEZONE: str = "Asia/Tokyo"

    class Config:
        env_file = ".env"                # ここで .env を読む

settings = Settings()
