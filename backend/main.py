from fastapi import FastAPI
from backend.features.auth import auth_router
from backend.features.exchange import exchange_router
from backend.db.base import Base
from backend.db.session import engine, SessionLocal
from backend.db import models
from backend.features.auth import auth_google
from backend.features.points import bp_router, sp_router
from backend.features.rankings import ranking_router
from backend.features.rankings import history
from backend.features.users import user_router
from backend.features.groups import group_router
from backend.features.dev import dev_router
from backend.features.tasks.monthly_tasks import generate_next_month_weeks
from backend.features.tasks.weekly_tasks import run_weekly_tasks
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from backend.db.set_up import setUp_regions, init_weeks_if_empty
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from backend.core.middleware import ErrorHandlingMiddleware, LoggingMiddleware


# ---- Scheduler ----
weekly_scheduler = BackgroundScheduler()
monthly_scheduler = BackgroundScheduler()
weekly_scheduler.add_job(run_weekly_tasks, 'cron', day_of_week='mon', hour=0, minute=10)
monthly_scheduler.add_job(generate_next_month_weeks, 'cron', day=1, hour=3, minute=0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("DB初期化")
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        setUp_regions(db)
        init_weeks_if_empty(db)

    print("スケジューラ開始")
    weekly_scheduler.start()
    monthly_scheduler.start()

    yield

    print("スケジューラ停止")
    weekly_scheduler.shutdown()
    monthly_scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター
app.include_router(auth_router.router, prefix="/auth/mail", tags=["auth:mail"])
app.include_router(user_router.router, prefix="/users", tags=["users"])
app.include_router(exchange_router.router, prefix="/tickets", tags=["tickets"])
app.include_router(sp_router.router, prefix="/sp", tags=["SP"])
app.include_router(bp_router.router, prefix="/bp", tags=["BP"])
app.include_router(group_router.router, prefix="/groups", tags=["groups"])

app.include_router(history.router, prefix="/history", tags=["history"])
app.include_router(ranking_router.router, prefix="/ranking", tags=["ranking"])

# 管理者用（開発用）ルーター
app.include_router(dev_router.router, prefix="/dev", tags=["dev"])