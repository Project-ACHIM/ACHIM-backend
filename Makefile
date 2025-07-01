# 環境変数ファイル
ENV_FILE=db.env

# envから各値を取得
include $(ENV_FILE)
export $(shell sed 's/=.*//' $(ENV_FILE))

# composeファイル
COMPOSE_FILE=docker-compose.yml

# サービス名
DB_SERVICE=db
API_SERVICE=api

# コンテナ名（composeプロジェクト名が 'achim-backend' の場合）
PROJECT_NAME=achim-backend
DB_CONTAINER=$(PROJECT_NAME)-$(DB_SERVICE)-1
API_CONTAINER=$(PROJECT_NAME)-$(API_SERVICE)-1

# --- 起動・停止 ---
up:
	docker compose -f $(COMPOSE_FILE) up -d

down:
	docker compose -f $(COMPOSE_FILE) down

restart:
	make down
	make up

# --- ログ・ステータス ---
logs:
	docker compose -f $(COMPOSE_FILE) logs -f

ps:
	docker compose -f $(COMPOSE_FILE) ps

# --- DB操作 ---
psql:
	docker exec -it $(DB_CONTAINER) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

# --- DBフルリセット ---
reset-db:
	docker compose -f $(COMPOSE_FILE) down -v
	docker compose -f $(COMPOSE_FILE) up -d $(DB_SERVICE)

# --- DB初期データ投入 ---
seed-db:
	docker exec -it $(API_CONTAINER) python backend/db/seed_regions.py

# --- イメージ再構築 ---
rebuild:
	docker compose -f $(COMPOSE_FILE) build --no-cache

# --- APIホットリロード ---
reload:
	docker compose -f $(COMPOSE_FILE) restart $(API_SERVICE)

# --- キャッシュクリア ---
clean-pycache:
	find . -type d -name "__pycache__" -exec rm -r {} + -o -name "*.pyc" -exec rm -f {} +

# --- 完全データ削除 ---
nuke:
	docker compose -f $(COMPOSE_FILE) down -v
