# backend/db/session.py
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from backend.core.config import settings

for _ in range(10):
    try:
        engine = create_engine(settings.DATABASE_URL, echo=True, future=True)
        conn = engine.connect()
        conn.close()
        print("DB接続成功")
        break
    except OperationalError:
        print("DB接続失敗、再試行中")
        time.sleep(2)
else:
    raise Exception("DBに接続できませんでした")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
