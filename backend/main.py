from fastapi import FastAPI
from api.auth import mail
from api import users
from api import discount_ticket

app = FastAPI()

app.include_router(mail.router, prefix="/auth/mail", tags=["auth:mail"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(discount_ticket.router, prefix="/tickets",tags=["tickets"])



# ひとまずテーブルを作るための処理
from db.session import engine
from db.models.common import Base  # モデル全体が登録されたBase

print("テーブル作成開始")
Base.metadata.create_all(bind=engine)
print("テーブル作成完了")

