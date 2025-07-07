from fastapi import FastAPI
from backend.api.auth import mail
from backend.api import users
from backend.db.base import Base
from backend.db.session import engine
from backend.db import models  # モデル定義の読み込み
from backend.api import auth_google
from backend.service.weekly_tasks import run_weekly_tasks
from apscheduler.schedulers.background import BackgroundScheduler
import logging

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

scheduler = BackgroundScheduler()
# 毎週月曜0:10に実行
scheduler.add_job(run_weekly_tasks, 'cron', day_of_week='mon', hour=0, minute=10)
scheduler.start()

app.include_router(mail.router, prefix="/auth/mail", tags=["auth:mail"])
app.include_router(users.router, prefix="/users", tags=["users"])

# ひとまずテーブルを作るための処理
print("テーブル作成開始")
Base.metadata.create_all(bind=engine)
print("テーブル作成完了")
