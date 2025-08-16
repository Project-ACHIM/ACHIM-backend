from datetime import date, timedelta
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.db.session import get_db
from backend.db.models.tables.users import User
from backend.db.models.tables.points import Point
from backend.db.models.tables.weeks import Week
from backend.db.models.tables.groups import Group
from backend.db.models.tables.group_members import GroupMember
from backend.db.models.tables.bp_entries import BpEntry

router = APIRouter()

def _require_dev_and_key(x_admin_key: str | None):
    if settings.APP_ENV != "development":
        raise HTTPException(status_code=403, detail="development環境のみ利用可能です")
    if not settings.__dict__.get("ADMIN_API_KEY"):
        raise HTTPException(status_code=403, detail="ADMIN_API_KEY未設定")
    if x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="admin keyが無効です")

@router.post("/bootstrap")
def bootstrap(
    user_id: int = 9999,
    username: str = "super_tester",
    bp_balance: int = 1_000_000,
    db: Session = Depends(get_db),
    x_admin_key: str | None = Header(None)
):
    """今日を含む週/ユーザー/BPを作成して、すぐに参加テストできる状態にする"""
    _require_dev_and_key(x_admin_key)

    # 1) 今日を含むWeekを確保（なければ作成・active化）
    today = date.today()
    wk = (
        db.query(Week)
        .filter(Week.start_date <= today, Week.end_date >= today)
        .first()
    )
    if not wk:
        start = today - timedelta(days=today.weekday())  # 月曜
        end = start + timedelta(days=6)                  # 日曜
        wk = Week(start_date=start, end_date=end, status="active")
        db.add(wk)
        db.flush()
    else:
        # 開発では active に寄せておく
        wk.status = "active"
        db.add(wk)

    # 2) ユーザー確保
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id, username=username)  # あなたのUserモデルの必須項目に合わせて調整
        db.add(user)
        db.flush()

    # 3) BP口座を用意して残高セット
    pt = db.query(Point).filter(Point.user_id == user.id).first()
    if not pt:
        pt = Point(user_id=user.id, bp_total=bp_balance)
        db.add(pt)
    else:
        pt.bp_total = bp_balance
        db.add(pt)

    db.commit()
    return {
        "message": "bootstrap完了",
        "week_id": wk.id,
        "user_id": user.id,
        "bp_balance": pt.bp_total,
    }

@router.post("/topup_bp")
def topup_bp(
    user_id: int,
    amount: int = 100_000,
    db: Session = Depends(get_db),
    x_admin_key: str | None = Header(None)
):
    """任意ユーザーのBPを増やす（開発専用）"""
    _require_dev_and_key(x_admin_key)
    pt = db.query(Point).filter(Point.user_id == user_id).first()
    if not pt:
        pt = Point(user_id=user_id, bp_total=0)
        db.add(pt)
        db.flush()
    pt.bp_total = (pt.bp_total or 0) + amount
    db.commit()
    return {"user_id": user_id, "bp_balance": pt.bp_total}

@router.post("/reset_membership")
def reset_membership(
    user_id: int,
    db: Session = Depends(get_db),
    x_admin_key: str | None = Header(None)
):
    """今週のグループ参加/賭け記録をクリアしてやり直せるようにする（開発専用）"""
    _require_dev_and_key(x_admin_key)

    # 今日を含む週（active化はbootstrap側で済んでいる想定）
    today = date.today()
    wk = (
        db.query(Week)
        .filter(Week.start_date <= today, Week.end_date >= today)
        .first()
    )
    if not wk:
        raise HTTPException(status_code=404, detail="今週のWeekが見つかりません")

    # その週の group_members と bp_entries を削除
    # まずユーザーが入っているグループを取得
    groups = (
        db.query(Group)
        .join(GroupMember, GroupMember.group_id == Group.id)
        .filter(GroupMember.user_id == user_id, Group.week_id == wk.id)
        .all()
    )
    for g in groups:
        # BPエントリ削除
        db.query(BpEntry).filter(BpEntry.user_id == user_id, BpEntry.group_id == g.id).delete()
        # メンバー削除
        db.query(GroupMember).filter(GroupMember.user_id == user_id, GroupMember.group_id == g.id).delete()

    db.commit()
    return {"message": "reset完了", "week_id": wk.id, "user_id": user_id}
