# backend/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from core.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
