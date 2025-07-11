from fastapi import FastAPI
from api.auth import mail
from api import users
from api import discount_ticket
from backend.api.auth import mail
from backend.api import users, sp_routes, bp_routes
from backend.db.base import Base
from backend.db.session import engine
from backend.db import models  # モデル定義の読み込み
from backend.api import auth_google
from backend.service.monthly_tasks import generate_next_month_weeks
from backend.service.weekly_tasks import run_weekly_tasks
from apscheduler.schedulers.background import BackgroundScheduler
# import logging
from contextlib import asynccontextmanager
from backend.db.set_up import setUp_regions


app.include_router(mail.router, prefix="/auth/mail", tags=["auth:mail"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(discount_ticket.router, prefix="/tickets",tags=["tickets"])
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

app.include_router(mail.router, prefix="/auth/mail", tags=["auth:mail"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(sp_routes.router)
app.include_router(bp_routes.router)

# ひとまずテーブルを作るための処理
print("テーブル作成開始")
Base.metadata.create_all(bind=engine)
setUp_regions()
print("テーブル作成完了")


