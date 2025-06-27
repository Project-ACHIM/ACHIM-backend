from sqlalchemy.orm import Session
from db.models.user import User

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, hashed_password: str):
    user = User(email = email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user