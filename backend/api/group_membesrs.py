from http.client import HTTPException
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from backend.db.models import GroupMember
import json

router = APIRouter()

# groupmenberに所属しているuser.idをjsonで返す(自分を除く）
@router.get("/groups/{user_id}/members")
def get_group_menbers(db, user_id):

    # group_idを取得
    group_member = db.query(GroupMember).filter(GroupMember.user_id == user_id).first()
    if not group_member:
        raise HTTPException(status_code=404, detail="User not in any group")

    group_id = group_member.group_id

    # 同じグループの他メンバーのuser.idを取得(自分を除く)
    other_user_ids = (
        db.query(GroupMember.user_id)
        .filter(GroupMember.group_id == group_id)
        .filter(GroupMember.user_id != user_id)
        .all()
    )
    user_ids = [uid for (uid,) in other_user_ids]  # unpack
    user_dict = {uid: uid for uid in user_ids}
    print(user_dict)

    # {"uid":uid, ...}の形で返す
    return JSONResponse(content=user_dict)
    