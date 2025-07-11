from fastapi import FastAPI
from backend.api.auth import mail
from backend.api import users, sp_routes, bp_routes
from backend.db.base import Base
from backend.db.session import engine
from backend.db import models  # モデル定義の読み込み
from backend.api import auth_google
from backend.db.seed import seed_regions

# from fastapi import FastAPI, Depends
# from sqlalchemy.orm import Session
# from sqlalchemy import text
# from db.session import get_db
# from api import auth_google
# from api.auth import mail
# from api import users

import logging

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

app.include_router(mail.router, prefix="/auth/mail", tags=["auth:mail"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(sp_routes.router)
app.include_router(bp_routes.router)

# ひとまずテーブルを作るための処理
print("テーブル作成開始")
Base.metadata.create_all(bind=engine)
seed_regions()
print("テーブル作成完了")
