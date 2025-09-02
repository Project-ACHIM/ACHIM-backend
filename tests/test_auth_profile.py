import requests

BASE_URL = "http://localhost:8000"  # APIのURL
EMAIL = "test@example.com"          # テスト用メール
PASSWORD = "password123"            # テスト用パスワード

def login():
    print("=== 1. ログイン ===")
    res = requests.post(f"{BASE_URL}/auth/mail/login", data={
        "username": EMAIL,
        "password": PASSWORD
    })
    print(res.json())
    if res.status_code != 200:
        print("ログイン失敗。サインアップを試みます。")
        signup()
        # サインアップ後は再度ログイン
        res = requests.post(f"{BASE_URL}/auth/mail/login", data={
            "username": EMAIL,
            "password": PASSWORD
        })
        print(res.json())
        if res.status_code != 200:
            raise RuntimeError("ログインに失敗しました")
    token = res.json()["data"]["access_token"]
    return token

def signup():
    print("=== サインアップ ===")
    res = requests.post(f"{BASE_URL}/auth/mail/signup", json={
        "email": EMAIL,
        "password": PASSWORD
    })
    print(res.json())

def get_profile(token):
    print("=== 2. プロフィール取得 ===")
    res = requests.get(f"{BASE_URL}/users/profile", headers={
        "Authorization": f"Bearer {token}"
    })
    print(res.json())

def update_profile(token):
    print("=== 3. プロフィール更新 ===")
    update_data = {
        "name": "新しい名前",
        "birth_date": "2000-01-01",
        "region_id": 1,  # 存在する地域IDを指定
        "wake_up_time": "06:30:00",
        "notification_enabled": True
    }
    res = requests.patch(f"{BASE_URL}/users/profile", json=update_data, headers={
        "Authorization": f"Bearer {token}"
    })
    print(res.json())

if __name__ == "__main__":
    token = login()
    get_profile(token)
    update_profile(token)
    get_profile(token)
