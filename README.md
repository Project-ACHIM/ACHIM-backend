# Project-ACHIM
ACHIM制作

# .env ファイルを作成
cp .env.example .env

# 通常起動
docker compose up -d
# 再起動
docker compose restart

make up        # DBとAPIをまとめて起動
make down      # DBとAPIをまとめて停止
make restart   # 再起動
make logs      # backend のログを見る
make psql      # DBに直接入る（確認用）
