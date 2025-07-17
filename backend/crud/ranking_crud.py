from backend.db.models import User, RankingResult

# rankingデータ挿入
def create_ranking():
    print()

# 引数にあるユーザーと週のランキングを返す
def get_rankings (db, user_id, week_id):

    result = (
        db.query(RankingResult)
        .join(User)
        .filter(RankingResult.week_id == week_id)
        .filter(RankingResult.user_id == user_id)
        .all()
    )

    if result:
        return {
            "user_id": result.user_id,
            "week_id": result.week_id,
            "total_sp": result.total_sp,
            "rank": result.rank
        }
    else:
        return {
            "user_id": user_id,
            "week_id": week_id,
            "message": "ランキングデータが見つかりませんでした"
        }

# ランキングを更新
def update_ranking_result() -> None:
    print()
