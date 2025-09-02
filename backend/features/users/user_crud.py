from sqlalchemy.orm import Session
from backend.db.models.tables.users import User
from backend.db.models.tables.auth_providers import AuthProvider
from backend.db.models.tables.points import Point

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def get_auth_provider_by_email(db: Session, email: str) -> AuthProvider | None:
    normalized_email = email.strip().lower()
    return db.query(AuthProvider).filter(
        AuthProvider.email == normalized_email,
        AuthProvider.provider == "email"
    ).first()

def create_user(db: Session, email: str, hashed_password: str) -> User:
    user = User(
        email=email,
        name=None,
        password=hashed_password,
        region_id=999,
        notification_enabled=True,
        is_profile_completed=False,  # 仮登録状態
    )

    auth_provider = AuthProvider(
        provider="email",
        provider_user_id=email,
        email=email,
        password_hash=hashed_password
    )

    initial_point = Point(bp_total=0, bet_bp_pending=0)

    user.auth_providers.append(auth_provider)
    user.points = initial_point

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def update_user(db: Session, user: User, **kwargs) -> User:
    ALLOWED_FIELDS = {"name", "birth_date", "region_id", "wake_up_time", "notification_enabled"}
    for key, value in kwargs.items():
        if key in ALLOWED_FIELDS and value is not None:
            setattr(user, key, value)

    if user.name and user.birth_date and user.region_id and user.wake_up_time:
        user.is_profile_completed = True

    db.commit()
    db.refresh(user)
    return user

def get_auth_provider(db: Session, user_id: int) -> AuthProvider | None:
    return db.query(AuthProvider).filter(
        AuthProvider.user_id == user_id,
        AuthProvider.provider == "email"
    ).first()