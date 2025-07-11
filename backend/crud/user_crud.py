from sqlalchemy.orm import Session
from backend.db.models.tables.users import User
from backend.db.models.tables.auth_providers import AuthProvider
from backend.db.models.tables.points import Point

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(AuthProvider).filter(
        AuthProvider.email == email,
        AuthProvider.provider == "email"
    ).first()

def create_user(db: Session, email: str, hashed_password: str):
    user = User(region_id=999)  # 初期は未設定
    db.add(user)
    db.commit()
    db.refresh(user)

    auth_provider = AuthProvider(
        user_id=user.id,
        provider="email",
        provider_user_id=email,
        email=email,
        password_hash=hashed_password
    )
    db.add(auth_provider)

    # BP初期化
    initial_point = Point(user_id=user.id, bp_total=0, bet_bp_pending=0)
    db.add(initial_point)
    
    db.commit()
    db.refresh(auth_provider)

    return user