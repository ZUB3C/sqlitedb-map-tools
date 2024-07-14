.POSIX:

PROJECT_DIR := .

lint:
	@poetry run ruff format --check --diff $(PROJECT_DIR)
	@poetry run ruff check $(PROJECT_DIR)
	@poetry run mypy $(PROJECT_DIR)

format:
	@poetry run ruff format $(PROJECT_DIR)
	@poetry run ruff check --fix $(PROJECT_DIR)

.PHONY: lint, format

migration:
	poetry run alembic revision \
	  --autogenerate \
	  --rev-id $(shell python migrations/_get_next_revision_id.py) \
	  --message "$(message)"

migrate:
	poetry run alembic upgrade head

.PHONY: migration, migrate

app-build:
	docker-compose build

app-run:
	docker-compose stop
	docker-compose up -d --remove-orphans

app-stop:
	docker-compose stop

app-down:
	docker-compose down

app-destroy:
	docker-compose down -v --remove-orphans

app-logs:
	docker-compose logs -f bot

.PHONY: app-build app-run app-stop app-down app-destroy app-logs
