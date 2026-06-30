.PHONY: run up down clean migrate health test coverage frontend frontend-install test-database psql install-deps

run:
	docker compose up --build

up:
	docker compose up

down:
	docker compose down

clean:
	docker compose down -v

migrate:
	docker compose exec api alembic upgrade head

health:
	curl http://127.0.0.1:8000/api/v1/health

test:
	pytest -q

coverage:
	pytest --cov=app --cov-report=term-missing

frontend-install:
	cd frontend && npm install

frontend:
	cd frontend && npm run dev

test-database:
	docker compose exec postgres psql -U postgres -c "CREATE DATABASE team_task_manager_test;"

psql:
	docker compose exec postgres psql -U postgres -d team_task_manager

install-deps:
	python -m pip install -e ".[dev]"
