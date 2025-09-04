# backend/core/config.py
from pydantic_settings import BaseSettings
from pathlib import Path
import os

class Settings(BaseSettings):
    # --- infra / IO ---
    DATABASE_URL: str
    UPLOAD_DIR: str = "backend/static/uploads"

    BASE_DIR: str = str(Path(__file__).resolve().parent.parent)  

    GROUP_MAX_MEMBERS: int = 5

    # --- app behavior ---
    APP_ENV: str = "production"          # "production" / "development"
    MONDAY_JOIN_ONLY: bool = True        # 本番は True 推奨
    APP_TIMEZONE: str = "Asia/Tokyo"


    ADMIN_API_KEY: str | None = None
    class Config:
        env_file = ".env"                # ここで .env を読む

settings = Settings()

UPLOAD_DIR = Path(settings.UPLOAD_DIR)

os.makedirs(UPLOAD_DIR, exist_ok=True)
