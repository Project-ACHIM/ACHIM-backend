from datetime import date, timedelta
from backend.db.models.tables.weeks import Week
from backend.db.session import SessionLocal
from backend.db.models.tables.regions import Region
from sqlalchemy.orm import Session

regions = [
    {"id": 999, "name": "未設定", "code": "999", "area_group": "未分類"},
    {"id": 1, "name": "北海道", "code": "01", "area_group": "北海道地方"},
    {"id": 2, "name": "青森県", "code": "02", "area_group": "東北地方"},
    {"id": 3, "name": "岩手県", "code": "03", "area_group": "東北地方"},
    {"id": 4, "name": "宮城県", "code": "04", "area_group": "東北地方"},
    {"id": 5, "name": "秋田県", "code": "05", "area_group": "東北地方"},
    {"id": 6, "name": "山形県", "code": "06", "area_group": "東北地方"},
    {"id": 7, "name": "福島県", "code": "07", "area_group": "東北地方"},
    {"id": 8, "name": "茨城県", "code": "08", "area_group": "関東地方"},
    {"id": 9, "name": "栃木県", "code": "09", "area_group": "関東地方"},
    {"id": 10, "name": "群馬県", "code": "10", "area_group": "関東地方"},
    {"id": 11, "name": "埼玉県", "code": "11", "area_group": "関東地方"},
    {"id": 12, "name": "千葉県", "code": "12", "area_group": "関東地方"},
    {"id": 13, "name": "東京都", "code": "13", "area_group": "関東地方"},
    {"id": 14, "name": "神奈川県", "code": "14", "area_group": "関東地方"},
    {"id": 15, "name": "新潟県", "code": "15", "area_group": "中部地方"},
    {"id": 16, "name": "富山県", "code": "16", "area_group": "中部地方"},
    {"id": 17, "name": "石川県", "code": "17", "area_group": "中部地方"},
    {"id": 18, "name": "福井県", "code": "18", "area_group": "中部地方"},
    {"id": 19, "name": "山梨県", "code": "19", "area_group": "中部地方"},
    {"id": 20, "name": "長野県", "code": "20", "area_group": "中部地方"},
    {"id": 21, "name": "岐阜県", "code": "21", "area_group": "中部地方"},
    {"id": 22, "name": "静岡県", "code": "22", "area_group": "中部地方"},
    {"id": 23, "name": "愛知県", "code": "23", "area_group": "中部地方"},
    {"id": 24, "name": "三重県", "code": "24", "area_group": "近畿地方"},
    {"id": 25, "name": "滋賀県", "code": "25", "area_group": "近畿地方"},
    {"id": 26, "name": "京都府", "code": "26", "area_group": "近畿地方"},
    {"id": 27, "name": "大阪府", "code": "27", "area_group": "近畿地方"},
    {"id": 28, "name": "兵庫県", "code": "28", "area_group": "近畿地方"},
    {"id": 29, "name": "奈良県", "code": "29", "area_group": "近畿地方"},
    {"id": 30, "name": "和歌山県", "code": "30", "area_group": "近畿地方"},
    {"id": 31, "name": "鳥取県", "code": "31", "area_group": "中国地方"},
    {"id": 32, "name": "島根県", "code": "32", "area_group": "中国地方"},
    {"id": 33, "name": "岡山県", "code": "33", "area_group": "中国地方"},
    {"id": 34, "name": "広島県", "code": "34", "area_group": "中国地方"},
    {"id": 35, "name": "山口県", "code": "35", "area_group": "中国地方"},
    {"id": 36, "name": "徳島県", "code": "36", "area_group": "四国地方"},
    {"id": 37, "name": "香川県", "code": "37", "area_group": "四国地方"},
    {"id": 38, "name": "愛媛県", "code": "38", "area_group": "四国地方"},
    {"id": 39, "name": "高知県", "code": "39", "area_group": "四国地方"},
    {"id": 40, "name": "福岡県", "code": "40", "area_group": "九州地方"},
    {"id": 41, "name": "佐賀県", "code": "41", "area_group": "九州地方"},
    {"id": 42, "name": "長崎県", "code": "42", "area_group": "九州地方"},
    {"id": 43, "name": "熊本県", "code": "43", "area_group": "九州地方"},
    {"id": 44, "name": "大分県", "code": "44", "area_group": "九州地方"},
    {"id": 45, "name": "宮崎県", "code": "45", "area_group": "九州地方"},
    {"id": 46, "name": "鹿児島県", "code": "46", "area_group": "九州地方"},
    {"id": 47, "name": "沖縄県", "code": "47", "area_group": "沖縄地方"},
]
def setUp_regions(db: Session):
    
    if db.query(Region).count() == 0:
        for r in regions:
            db.add(Region(id=r["id"], name=r["name"], code=r["code"], area_group=r["area_group"]))
        db.commit()
        print("地域データを登録しました")
    else:
        print("地域データは既に存在します")

# activeの週を挿入
def insert_active_week(db):
    today = date.today()

    # 今週の active week
    active_start = today - timedelta(days=today.weekday())  # 今週の月曜
    active_end = active_start + timedelta(days=6)

    active_week = Week(
        start_date=active_start,
        end_date=active_end,
        status='active'
    )

    db.add(active_week)
    db.commit()
    print("activeの週を登録しました。")

    return active_week


# 指定月の月曜始まり週を返す(開始日と終了日)
def get_month_weeks(year: int, month: int):
    
    first_day = date(year, month, 1)
    next_month = (month % 12) + 1
    next_month_year = year + (month // 12)
    last_day = date(next_month_year, next_month, 1) - timedelta(days=1)

    current = first_day
    weeks = []

    while current <= last_day:
        if current.weekday() == 0:  # 月曜日
            start = current
            end = start + timedelta(days=6)
            weeks.append((start, end))
        current += timedelta(days=1)

    return weeks

# weeksテーブルが空なら、今月・翌月分のscheduled weekを登録
def init_weeks_if_empty(db):
    
    week_count = db.query(Week).count()
    if week_count > 0:
        return  # すでに存在している場合は何もしない

    today = date.today()

    # 今月と翌月の週を取得
    this_month_weeks = get_month_weeks(today.year, today.month)

    next_month = (today.month % 12) + 1
    next_year = today.year + (today.month // 12)

    next_month_weeks = get_month_weeks(next_year, next_month)

    # データ挿入
    for start, end in this_month_weeks + next_month_weeks:
        week = Week(start_date=start, end_date=end, status='scheduled')
        db.add(week)

    db.commit()

