# Makefile - backend から DB + アプリをまとめて制御

up:
	docker compose -f ../achim-db/docker-compose.yml up -d
	docker compose -f docker-compose.yml up -d

down:
	docker compose -f docker-compose.yml down
	docker compose -f ../achim-db/docker-compose.yml down

restart:
	make down
	make up

logs:
	docker compose -f docker-compose.yml logs -f

psql:
	docker exec -it achim_db psql -U postgres -d achim_db

rebuild:  # イメージをキャッシュ無視で再構築（変更反映されないとき）
	docker compose -f docker-compose.yml build --no-cache
	docker compose -f ../achim-db/docker-compose.yml build --no-cache

reload:  # コード変更後にAPI側だけ再起動
	docker compose -f docker-compose.yml restart


.PHONY: clean-pycache

# Pythonキャッシュ削除コマンド
clean-pycache:
	find . -type d -name "__pycache__" -exec rm -r {} + -o -name "*.pyc" -exec rm -f {} +