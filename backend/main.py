from fastapi import FastAPI
from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware

# Routers
from backend.features.auth import auth_router
from backend.features.exchange import exchange_router
from backend.features.points import bp_router, sp_router
from backend.features.rankings import history, ranking_router
from backend.features.users import user_router
from backend.features.photo_event import photo_router, upload_router
from backend.features.auth import auth_google  # 使っていれば残す

# DB
from backend.db.base import Base
from backend.db.session import engine, SessionLocal
from backend.db import models  # モデル定義の読み込み（副作用でメタ登録）
from backend.db.set_up import setUp_regions, init_weeks_if_empty

# Tasks (ジョブ本体は db を引数に取る想定)
from backend.features.tasks.monthly_tasks import generate_next_month_weeks
from backend.features.tasks.weekly_tasks import run_weekly_tasks

# Scheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

import logging

logger = logging.getLogger(__name__)

# ============================================================
# 変更点1: スケジューラは1つに集約 + タイムゾーン指定
# ============================================================
scheduler = BackgroundScheduler(timezone="Asia/Tokyo")

# ============================================================
# 変更点2: 毎回セッションを開閉するラッパーを用意
# ============================================================
def weekly_job():
    db = SessionLocal()
    try:
        run_weekly_tasks(db)  # ← ここは引数が db のままでOK
    finally:
        db.close()

def monthly_job():
    db = SessionLocal()
    try:
        generate_next_month_weeks(db)  # ← こちらも db を受け取る想定
    finally:
        db.close()

# ============================================================
# lifespan: 起動時にテーブル作成・初期化 → ジョブ登録 → スケジューラ開始
#           終了時にスケジューラ停止
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- DB初期化（テーブル作成 & ベースデータ投入） ---
    print("テーブル作成開始")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        setUp_regions(db)
        init_weeks_if_empty(db)
    finally:
        db.close()
    print("テーブル作成完了")

    # --- ジョブ登録（重複登録を避ける） ---
    if not scheduler.get_jobs():
        # 毎週月曜 00:10
        scheduler.add_job(
            weekly_job,
            trigger=CronTrigger(day_of_week="mon", hour=0, minute=10),
            id="weekly_tasks",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=300,
        )
        # 毎月1日 03:00
        scheduler.add_job(
            monthly_job,
            trigger=CronTrigger(day=1, hour=3, minute=0),
            id="monthly_tasks",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=600,
        )

    print("スケジューラ開始")
    scheduler.start()

    try:
        yield
    finally:
        print("スケジューラ停止")
        # wait=False: シャットダウンを素早く
        scheduler.shutdown(wait=False)

# ============================================================
# FastAPI アプリ本体
# ============================================================
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: 後で必要なオリジンに絞る
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(auth_router.router,    prefix="/auth/mail", tags=["auth:mail"])
app.include_router(user_router.router,    prefix="/users",     tags=["users"])
app.include_router(exchange_router.router, prefix="/tickets",  tags=["tickets"])
app.include_router(sp_router.router,      prefix="/sp",        tags=["SP"])
app.include_router(bp_router.router,      prefix="/bp",        tags=["BP"])
app.include_router(history.router,        prefix="/history",   tags=["history"])
app.include_router(ranking_router.router, prefix="/groups",    tags=["ranking"])

app.include_router(photo_router.router, prefix="/photo",    tags=["photo"])
app.include_router(upload_router.router, prefix="/photo",    tags=["photo"])

from backend.features.groups import group_service
app.include_router(group_service.router,  prefix="/groups",    tags=["members"])


