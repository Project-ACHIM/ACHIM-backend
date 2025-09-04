# backend/features/groups/group_service.py

from fastapi import HTTPException
from sqlalchemy.orm import Session
import shutil
from pathlib import Path
from datetime import date

from backend.core.config import settings
from backend.features.weeks.week_service import get_week_for_join, require_monday_if_production
from backend.features.groups.group_crud import (
    is_user_joined_in_week,
    join_week_category,
    get_group_member_count,
)
from backend.features.groups.group_schemas import GroupCategory, JoinResponse, StatusResponse
from backend.features.points.point_service import decrease_bp_logic
from backend.db.models.tables.points import Point
from backend.db.models.tables.bp_entries import BpEntry
from backend.db.models.tables.users      import User
from backend.db.models.tables.sp_records import SPRecord
from backend.features.weeks.week_service import get_week_for_join
from backend.core.config import UPLOAD_DIR

# ダミーユーザー設定
DEMO_USERS_INFO = [
    {"user_id": 100, "name": "ともっきーandもも君", "initial_sp": 1000, "initial_bp": 1000},
    {"user_id": 101, "name": "デモ花子",           "initial_sp": 200, "initial_bp": 1000},
    {"user_id": 102, "name": "デモ次郎",           "initial_sp": 500, "initial_bp": 1000},
    {"user_id": 103, "name": "デモ三郎",           "initial_sp": 350, "initial_bp": 1000},
]
DEMO_FILES    = ["demo_godzaiv2.png", "demo_momo2.png", "demo_m.png", "demo_fushimi.png"]
DEMO_SRC_DIR  = Path(settings.BASE_DIR) / "static" / "demo_photos"

# ① ダミーのプロファイル＆ポイントを初回のみ作成する
def ensure_demo_user_profile(db: Session):
    # 1) User を先に登録しコミット
    TOKYO_REGION_ID = 13
    for info in DEMO_USERS_INFO:
        uid = info["user_id"]
        if not db.query(User).filter(User.id == uid).first():
            db.add(User(id=uid, name=info["name"], email=f"demo{uid}@example.com", password="demo", region_id=TOKYO_REGION_ID))
    db.commit()

    # 2) SPRecord を登録・コミット
    current_week = get_week_for_join(db)
    for info in DEMO_USERS_INFO:
        uid = info["user_id"]
        # すでに SPRecord があればスキップ
        if db.query(SPRecord).filter(
            SPRecord.user_id == uid,
            SPRecord.week_id == current_week.id
        ).first():
            continue
        # 必須カラムをすべて埋めて作成
        rec = SPRecord(
            user_id=uid,
            week_id=current_week.id,
            date=date.today(),
            sp=info["initial_sp"],
            mode="demo",             # 'mode'のEnum値に合わせて
        )
        db.add(rec)
    db.commit()
    # 3) Point を登録・コミット
    for info in DEMO_USERS_INFO:
        uid = info["user_id"]
        if not db.query(Point).filter(Point.user_id == uid).first():
            db.add(Point(user_id=uid, bp_total=info["initial_bp"]))
    db.commit()

def ensure_enough_bp(db: Session, user_id: int, bet_bp: int):
    pt = db.query(Point).filter(Point.user_id == user_id).first()
    if not pt or (pt.bp_total or 0) < bet_bp:
        raise HTTPException(status_code=400, detail="BP残高が不足しています")

def create_bet_entry(db: Session, user_id: int, group_id: int, bet_bp: int):
    entry = BpEntry(user_id=user_id, group_id=group_id, bet_bp=bet_bp, result_bp=0)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def join_group(
    db: Session,
    user_id: int,
    category: GroupCategory,
    bet_bp: int,
    *,
    force_new_group: bool = False,
):
    require_monday_if_production()
    week = get_week_for_join(db)

    if is_user_joined_in_week(db, user_id, week.id):
        raise HTTPException(400, "既に今週参加済み")

    ensure_enough_bp(db, user_id, bet_bp)
    decrease_bp_logic(db, user_id=user_id, amount=bet_bp, reason="BET", detail=f"{category.value}参加")

    if force_new_group:
        # 毎回新規グループを作る
        from backend.features.groups.group_crud import _create_group, add_member_to_group
        group = _create_group(db, week_id=week.id, category=category.value)
        add_member_to_group(db, user_id=user_id, group_id=group.id)
    else:
        # 空きグループに入る既存ロジック
        group = join_week_category(db, user_id=user_id, week_id=week.id, category=category.value)

    create_bet_entry(db, user_id=user_id, group_id=group.id, bet_bp=bet_bp)

    pt = db.query(Point).filter(Point.user_id == user_id).first()
    return JoinResponse(
        message="参加が完了しました",
        week_id=week.id,
        group_id=group.id,
        category=category,
        bet_bp=bet_bp,
        bp_balance=pt.bp_total if pt else 0,
    )

def get_join_status(db: Session, user_id: int):
    week = get_week_for_join(db)
    joined = is_user_joined_in_week(db, user_id, week.id)
    return StatusResponse(week_id=week.id, is_joined=joined)

def fill_with_demo(db: Session, group_id: int):
    # 0) ダミープロフィールは初回のみシード
    ensure_demo_user_profile(db)

    from backend.db.models.tables.group_members   import GroupMember
    from backend.db.models.tables.uploaded_photos import UploadedPhoto
    from backend.features.weeks.week_service       import get_week_for_join

    # この週の週開始日を取得（例: Monday の日付）
    week = get_week_for_join(db)
    demo_date = week.start_date  # または week.date, week.begin_at など、ご自分のモデルに合わせて

    # 1) 既存メンバーID と 現在人数取得
    existing = {m.user_id for m in db.query(GroupMember).filter(GroupMember.group_id == group_id)}
    current_count = get_group_member_count(db, group_id)
    slots = settings.GROUP_MAX_MEMBERS - current_count
    if slots <= 0:
        return

    # 2) 空き枠分だけダミー参加＆投稿
    for info, fname in zip(DEMO_USERS_INFO, DEMO_FILES):
        user_id = info["user_id"]
        if user_id in existing:
            continue
        if slots <= 0:
            break

        # グループに追加
        db.add(GroupMember(group_id=group_id, user_id=user_id))

        # ファイルコピー
        src = DEMO_SRC_DIR / fname
        dst = UPLOAD_DIR     / fname
        if not dst.exists():
            shutil.copy(src, dst)

        # 投稿レコード作成：upload_date に demo_date をセット
        db.add(UploadedPhoto(
            group_id   = group_id,
            user_id    = user_id,
            filename   = fname,
            url        = f"/photo/file/{{photo.id}}",
            is_demo    = True,
            upload_date= demo_date
        ))
        slots -= 1

    db.commit()
