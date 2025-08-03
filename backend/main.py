from fastapi import FastAPI
from backend.features.auth import auth_router
from backend.features.exchange import exchange_router
from backend.features.exchange import exchange_router
from backend.db.base import Base
from backend.db.session import engine, SessionLocal
from backend.db import models  # モデル定義の読み込み
from backend.features.auth import auth_google
from backend.features.groups import group_router
from backend.features.points import bp_router, sp_router
from backend.features.rankings import history, ranking_router
from backend.features.users import user_router
from backend.services.monthly_tasks import generate_next_month_weeks
from backend.services.weekly_tasks import run_weekly_tasks
from apscheduler.schedulers.background import BackgroundScheduler
# import logging
from contextlib import asynccontextmanager
from backend.db.set_up import setUp_regions, init_weeks_if_empty
from sqlalchemy.orm import Session

from fastapi.middleware.cors import CORSMiddleware
# logging.basicConfig(level=logging.DEBUG)

# ----自動実行(schedular)の設定---------------
weekly_scheduler = BackgroundScheduler() # インスタンス生成
monthly_scheduler = BackgroundScheduler()

weekly_scheduler.add_job(run_weekly_tasks, 'cron', day_of_week='mon', hour=0, minute=10) # 毎週月曜0:10に実行
monthly_scheduler.add_job(generate_next_month_weeks, 'cron', day=1, hour=3, minute=0) # 毎月1日3:00に実行


# -------------------------------------------

# lifespanハンドラーの定義
@asynccontextmanager
async def lifespan(app: FastAPI):
    # FastAPI アプリの起動・終了時の処理をここに定義。
    # ここでは APScheduler の起動とシャットダウンを行う。

    # 起動時の処理
    print("スケジューラ開始")
    weekly_scheduler.start()
    monthly_scheduler.start()
    
    yield  # アプリが動いている間ここで止まる

    # シャットダウン時の処理
    print("スケジューラ停止")
    weekly_scheduler.shutdown()
    monthly_scheduler.shutdown()
    

# FastAPI アプリに lifespan を登録
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 一旦 "*" にしておいて、後で絞り込むと安全です
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/auth/mail", tags=["auth:mail"])
app.include_router(user_router.router, prefix="/users", tags=["users"])
app.include_router(exchange_router.router, prefix="/tickets",tags=["tickets"])
app.include_router(sp_router.router, prefix="/sp", tags=["SP"])
app.include_router(bp_router.router, prefix="/bp", tags=["BP"])

app.include_router(history.router, prefix="/history", tags=["history"])
app.include_router(ranking_router.router, prefix="/groups", tags=["ranking"])
app.include_router(group_router.router, prefix="/groups", tags=["members"])

# ひとまずテーブルを作るための処理
print("テーブル作成開始")
Base.metadata.create_all(bind=engine)
db = SessionLocal()
setUp_regions(db)
init_weeks_if_empty(db)
db.close()
print("テーブル作成完了")


