FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim

ENV APP_NAME=calendar_backend

ENV APP_MODULE=${APP_NAME}.app:app

COPY ./calendar_backend /app
COPY ./requirements.txt /app/
COPY ./alembic.ini /app/alembic.ini
COPY ./migrations /app/migrations
COPY ./templates /app/templates
COPY ./${APP_NAME} /app/${APP_NAME}
RUN pip install -r /app/requirements.txt