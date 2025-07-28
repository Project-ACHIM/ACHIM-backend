# backend/core/config.py
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 画像アップロード用ディレクトリ設定
UPLOAD_DIR = os.getenv("UPLOAD_DIR")


