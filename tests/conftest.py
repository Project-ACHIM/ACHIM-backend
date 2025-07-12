# tests/conftest.py
import pytest
from typing import Generator
from sqlalchemy.orm import Session as SQLAlchemySession

from backend.db.session import SessionLocal
from backend.db.base import Base


@pytest.fixture(scope="function")
def db() -> Generator[SQLAlchemySession, None, None]:
    """
    テストごとに新しいデータベースセッションを作成し、
    使用後はロールバックして閉じるfixture。
    """
    db = SessionLocal()

    # テーブル作成（初回のみ or 明示的に毎回作成したい場合）
    Base.metadata.create_all(bind=db.get_bind())

    try:
        yield db
    finally:
        db.rollback()  # セッションを元に戻す
        db.close()
        # 通常DBではdrop_all()は使わない方が安全（SQLiteなどではOK）
        # Base.metadata.drop_all(bind=db.get_bind())
