from backend.db.session import SessionLocal
from backend.db.models.tables.regions import Region

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

def seed_regions():
    db = SessionLocal()
    if db.query(Region).count() == 0:
        for r in regions:
            db.add(Region(id=r["id"], name=r["name"], code=r["code"], area_group=r["area_group"]))
        db.commit()
        print("地域データを登録しました")
    else:
        print("地域データは既に存在します")
    db.close()
