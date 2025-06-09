from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from db.session import get_db

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, zai"}

@app.get("/test-db")
def test_db_connection(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1")).scalar()
    return {"message": "DB接続成功" if result == 1 else "DB接続失敗"}