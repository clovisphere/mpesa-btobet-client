.PHONY:  build-start-container-dev build-start-container-prod local-dev stop-container


local-dev:
	uvicorn app.main:app --host 127.0.0.1 --port 8088 --log-level debug --env-file .env.dev --reload

build-start-container-dev:
	docker compose up -d --build

build-start-container-prod:
	docker compose -f compose.prod.yml up -d --build

stop-container:
	docker-compose down -v
