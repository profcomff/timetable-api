run:
	source ./venv/bin/activate && uvicorn --reload --log-level debug calendar_backend.routes.base:app

db:
	docker run -d -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust --name db-timetable_api postgres:15

migrate:
	alembic upgrade head
