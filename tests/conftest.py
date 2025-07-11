# tests/conftest.py
import pytest
from backend.db.session import SessionLocal
from backend.db.base import Base
from sqlalchemy.orm import Session
import backend.db.models

@pytest.fixture(scope="function")
def db() -> Session: # type: ignore
    # """本番と同じDBエンジンを使うfixture（テストごとに初期化）"""
    db = SessionLocal()

    # テーブル作成（必要ならここで）
    Base.metadata.create_all(bind=db.get_bind())

    try:
        yield db
    finally:
        db.rollback()  # テスト後はロールバック
        db.close()
        # 通常のDBを使っている場合、テーブル削除は避けるのが無難
        # SQLiteのような使い捨てなら以下を使ってもOK
        # Base.metadata.drop_all(bind=db.get_bind())
