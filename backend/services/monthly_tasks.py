from datetime import date, timedelta
from backend.db.session import get_db
from backend.db.models import Week

# 翌月の１ヵ月分のweeksデータを挿入する
def generate_next_month_weeks():
    db = next(get_db())
    today = date.today()

    # 翌月の初日
    if today.month == 12:
        next_month = date(today.year + 1, 1, 1)
    else:
        next_month = date(today.year, today.month + 1, 1)

    # 翌月の最終日を計算
    if next_month.month == 12:
        next_next_month = date(next_month.year + 1, 1, 1)
    else:
        next_next_month = date(next_month.year, next_month.month + 1, 1)
    last_day = next_next_month - timedelta(days=1)

    # 翌月の月曜始まり週を計算
    current = next_month
    while current <= last_day:
        if current.weekday() == 0:  # 月曜
            start = current
            end = start + timedelta(days=6)

            # すでに登録されていないか確認
            exists = db.query(Week).filter(Week.start_date == start).first()
            if not exists:
                week = Week(start_date=start, end_date=end, status='scheduled')
                db.add(week)

        current += timedelta(days=1)

    db.commit()
    db.close()
