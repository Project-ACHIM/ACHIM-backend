from fastapi import FastAPI
from backend.api.auth import mail
from backend.api import users
from backend.db.base import Base
from backend.db.session import engine
from backend.db import models  # モデル定義の読み込み

import logging

logging.basicConfig(level=logging.DEBUG)


app = FastAPI()

app.include_router(mail.router, prefix="/auth/mail", tags=["auth:mail"])
app.include_router(users.router, prefix="/users", tags=["users"])

# ひとまずテーブルを作るための処理
print("テーブル作成開始")
Base.metadata.create_all(bind=engine)
print("テーブル作成完了")
