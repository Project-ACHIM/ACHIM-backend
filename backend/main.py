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

from contextlib import asynccontextmanager

logging.basicConfig(level=logging.DEBUG)

# ----自動実行(schedular)の設定---------------
weekly_scheduler = BackgroundScheduler() # インスタンス生成

weekly_scheduler.add_job(run_weekly_tasks, 'cron', day_of_week='mon', hour=0, minute=10) # 毎週月曜0:10に実行

weekly_scheduler.start() # スケジューラー起動

# -------------------------------------------

# lifespanハンドラーの定義
@asynccontextmanager
async def lifespan(app: FastAPI):
    # FastAPI アプリの起動・終了時の処理をここに定義。
    # ここでは APScheduler の起動とシャットダウンを行う。

    # 起動時の処理
    print("スケジューラ開始")
    weekly_scheduler.start()
    
    yield  # アプリが動いている間ここで止まる

    # シャットダウン時の処理
    print("スケジューラ停止")
    weekly_scheduler.shutdown()
    

# FastAPI アプリに lifespan を登録
app = FastAPI(lifespan=lifespan)

app.include_router(mail.router, prefix="/auth/mail", tags=["auth:mail"])
app.include_router(users.router, prefix="/users", tags=["users"])

# ひとまずテーブルを作るための処理
print("テーブル作成開始")
Base.metadata.create_all(bind=engine)
print("テーブル作成完了")


